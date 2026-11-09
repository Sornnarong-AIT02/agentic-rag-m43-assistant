import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import ChatRequest, ChatResponse
from app.services.agent import run_agent_loop

app = FastAPI(
    title="M43 Video Assistant API",
    description="Backend API สำหรับผู้ช่วยตั้งค่ากล้องวิดีโอ M43 พร้อมระบบ Agentic RAG และ SSE Streaming"
)

# 🟢 Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    # 🟢 ส่งหน้าเว็บ UI กลับไปเมื่อผู้ใช้เข้าผ่าน http://127.0.0.1:8000/
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "ok", "app": "M43 Video Assistant API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "gemma-4-E4B-it",
                "object": "model",
                "created": 1700000000,
                "owned_by": "m43-assistant"
            }
        ]
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        reply = await asyncio.to_thread(run_agent_loop, user_query=req.message, camera_hint=req.camera_model)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM Upstream Error: {str(e)}")

@app.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    async def sse_generator():
        try:
            reply = await asyncio.to_thread(run_agent_loop, user_query=req.message, camera_hint=req.camera_model)
            
            words = reply.split(" ")
            for word in words:
                data = json.dumps({"token": word + " "}, ensure_ascii=False)
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.03)
                
            yield "data: [DONE]\n\n"
        except Exception as e:
            err_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {err_data}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")