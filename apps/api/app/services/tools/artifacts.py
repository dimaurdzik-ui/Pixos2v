from typing import Any, Dict
import uuid
from apps.api.app.services.tools.base import BaseAdapter
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.outputs import Artifact

class ArtifactsAdapter(BaseAdapter):
    async def execute(self, payload: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        if not context or not context.get("workspace_id"):
            raise ValueError("workspace_id is required in context to save artifacts")
            
        workspace_id = context["workspace_id"]
        workflow_run_id = context.get("workflow_run_id")
        
        name = payload.get("name", "Untitled Artifact")
        content = payload.get("content", "")
        artifact_type = payload.get("artifact_type", "markdown")
        
        async with AsyncSessionLocal() as db:
            artifact = Artifact(
                workspace_id=uuid.UUID(workspace_id),
                workflow_run_id=uuid.UUID(workflow_run_id) if workflow_run_id else None,
                name=name,
                content=content,
                artifact_type=artifact_type
            )
            db.add(artifact)
            await db.commit()
            await db.refresh(artifact)
            
            return {"status": "success", "artifact_id": str(artifact.id), "message": "Artifact saved successfully."}
