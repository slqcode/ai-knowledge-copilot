from pydantic import BaseModel


class HealthResp(BaseModel):
    status: str = "ok"
    app: str
    env: str


class HelloResp(BaseModel):
    message: str
