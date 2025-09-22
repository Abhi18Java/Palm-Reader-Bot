from pydantic import BaseModel

class PalmRequest(BaseModel):
    fake: bool = False  # if true, skip camera and use random metrics

class PalmResponse(BaseModel):
    summary: str
    prediction: str
