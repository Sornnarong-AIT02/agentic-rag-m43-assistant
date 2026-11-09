import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from app.services.tools import TOOLS_SCHEMA, calculate_video_settings, search_m43_docs

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://llm.nat-d.uk/v1")
)

def run_agent_loop(user_query: str, camera_hint: str = None, max_steps: int = 4) -> str:
    """Agentic Loop พร้อม Guardrails จำกัด max_steps และบังคับ temperature=0"""
    system_prompt = (
        "คุณคือผู้เชี่ยวชาญการตั้งค่ากล้องถ่ายวิดีโอระบบ Micro Four Thirds (M43) "
        "คำเตือน: คุณต้องเรียกใช้ Tool `search_m43_docs` เพื่อดึงข้อมูลการตั้งค่า เลนส์ หรือสไตล์วิดีโอจากคลังเอกสารเสมอ "
        "ห้ามตอบคำถามการตั้งค่ากล้องหรือสไตล์วิดีโอจากความรู้ทั่วไปโดยไม่ค้นหาเอกสาร "
        "และต้องใส่อ้างอิงแหล่งที่มา [source] จากเอกสารที่ค้นได้ในคำตอบทุกครั้ง"
    )
    if camera_hint:
        system_prompt += f" (กล้องปัจจุบันของผู้ใช้: {camera_hint})"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    for step in range(max_steps):
        response = client.chat.completions.create(
            model="gemma-4-E4B-it",
            messages=messages,
            tools=TOOLS_SCHEMA,
            temperature=0
        )

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content

        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                
                # ส่ง camera_hint ไปด้วยหากผู้ใช้ไม่ได้ระบุใน arguments
                if fn_name == "search_m43_docs" and camera_hint and not args.get("camera_model"):
                    args["camera_model"] = camera_hint

                if fn_name == "calculate_video_settings":
                    result = calculate_video_settings(args)
                elif fn_name == "search_m43_docs":
                    result = search_m43_docs(args)
                else:
                    result = json.dumps({"error": f"Unknown tool: {fn_name}"}, ensure_ascii=False)
            except Exception as e:
                result = json.dumps({"error": f"Invalid tool arguments: {str(e)}"}, ensure_ascii=False)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    return "ระบบหยุดการทำงานเนื่องจากเกินจำนวนขั้นตอนที่กำหนด (Max Steps Termination Guardrail)"