from typing import Any, Dict
from apps.api.app.core.config import settings
from .registry import ToolRegistry
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.integrations import IntegrationConnection
from apps.api.app.db.models.policy import ToolPolicy, ToolExecution, PolicyDecision, PendingApproval
from apps.api.app.db.models.workflow import WorkflowRun, WorkflowStep, WorkflowEvent
from apps.api.app.core.security import decrypt_token
from apps.api.app.core.statuses import ApprovalStatus
from sqlalchemy import select
from datetime import datetime, timezone
from langgraph.errors import NodeInterrupt
import uuid

class ToolGateway:
    @staticmethod
    async def execute(tool_name: str, payload: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        context = context or {}
        workspace_id_str = context.get("workspace_id")
        run_id_str = context.get("workflow_run_id")
        agent_id_str = context.get("agent_id")
        step_id_str = context.get("workflow_step_id")
        user_id_str = context.get("user_id")
        tool_call_id = context.get("tool_call_id", str(uuid.uuid4()))

        async with AsyncSessionLocal() as db:
            workspace_id = uuid.UUID(workspace_id_str) if workspace_id_str else None
            run_id = uuid.UUID(run_id_str) if run_id_str else None
            agent_id = uuid.UUID(agent_id_str) if agent_id_str else None
            step_id = uuid.UUID(step_id_str) if step_id_str else None
            user_id = uuid.UUID(user_id_str) if user_id_str else None

            # 0. Idempotency Check
            result_exec = await db.execute(
                select(ToolExecution).where(
                    ToolExecution.workflow_run_id == run_id,
                    ToolExecution.idempotency_key == tool_call_id
                )
            )
            execution = result_exec.scalar_one_or_none()
            
            if not execution:
                # 1. Create ToolExecution record
                execution = ToolExecution(
                    workspace_id=workspace_id,
                    workflow_run_id=run_id,
                    workflow_step_id=step_id,
                    agent_id=agent_id,
                    tool_name=tool_name,
                    risk_level="HIGH",
                    status="pending",
                    payload_preview=payload,
                    idempotency_key=tool_call_id,
                    started_at=datetime.now(timezone.utc)
                )
                db.add(execution)
                await db.commit()
                await db.refresh(execution)
            else:
                # If it exists, check if it's already completed
                if execution.status == "completed":
                    return execution.result_payload
                if execution.status == "failed":
                    return {"error": execution.error_message}

            # 2. Evaluate Policy
            result_policy = await db.execute(
                select(ToolPolicy).where(
                    ToolPolicy.workspace_id == workspace_id,
                    ToolPolicy.tool_name == tool_name
                )
            )
            policy = result_policy.scalar_one_or_none()
            
            risk_level = policy.risk_level if policy else "HIGH"
            approval_required = policy.approval_required if policy else "approval_optional"
            execution.risk_level = risk_level
            
            # Save PolicyDecision
            decision = PolicyDecision(
                workspace_id=workspace_id,
                workflow_run_id=run_id,
                agent_id=agent_id,
                tool_name=tool_name,
                decision="require_approval" if approval_required == "approval_required" else "allow",
                reason=f"Policy specified {approval_required}",
                policy_snapshot={"risk_level": risk_level, "approval_required": approval_required}
            )
            db.add(decision)
            
            # 3. Check connections
            provider = tool_name.split('.')[0] if '.' in tool_name else None
            if not settings.MOCK_TOOLS and provider and provider not in ["web", "artifacts"]:
                result_conn = await db.execute(
                    select(IntegrationConnection).where(
                        IntegrationConnection.workspace_id == workspace_id,
                        IntegrationConnection.provider == provider,
                        IntegrationConnection.status == "connected"
                    )
                )
                connection = result_conn.scalar_one_or_none()
                if not connection:
                    execution.status = "failed"
                    execution.error_message = "CONNECTION_REQUIRED"
                    decision.decision = "connection_required"
                    decision.reason = "Missing provider connection"
                    await db.commit()
                    return {"error": "CONNECTION_REQUIRED"}
                
                if connection.encrypted_token:
                    context["access_token"] = decrypt_token(connection.encrypted_token)

            # 4. Handle Approvals
            if decision.decision == "require_approval":
                # Check if approval was already granted (idempotency/resume)
                result_approval = await db.execute(
                    select(PendingApproval).where(
                        PendingApproval.tool_execution_id == execution.id
                    )
                )
                existing_approval = result_approval.scalar_one_or_none()
                
                if not existing_approval:
                    approval = PendingApproval(
                        workspace_id=workspace_id,
                        workflow_run_id=run_id,
                        tool_call_id=tool_call_id,
                        tool_execution_id=execution.id,
                        agent_id=agent_id,
                        requested_by=user_id,
                        risk_level=risk_level,
                        action_type=tool_name,
                        payload_preview=payload,
                        status=ApprovalStatus.pending
                    )
                    db.add(approval)
                    execution.status = "waiting_approval"
                    execution.approval_id = approval.id
                    
                    if step_id:
                        event = WorkflowEvent(
                            workflow_run_id=run_id,
                            workflow_step_id=step_id,
                            event_type="paused_for_approval",
                            payload={"approval_id": str(approval.id), "tool": tool_name}
                        )
                        db.add(event)
                        
                    await db.commit()
                    
                    # Raise NodeInterrupt to pause LangGraph natively
                    raise NodeInterrupt(f"PAUSED_FOR_APPROVAL:{approval.id}")
                else:
                    if existing_approval.status == ApprovalStatus.pending:
                        raise NodeInterrupt(f"PAUSED_FOR_APPROVAL:{existing_approval.id}")
                    elif existing_approval.status == ApprovalStatus.rejected:
                        execution.status = "rejected"
                        execution.error_message = "Approval rejected"
                        await db.commit()
                        return {"error": "Execution rejected by user."}
                    elif existing_approval.status == ApprovalStatus.executed:
                        return execution.result_payload
                    elif existing_approval.status == ApprovalStatus.failed:
                        execution.status = "failed"
                        execution.error_message = "Approval failed during execution"
                        await db.commit()
                        return {"error": execution.error_message}
                    # If it's executing, that means it was approved and we should run it!
                    elif existing_approval.status == ApprovalStatus.executing:
                        pass # Proceed to execute
            
            # 5. Execute Tool
            adapter = ToolRegistry.get_adapter(tool_name, use_mock=settings.MOCK_TOOLS)
            if not adapter:
                execution.status = "failed"
                execution.error_message = "Tool not found in registry"
                await db.commit()
                return {"error": f"Tool {tool_name} not found."}
                
            execution.status = "running"
            await db.commit()
            
            try:
                result = await adapter.execute(payload, context)
                execution.status = "completed"
                execution.result_payload = result if isinstance(result, dict) else {"result": result}
                execution.completed_at = datetime.now(timezone.utc)
                if decision.decision == "require_approval" and existing_approval:
                    existing_approval.status = ApprovalStatus.executed
                    existing_approval.executed_at = datetime.now(timezone.utc)
                await db.commit()
                return result
            except Exception as e:
                execution.status = "failed"
                execution.error_message = str(e)
                execution.completed_at = datetime.now(timezone.utc)
                await db.commit()
                return {"error": str(e)}
