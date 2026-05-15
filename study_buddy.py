import streamlit as st
import os
from anthropic import Anthropic
from dotenv import load_dotenv
import streamlit.components.v1 as components
import json
import base64

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

def show_about():
    components.html("""
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:sans-serif}
.page{padding:1.5rem;max-width:640px;color:#111}
.badge{display:inline-flex;align-items:center;gap:6px;font-size:12px;padding:4px 12px;border-radius:999px;background:#eff6ff;color:#1d4ed8;margin-bottom:1rem}
.hero{text-align:center;padding:1.5rem 0 2rem}
.hero h1{font-size:26px;font-weight:500;margin-bottom:8px}
.hero p{font-size:14px;color:#6b7280;line-height:1.6;max-width:480px;margin:0 auto 1.5rem}
.btn{display:inline-flex;align-items:center;gap:6px;padding:10px 20px;border:1px solid #e5e7eb;border-radius:8px;font-size:14px;font-weight:500;color:#111;text-decoration:none;background:#fff}
.divider{height:1px;background:#f3f4f6;margin:1.5rem 0}
.label{font-size:11px;color:#9ca3af;letter-spacing:.06em;text-transform:uppercase;margin-bottom:12px}
.features{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:1.5rem}
.feat{background:#fff;border:1px solid #f3f4f6;border-radius:12px;padding:14px}
.feat-icon{font-size:18px;margin-bottom:6px}
.feat-title{font-size:14px;font-weight:500;margin-bottom:3px}
.feat-desc{font-size:12px;color:#6b7280;line-height:1.5}
.steps{display:flex;flex-direction:column;gap:12px;margin-bottom:1.5rem}
.step{display:flex;gap:10px;align-items:flex-start}
.num{width:26px;height:26px;border-radius:50%;background:#f9fafb;border:1px solid #e5e7eb;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:500;color:#6b7280;flex-shrink:0;margin-top:2px}
.step-title{font-size:14px;font-weight:500}
.step-desc{font-size:13px;color:#6b7280;margin-top:2px;line-height:1.5}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:1.5rem}
.stat{background:#f9fafb;border-radius:8px;padding:14px;text-align:center}
.stat-val{font-size:20px;font-weight:500}
.stat-label{font-size:11px;color:#9ca3af;margin-top:2px}
.founder{display:flex;align-items:flex-start;gap:12px;background:#fff;border:1px solid #f3f4f6;border-radius:12px;padding:14px;margin-bottom:1.5rem}
.avatar{width:42px;height:42px;border-radius:50%;background:#eff6ff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:500;color:#1d4ed8;flex-shrink:0}
.founder-name{font-size:15px;font-weight:500}
.founder-role{font-size:12px;color:#9ca3af;margin-top:2px}
.founder-quote{font-size:13px;color:#6b7280;margin-top:8px;line-height:1.5;font-style:italic}
.contact{display:flex;align-items:center;justify-content:space-between;background:#fff;border:1px solid #f3f4f6;border-radius:12px;padding:14px}
.contact-text{font-size:13px;color:#6b7280}
.contact-link{font-size:13px;color:#1d4ed8;text-decoration:none}
</style>
<div class="page">
  <div class="hero">
    <div class="badge">✨ AI-powered study tool</div>
    <h1>Friend Study</h1>
    <p>ผู้ช่วย AI ที่เปลี่ยนบทเรียนยากๆ ให้เข้าใจง่าย — แค่ถ่ายรูปสมุดหรือวางข้อความ แล้ว AI จะทำทุกอย่างให้</p>
  </div>
  <div class="divider"></div>
  <div class="label">สิ่งที่ทำได้</div>
  <div class="features">
    <div class="feat"><div class="feat-icon">🃏</div><div class="feat-title">Flashcards</div><div class="feat-desc">สร้างบัตรคำถาม-คำตอบ พลิกดูคำตอบได้ทันที</div></div>
    <div class="feat"><div class="feat-icon">📝</div><div class="feat-title">สรุปบทเรียน</div><div class="feat-desc">สรุปเนื้อหายาวๆ เป็น bullet points กระชับ</div></div>
    <div class="feat"><div class="feat-icon">💡</div><div class="feat-title">อธิบายให้เข้าใจ</div><div class="feat-desc">อธิบายเหมือนพี่สอนน้อง ใช้ภาษาพูดธรรมดา</div></div>
    <div class="feat"><div class="feat-icon">📷</div><div class="feat-title">ถ่ายรูปสมุด</div><div class="feat-desc">ถ่ายรูปแล้ว AI อ่านและวิเคราะห์ให้เลย</div></div>
  </div>
  <div class="divider"></div>
  <div class="label">วิธีใช้</div>
  <div class="steps">
    <div class="step"><div class="num">1</div><div><div class="step-title">ถ่ายรูปหรือวางข้อความ</div><div class="step-desc">ถ่ายรูปสมุดจด หรือ copy เนื้อหาบทเรียนวางลงมา</div></div></div>
    <div class="step"><div class="num">2</div><div><div class="step-title">เลือก mode</div><div class="step-desc">เลือกว่าอยากได้ flashcard, สรุป, หรืออธิบาย</div></div></div>
    <div class="step"><div class="num">3</div><div><div class="step-title">กด "สร้างเลย"</div><div class="step-desc">AI ประมวลผลและส่งผลลัพธ์กลับในไม่กี่วินาที</div></div></div>
  </div>
  <div class="divider"></div>
  <div class="label">stats</div>
  <div class="stats">
    <div class="stat"><div class="stat-val">3</div><div class="stat-label">learning modes</div></div>
    <div class="stat"><div class="stat-val">AI</div><div class="stat-label">powered by Claude</div></div>
    <div class="stat"><div class="stat-val">24/7</div><div class="stat-label">พร้อมใช้ตลอดเวลา</div></div>
  </div>
  <div class="divider"></div>
  <div class="label">founder</div>
  <div class="founder">
    <div class="avatar">N</div>
    <div>
      <div class="founder-name">Suphasan</div>
      <div class="founder-role">Founder</div>
      <div class="founder-quote">"สร้างเพราะอยากให้ตัวเองและเพื่อนทบทวนบทเรียนได้ง่ายขึ้น — หาอะไรทำครับ"</div>
    </div>
  </div>
  <div class="contact">
    <span class="contact-text">ติดต่อหรือ feedback</span>
    <a class="contact-link" href="https://instagram.com/suphasan.sh" target="_blank">Instagram: suphasan.sh</a>
  </div>
</div>
""", height=1100, scrolling=False)

