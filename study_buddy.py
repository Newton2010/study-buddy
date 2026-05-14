import streamlit as st
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

PROMPTS = {
    "summary": """คุณคือติวเตอร์ที่สรุปบทเรียนได้กระชับและชัดเจน
สรุปเนื้อหาเป็น 10 bullet points ภาษาไทย
แต่ละ bullet ต้องสั้น อ่านแล้วเข้าใจทันที""",

    "flashcard": """คุณสร้าง flashcards สำหรับทบทวนบทเรียน
Return Only valid JSON in this exact format, no other text:
{
    "flashcards":[
        {"question": "คำถาม", "answer": "คำตอบ"},
        {"question": "คำถาม", "answer": "คำตอบ"}
    ]
}
สร้าง 5 flashcards จากเนื้อหาที่ให้มา ภาษาไทย""",

    "explain": """คุณอธิบายเนื้อหายากให้เข้าใจง่าย
อธิบายเหมือนกำลังสอนเพื่อนที่ไม่รู้เรื่องนี้มาก่อนเลย
ใช้ภาษาพูดธรรมดา ยกตัวอย่างจากชีวิตจริง
ห้ามใช้ศัพท์เทคนิคโดยไม่อธิบาย"""
}

def ask_claude(content: str, mode: str):
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2000,
        temperature=0.7,
        system=PROMPTS[mode],
        messages=[{"role": "user", "content": content}]
    )
    return message.content[0].text

# ── UI ──────────────────────────────────────
st.title("📚 Study Buddy")
st.caption("ถ่ายรูปสมุด หรือวางข้อความ แล้วให้ AI ช่วยทบทวน")
st.caption("ทดลองใช้ติดต่อ ig: suphasan.sh")


pwd = st.text_input("รหัสผ่าน", type="password")
if pwd != os.getenv("APP_PASSWORD"):
    st.stop() 

image = st.camera_input("ถ่ายรูป") or st.file_uploader("หรืออัปโหลดรูป", type=["jpg","png"])
text = st.text_area("หรือวางข้อความบทเรียน", height=150)
mode = st.radio("เลือก mode", ["flashcard", "summary", "explain"], horizontal=True)

if st.button("สร้างเลย ✨"):
    # เช็คว่ามี input อะไรบ้าง
    if not text and not image:
        st.warning("กรุณาวางบทเรียนหรืออัปโหลดรูปก่อนครับ")
    else:
        with st.spinner("กำลังคิด..."):
            
            if image:
                import base64
                image_data = base64.standard_b64encode(image.read()).decode("utf-8")
                message = client.messages.create(
                    model="claude-haiku-4-5",
                    max_tokens=2000,
                    system=PROMPTS[mode],
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data
                                }
                            },
                            {"type": "text", "text": "สร้างจากรูปนี้"}
                        ]
                    }]
                )
                result = message.content[0].text
            
            # ถ้ามีแค่ข้อความ
            else:
                result = ask_claude(text, mode)

        # แสดงผล
        if mode == "flashcard":
            import json
            try:
                cards = json.loads(result)["flashcards"]
                for i, card in enumerate(cards, 1):
                    with st.expander(f"ข้อ {i}: {card['question']}"):
                        st.write(card["answer"])
            except:
                st.write(result)
        else:
            st.write(result)