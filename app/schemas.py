# app/schemas.py
from pydantic import BaseModel
from typing import Optional

class PalmResponse(BaseModel):
    summary: str
    prediction: str
    image_path: Optional[str] = None
