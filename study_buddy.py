import streamlit as st
import os
from anthropic import Anthropic
from dotenv import load_dotenv
import streamlit.components.v1 as components
import json

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
ช
def show_flashcards(cards):
    cards_json = json.dumps(cards, ensure_ascii=False)
    html = f"""
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 8px; }}
  .scene {{ height: 140px; perspective: 600px; cursor: pointer; }}
  .card {{ width: 100%; height: 100%; position: relative; transform-style: preserve-3d; transition: transform 0.5s ease; border-radius: 12px; }}
  .scene.flipped .card {{ transform: rotateY(180deg); }}
  .front, .back {{
    position: absolute; inset: 0;
    backface-visibility: hidden;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    padding: 16px; text-align: center;
    border: 1px solid #e5e7eb;
  }}
  .front {{ background: #f9fafb; }}
  .back {{ background: #eff6ff; transform: rotateY(180deg); }}
  .num {{ font-size: 11px; color: #9ca3af; margin-bottom: 6px; }}
  .q {{ font-size: 14px; font-weight: 500; color: #111827; line-height: 1.4; }}
  .a {{ font-size: 13px; color: #1d4ed8; line-height: 1.5; }}
  .hint {{ font-size: 11px; color: #9ca3af; margin-top: 8px; }}
  .progress {{ text-align: center; padding: 8px; font-size: 13px; color: #6b7280; margin-bottom: 8px; }}
</style>

<div class="progress" id="prog">กดที่การ์ดเพื่อดูคำตอบ</div>
<div class="grid" id="grid"></div>

<script>
const cards = {cards_json};
let flipped = 0;
const grid = document.getElementById('grid');

cards.forEach((card, i) => {{
  const scene = document.createElement('div');
  scene.className = 'scene';
  scene.innerHTML = `
    <div class="card">
      <div class="front">
        <div>
          <div class="num">ข้อ ${{i+1}}</div>
          <div class="q">${{card.question}}</div>
          <div class="hint">👆 กดเพื่อดูคำตอบ</div>
        </div>
      </div>
      <div class="back">
        <div class="a">${{card.answer}}</div>
      </div>
    </div>`;
  
  scene.onclick = () => {{
    const wasFlipped = scene.classList.contains('flipped');
    scene.classList.toggle('flipped');
    flipped += wasFlipped ? -1 : 1;
    document.getElementById('prog').textContent = 
      flipped === 0 ? 'กดที่การ์ดเพื่อดูคำตอบ' :
      `เปิดดูแล้ว ${{flipped}}/${{cards.length}} ใบ`;
  }};
  
  grid.appendChild(scene);
}});
</script>
"""
    components.html(html, height=len(cards) * 90 + 60, scrolling=False)

# ── UI ──────────────────────────────────────
st.title("📚 Friend Study")
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
            try:
               cards = json.loads(result)["flashcards"]
               st.markdown(f"### 🃏 Flashcards ({len(cards)} ใบ)")
               show_flashcards(cards)
            except:
                 st.write(result)
        else:
            st.write(result)