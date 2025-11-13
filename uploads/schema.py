from pydantic import BaseModel

class SignatureResponseSchema(BaseModel):
    cloud_name: str
    api_key: str
    timestamp: int
    signature: str
    folder: str
    resource_type: str