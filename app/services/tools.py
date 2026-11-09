import json

def calculate_video_settings(args: dict) -> str:
    """Tool คำนวณค่าทางวิดีโอ: Shutter Speed ตามกฎ 180° หรือ Crop Factor (2x) ของ M43"""
    try:
        calc_type = args.get("calc_type")
        if calc_type == "shutter_angle":
            fps = float(args.get("fps", 24))
            angle = float(args.get("shutter_angle", 180))
            shutter_speed = 1.0 / (fps * (360.0 / angle))
            return json.dumps({
                "recommended_shutter_speed": f"1/{round(1.0 / shutter_speed)}",
                "fps": fps,
                "shutter_angle": angle,
                "rule": "180-Degree Shutter Rule"
            }, ensure_ascii=False)
        elif calc_type == "crop_factor":
            focal_length = float(args.get("focal_length_mm", 25))
            return json.dumps({
                "m43_lens_mm": focal_length,
                "full_frame_equivalent_mm": focal_length * 2.0,
                "crop_factor": 2.0
            }, ensure_ascii=False)
        return json.dumps({"error": "Unknown calc_type"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Calculation error: {str(e)}"}, ensure_ascii=False)

def search_m43_docs(args: dict) -> str:
    """Tool ค้นหาคู่มือกล้อง M43 พร้อม Metadata Pre-filtering และ Thai Text Normalization"""
    raw_query = args.get("query", "").lower()
    camera_model = args.get("camera_model")
    
    # Normalization: สร้างสตริงแบบตัดช่องว่างเพื่อรองรับคำภาษาไทยที่เขียนติดกัน
    query_no_space = raw_query.replace(" ", "")
    query_terms = [term for term in raw_query.split() if len(term) > 1]
    
    try:
        with open("data/m43_manuals.json", "r", encoding="utf-8") as f:
            docs = json.load(f)
            
        results = []
        for doc in docs:
            # Metadata Pre-filtering: ยอมรับทั้งรุ่นกล้องที่ระบุ และเอกสารที่เป็น "ALL"
            doc_model = doc.get("camera_model", "").upper()
            if camera_model and doc_model not in [camera_model.upper(), "ALL"]:
                continue
            
            doc_text_lower = doc["text"].lower()
            doc_text_no_space = doc_text_lower.replace(" ", "")
            doc_category_lower = doc["category"].lower()

            # Robust Lexical Match: เช็กทั้งแบบแยกคำ และแบบไม่เว้นวรรคภาษาไทย
            match = (
                any(term in doc_text_lower or term in doc_category_lower for term in query_terms) or
                (len(query_no_space) > 2 and query_no_space in doc_text_no_space) or
                ("หว่อง" in raw_query and "wong" in doc_text_lower)
            )
            
            if match:
                results.append(f"[{doc['source']}] (Model: {doc['camera_model']}) {doc['text']}")
                
        if not results:
            return json.dumps(["ไม่พบข้อมูลที่ตรงกันในคู่มือ M43 ที่รองรับ"], ensure_ascii=False)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"}, ensure_ascii=False)

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calculate_video_settings",
            "description": "คำนวณค่า Shutter Speed จาก Shutter Angle (กฎ 180°) หรือคำนวณระยะเลนส์ Full-Frame Equivalent บนเซนเซอร์ M43",
            "parameters": {
                "type": "object",
                "properties": {
                    "calc_type": {"type": "string", "enum": ["shutter_angle", "crop_factor"]},
                    "fps": {"type": "number", "description": "Frame rate เช่น 24, 30, 60"},
                    "shutter_angle": {"type": "number", "default": 180},
                    "focal_length_mm": {"type": "number", "description": "ระยะเลนส์ M43 (mm)"}
                },
                "required": ["calc_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_m43_docs",
            "description": "ค้นหาคู่มือ การตั้งค่ากล้อง เลนส์ และสไตล์ภาพวิดีโอ (เช่น หว่องกาไว, portrait, depth of field) ของ M43",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "คำค้นหาการตั้งค่ากล้อง สไตล์ภาพ หรือเลนส์"},
                    "camera_model": {"type": "string", "description": "ระบุรุ่นกล้อง เช่น GM1, GH5, OM-1"}
                },
                "required": ["query"]
            }
        }
    }
]