# ── Navigation ──
page = st.sidebar.radio("", ["เกี่ยวกับเรา", "เรียน",])

# ── About Page ──
if page == "เกี่ยวกับเรา":
    show_about()

# ── Study Page ──
else:
    st.title("📚 Friend Study For Everybody")
    st.caption("ถ่ายรูปสมุด หรือวางข้อความ แล้วให้ AI ช่วยทบทวน")
    st.caption("ทดลองใช้ติดต่อ ig: suphasan.sh")

    pwd = st.text_input("รหัสผ่าน", type="password")
    if pwd != os.getenv("APP_PASSWORD"):
        st.stop()

    image = st.camera_input("ถ่ายรูป") or st.file_uploader("หรืออัปโหลดรูป", type=["jpg","png"])
    text = st.text_area("หรือวางข้อความบทเรียน", height=150)
    mode = st.radio("เลือก mode", ["flashcard", "summary", "explain"], horizontal=True)

    if st.button("สร้างเลย ✨"):
        if not text and not image:
            st.warning("กรุณาวางบทเรียนหรืออัปโหลดรูปก่อนครับ")
        else:
            with st.spinner("กำลังคิด..."):
                if image:
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
                else:
                    result = ask_claude(text, mode)

            if mode == "flashcard":
                try:
                    clean = result.replace("```json", "").replace("```", "").strip()
                    cards = json.loads(clean)["flashcards"]
                    st.markdown(f"### 🃏 Flashcards ({len(cards)} ใบ)")
                    show_flashcards(cards)
                except Exception as e:
                    st.error(f"Parse error: {e}")
                    st.write(result)
            else:
                st.write(result)