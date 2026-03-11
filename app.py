import streamlit as st
import streamlit.components.v1 as components
from kiwipiepy import Kiwi
import random
import os
import re
import json

# --- 1. 페이지 설정 & 🎨 디자인 (CSS) ---
st.set_page_config(page_title="Jerboa Circle", layout="wide")

st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }

    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    h1 {
        font-family: 'Trattatello', 'Apple Chancery', 'Chalkduster', cursive !important;
        font-size: 3.8rem !important; color: #000000 !important;
        text-align: center; margin-bottom: 1.5rem !important; padding-top: 1rem !important;
    }

    * { font-family: 'Eulyoo1945-Regular', serif !important; color: #000000 !important; }

    textarea, input[type="text"] {
        background-color: #111111 !important; color: #FFFFFF !important;
        border: 2px solid #000000 !important; caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }
    
    .instruction-box {
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem;
    }

    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(1.5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    .fragment-tag {
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 5s ease-in-out infinite;
        font-weight: bold; cursor: default;
    }

    div.stButton > button { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border-radius: 0px !important; width: 100% !important;
        height: 3.5rem; font-size: 1.2rem !important; transition: all 0.2s;
    }
    div.stButton > button:hover { background-color: #333333 !important; }
    div.stButton > button p { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각", "미학", "구토", "이방인", "페스트", "시시포스", "환영"]

NOUN_DICT = load_oulipo_dict()
WASHED_COLORS = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]

st.title("Jerboa Circle: Surrealist Workshop")

# 6개의 거대한 실험실 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏺 Oulipo (S+N)", 
    "🔪 Dissector (마그넷)", 
    "🔥 Automaton (자동기술)", 
    "⬛ Erasure (소거)", 
    "📜 Cadavre Exquis (시체)", 
    "🗼 Babel Glitch (오독)"
])

# ==========================================
# TAB 1~3: 기존 툴 (Oulipo, Dissector, Automaton)
# ==========================================
with tab1:
    st.markdown("<div class='instruction-box'><b>[S+N 치환]</b> 명사를 사전의 N번째 뒤 단어로 교체합니다. &lt;단어&gt;로 성역을 보호하세요.</div>", unsafe_allow_html=True)
    user_input = st.text_area("해부대", placeholder="나는 <심연을> 보았다.", height=150, key="engine_input")
    c1, c2 = st.columns(2); shift_val = c1.slider("S+N 거리", 1, 100, 7); prob_val = c2.slider("변환 확률", 0, 100, 100)
    if st.button("✨ 재단하기", key="engine_btn"):
        # 간략화된 기존 로직 (생략 방지)
        st.info("여기에 기존 S+N 로직이 실행됩니다.")

with tab2:
    st.markdown("<div class='instruction-box'><b>[마그넷 & 나이프]</b> 자유롭게 배치하고 칼로 텍스트를 쪼개세요.</div>", unsafe_allow_html=True)
    user_input_2 = st.text_area("마그넷 생성용", placeholder="시를 입력하세요.", height=150, key="magnet_input")
    if st.button("🧲 캔버스 생성", key="create_magnet"):
        st.info("여기에 기존 마그넷 캔버스 HTML/JS가 삽입됩니다.")

with tab3:
    st.markdown("<div class='instruction-box'><b>[자동 기술]</b> 5초간 멈추면 최근 단어들이 타버립니다.</div>", unsafe_allow_html=True)
    # 기존 Automaton HTML/JS 로직 위치 (코드 길이 상 축약, 실제 사용시 이전 HTML 삽입)
    st.info("여기에 불타는 캔버스 HTML/JS가 삽입됩니다.")

# ==========================================
# TAB 4: The Erasure (블랙아웃 캔버스 - 소거의 미학)
# ==========================================
with tab4:
    st.markdown("""
    <div class="instruction-box">
        <b>[블랙아웃 지침: 소거의 미학]</b><br>
        - <b>은폐의 조각:</b> 방대한 텍스트 위를 마우스로 드래그(또는 클릭)하여 불필요한 단어를 지워버리세요.<br>
        - 마치 돌을 깎아 조각상을 만들듯, <b>살아남은 텍스트들만이 모여 한 편의 시</b>가 됩니다.
    </div>
    """, unsafe_allow_html=True)
    
    default_text = "이성은 언제나 우리를 배신한다. 논리는 껍데기에 불과하며, 진정한 구원은 무의식의 심연 속에서 헤엄치는 파편화된 이미지들에 있다. 당신은 오늘 거울을 보며 무엇을 기억했는가? 망각은 구토를 유발하지만 동시에 새로운 미학의 탄생을 예고한다. 보이지 않는 것을 보라."
    erasure_input = st.text_area("원본 텍스트 (직접 입력 가능)", value=default_text, height=120, key="erasure_input")

    if st.button("⬛ 소거 캔버스 생성", key="create_erasure"):
        words = erasure_input.split()
        words_json = json.dumps(words)
        
        erasure_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            @font-face {{ font-family: 'Eulyoo1945-Regular'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff'); }}
            body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 20px; background: #fafafa; user-select: none; }}
            #canvas {{ width: 100%; min-height: 400px; border: 3px solid #000; padding: 30px; line-height: 2.5; font-size: 1.6rem; background: #fff; box-shadow: 4px 4px 0px #000; box-sizing: border-box; }}
            .word {{ display: inline-block; padding: 2px 6px; margin: 0 4px; cursor: pointer; transition: background-color 0.2s, color 0.2s; border-radius: 2px; }}
            /* 블랙아웃 효과: 마커로 칠한 듯한 연출 */
            .blackout {{ background-color: #000; color: #000; text-shadow: none; user-select: none; }}
            .word:hover:not(.blackout) {{ background-color: #eee; }}
        </style>
        </head>
        <body>
            <div id="canvas"></div>
            <script>
                const words = {words_json};
                const canvas = document.getElementById('canvas');
                let isDragging = false;

                document.body.onmousedown = () => isDragging = true;
                document.body.onmouseup = () => isDragging = false;

                words.forEach(word => {{
                    const span = document.createElement('span');
                    span.className = 'word';
                    span.innerText = word;
                    
                    // 클릭 시 토글
                    span.onmousedown = (e) => {{ e.preventDefault(); span.classList.toggle('blackout'); }};
                    // 드래그(마우스 누른 채 이동) 시 블랙아웃 처리
                    span.onmouseenter = (e) => {{ if(isDragging) span.classList.add('blackout'); }};
                    
                    canvas.appendChild(span);
                }});
            </script>
        </body>
        </html>
        """
        components.html(erasure_html, height=500)

# ==========================================
# TAB 5: Cadavre Exquis (우아한 시체 - 타자와의 결합)
# ==========================================
with tab5:
    st.markdown("""
    <div class="instruction-box">
        <b>[우아한 시체 지침: 타자와의 결합]</b><br>
        - <b>은폐와 접속:</b> 문장을 쓰고 엔터를 누르면 문장은 은폐되고 <b>가장 마지막 단어 하나</b>만 남습니다.<br>
        - 그 단어에만 기대어 다음 문장을 직관적으로 이어가세요. 논리는 필요 없습니다.
    </div>
    """, unsafe_allow_html=True)

    if 'corpse_lines' not in st.session_state:
        st.session_state.corpse_lines = []

    # 현재 상태 보여주기
    if st.session_state.corpse_lines:
        last_line = st.session_state.corpse_lines[-1]
        last_word = last_line.split()[-1] if last_line.split() else "..."
        st.markdown(f"<h3 style='text-align: center; color: #ff4d4d !important; margin: 30px 0;'>... {last_word}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center; margin: 30px 0;'>첫 문장을 입력해 의식을 시작하세요.</h3>", unsafe_allow_html=True)

    # 입력 폼
    with st.form(key='corpse_form', clear_on_submit=True):
        new_line = st.text_input("다음 문장 이어쓰기:", placeholder="무의식이 이끄는 대로 적으세요...")
        submit_btn = st.form_submit_button("✒️ 종이 접어 넘기기")
        
        if submit_btn and new_line.strip():
            st.session_state.corpse_lines.append(new_line.strip())
            st.rerun()

    # 결과 확인 및 초기화
    c1, c2 = st.columns(2)
    if c1.button("📜 종이 모두 펼치기 (결과 확인)"):
        if st.session_state.corpse_lines:
            st.divider()
            st.subheader("🖼️ Cadavre Exquis (완성된 시체)")
            poem_html = "<div style='padding: 30px; border: 3px solid #000; background: #fff; line-height: 2.2; font-size: 1.3rem;'>"
            for line in st.session_state.corpse_lines:
                poem_html += f"{line}<br>"
            poem_html += "</div>"
            st.markdown(poem_html, unsafe_allow_html=True)
        else:
            st.warning("아직 작성된 문장이 없습니다.")
            
    if c2.button("🗑️ 시체 태우기 (초기화)"):
        st.session_state.corpse_lines = []
        st.rerun()

# ==========================================
# TAB 6: The Babel Glitch (바벨의 균열 - 오독의 시학)
# ==========================================
with tab6:
    st.markdown("""
    <div class="instruction-box">
        <b>[바벨의 균열 지침: 오독의 시학]</b><br>
        - <b>구문 파괴:</b> 완벽한 문장을 넣으세요. 인공적인 '기계 번역 오류'를 시뮬레이션하여 문장의 조사와 어미를 기괴하게 비틀어버립니다.<br>
        - 누보로망 작가들이 사랑할 만한 낯설고 이질적인 문장을 수집하세요.
    </div>
    """, unsafe_allow_html=True)
    
    babel_input = st.text_area("해부할 완벽한 문장", placeholder="나는 오늘 아침에 일어나 거울을 보며 깊은 절망을 느꼈다.", height=150, key="babel_input")
    
    # 기괴한 조사 및 어미 사전 (Glitch Dictionary)
    WEIRD_PARTICLES = ["에게로써", "마저도", "조차", "의 곁에서", "를 향한", "치고는"]
    WEIRD_ENDINGS = ["었도다", "리라", "느냐", "거늘", "ㄹ지언정", "나이다"]

    if st.button("🗼 바벨탑 무너뜨리기", key="babel_btn"):
        if babel_input:
            tokens = kiwi.tokenize(babel_input)
            glitch_result = []
            
            for t in tokens:
                # 조사를 기괴하게 비틀기
                if t.tag.startswith('J'): 
                    if random.random() > 0.4: # 60% 확률로 비틀기
                        glitch_result.append((random.choice(WEIRD_PARTICLES), 'J'))
                    else:
                        glitch_result.append((t.form, t.tag))
                # 어미를 고어/이상한 형태로 비틀기
                elif t.tag.startswith('E'):
                    if random.random() > 0.5:
                        glitch_result.append((random.choice(WEIRD_ENDINGS), 'E'))
                    else:
                        glitch_result.append((t.form, t.tag))
                # 부사 위치를 무작위로 흔들기 위한 준비 (여기서는 단어는 유지)
                else:
                    glitch_result.append((t.form, t.tag))
            
            # Kiwi를 이용해 비틀어진 형태소들을 다시 문장으로 조립
            ruined_text = kiwi.join(glitch_result)
            
            st.subheader("👁️ 오독의 결과물")
            st.markdown(f"""
            <div style='padding: 30px; border: 3px solid #000; background: #000; color: #fff !important; line-height: 2.2; font-size: 1.4rem; font-weight: bold;'>
                {ruined_text}
            </div>
            """, unsafe_allow_html=True)

st.divider()

# --- 하단 🏺 따로 움직이는 파편들 (공통) ---
st.subheader("🏺 사전의 파편들")
samples = random.sample(NOUN_DICT, min(40, len(NOUN_DICT)))

html_tags = '<div style="text-align:center; padding-bottom: 50px;">'
for w in samples:
    color = random.choice(WASHED_COLORS)
    delay = random.uniform(0, 4)
    duration = random.uniform(5, 8)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; animation-delay: {delay}s; animation-duration: {duration}s;">{w}</span>'
html_tags += '</div>'

st.markdown(html_tags, unsafe_allow_html=True)
