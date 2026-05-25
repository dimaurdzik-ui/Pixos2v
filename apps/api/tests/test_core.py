import pytest
import uuid
from apps.api.app.db.models.core import User, Workspace, WorkspaceMember, RoleEnum

def test_user_creation():
    user = User(email="test@example.com", name="Test User")
    assert user.email == "test@example.com"
    assert user.name == "Test User"

def test_workspace_creation():
    ws = Workspace(name="Pixos Workspace")
    assert ws.name == "Pixos Workspace"

def test_workspace_member():
    member = WorkspaceMember(
        workspace_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        role=RoleEnum.owner
    )
    assert member.role == RoleEnum.owner
