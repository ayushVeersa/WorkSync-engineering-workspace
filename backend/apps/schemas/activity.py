from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict


class ActivityLogCreate(BaseModel):
    actor_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: int
    metadata_json: Optional[str] = None


class ActivityLogResponse(BaseModel):
    id: int
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
