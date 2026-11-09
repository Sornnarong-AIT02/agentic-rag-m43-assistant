from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="คำถามเกี่ยวกับการตั้งค่ากล้อง M43")
    camera_model: str | None = Field(default=None, description="เลือกรุ่นกล้อง M43 เช่น GM1, GH5, OM-1")

class ChatResponse(BaseModel):
    reply: str
    model: str = "gemma-4-E4B-it"