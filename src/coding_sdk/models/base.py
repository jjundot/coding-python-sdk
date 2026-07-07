"""Base model for all API models"""

from pydantic import BaseModel as PydanticBaseModel
from typing import Any, Dict


class BaseModel(PydanticBaseModel):
    """Base model with custom configuration"""

    class Config:
        # Allow extra fields from API responses
        extra = "allow"
        # Use population by field name
        populate_by_name = True
        # Convert snake_case to camelCase automatically
        alias_generator = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.model_dump(exclude_none=True)

    def to_json(self) -> str:
        """Convert model to JSON string"""
        return self.model_dump_json(exclude_none=True)
