from datetime import datetime

from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: int
    original_name: str
    stored_name: str
    file_path: str
    content_type: str
    file_size: int
    issue_id: int
    uploaded_by: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }