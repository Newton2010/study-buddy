import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

PROMPTS = {
    "summary": """คุณคือติวเตอร์ที่สรุปบทเรียนได้กระชับและชัดเจน
สรุปเนื้อหาเป็น 5 bullet points ภาษาไทย
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

content = st.text_area("วางบทเรียนของคุณ", height=200)
mode = st.selectbox("เลือก mode", list(PROMPTS.keys()))

if st.button("ส่ง"):
    if not content.strip():
        st.warning("กรุณาวางบทเรียนก่อน")
    else:
        with st.spinner("กำลังคิด..."):
            result = ask_claude(content, mode)
        st.write(result)