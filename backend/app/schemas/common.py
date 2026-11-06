from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    correlation_id: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
