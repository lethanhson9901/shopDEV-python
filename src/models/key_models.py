from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BaseKeyModel(BaseModel):
    user_id: str = Field(description="The unique identifier of the user.")
    public_key: Optional[str] = Field(default=None, description="The public key associated with the user.")
    private_key: Optional[str] = Field(default=None, description="The private key associated with the user.")
    refresh_token: str = Field(..., description="The current refresh token issued to the user.")
    refresh_tokens_used: List[str] = Field(default=[], description="A list of all refresh tokens that have been issued to the user.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the key information was created.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the last update to the key information.")
