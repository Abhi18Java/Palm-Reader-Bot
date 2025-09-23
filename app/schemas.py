from pydantic import BaseModel

class PalmRequest(BaseModel):
    pass

class PalmResponse(BaseModel):
    summary: str
    prediction: str
    image_path: str = None
    image_path: str = None
