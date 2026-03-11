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

    /* 폰트 4종 로드 */
    @font-face { font-family: 'Eulyoo1945'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff'); }
    @font-face { font-family: 'GmarketSans'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff'); }
    @font-face { font-family: 'KyoboHandwriting'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_20-04@1.0/KyoboHandwriting2019.woff') format('woff'); }
    @font-face { font-family: 'DungGeunMo'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/DungGeunMo.woff') format('woff'); }

    /* 폰트 적용 클래스 */
    .f-eulyoo { font-family: 'Eulyoo1945' !important; }
    .f-gmarket { font-family: 'GmarketSans' !important; }
    .f-kyobo { font-family: 'KyoboHandwriting' !important; }
    .f-pixel { font-family: 'DungGeunMo' !important; }

    /* 기본 텍스트 설정 */
    html, body, [class*="st-"] { font-family: 'Eulyoo1945', serif; color: #000000; }

    h1 {
        font-family: 'Trattatello', 'Apple Chancery', cursive !important;
        font-size: 3.8rem !important; color: #000000 !important;
        text-align: center; margin-bottom: 1.5rem !important; padding-top: 1rem !important;
    }

    /* ❗ 입력창 글씨 하얀색 고정 및 버튼 글씨 보호 */
    .stTextArea textarea, .stTextInput input {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        caret-color: #FFFFFF !important;
    }
    
    .instruction-box {
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem; color: #000000;
    }

    .fragment-tag {
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; font-weight: bold; color: #000000;
    }

    /* ❗ 버튼 글씨 색상 강제 지정 */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border-radius: 0px !important; width: 100% !important;
        height: 3.5rem; font-size: 1.2rem !important;
    }
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

st.title("Jerboa Circle: The Oulipo Engine")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏺 Oulipo", "🔪 Dissector", "🔥 Automaton", "⬛ Erasure", "📜 Cadavre Exquis", "🗼 Babel Glitch"
])

# --- TAB 1: Oulipo Engine ---
with tab1:
    st.markdown("""
    <div class="instruction-box">
        <b>[울리포 엔진 가동 지침]</b><br>
        - <b>해부대:</b> 문장을 입력하세요. <b>줄 바꿈</b>과 <b>단어 사이의 여백</b>은 엄격히 보존됩니다.<br>
        - <b>S+N 거리:</b> 명사를 사전에서 찾아 N단계 뒤의 단어로 치환합니다.<br>
        - <b>성역 보호:</b> <b>&lt;단어&gt;</b> 와 같이 꺽쇠로 감싼 부분은 변하지 않는 '성역'이 됩니다.<br>
        - <b>변환 확률:</b> 문장 속 모든 명사를 바꿀지, 일부만 무작위로 치환할지 결정합니다.
    </div>
    """, unsafe_allow_html=True)
    user_input = st.text_area("해부대", placeholder="나는 <심연을> 보았다.", height=150, key="engine_input")
    c1, c2 = st.columns(2); shift_val = c1.slider("S+N 거리", 1, 100, 7); prob_val = c2.slider("변환 확률 (%)", 0, 100, 100)
    
    def transform_with_logic(line, shift, prob):
        parts = re.split(r'(<.*?>)', line)
        d_len = len(NOUN_DICT)
        line_result = []
        for part in parts:
            if part.startswith('<') and part.endswith('>'): line_result.append(part[1:-1])
            else:
                tokens = kiwi.tokenize(part)
                sub_res = []
                for t in tokens:
                    if t.tag.startswith('N') and (hash(t.form) % 100) < prob:
                        if t.form in NOUN_DICT: idx = (NOUN_DICT.index(t.form) + shift) % d_len; new_w = NOUN_DICT[idx]
                        else: new_w = random.choice(NOUN_DICT)
                        sub_res.append((new_w, 'NNG'))
                    else: sub_res.append((t.form, t.tag))
                line_result.append(kiwi.join(sub_res))
        return "".join(line_result)

    if st.button("✨ 문장 재단하기"):
        lines = user_input.split('\n')
        for line in lines:
            st.write(transform_with_logic(line, shift_val, prob_val))

# --- TAB 3: Automaton (불타는 캔버스 로직 완전 복구) ---
with tab3:
    st.markdown("<div class='instruction-box'><b>[자동 기술]</b> 5초간 멈추면 최근 단어들이 타버립니다.</div>", unsafe_allow_html=True)
    automaton_html = """
    <div id="wrapper" style="border:3px solid #000; padding:10px; position:relative; background:#fff;">
        <div id="prog-bg" style="height:5px; background:#ddd;"><div id="prog-bar" style="height:100%; width:100%; background:#000;"></div></div>
        <textarea id="at" style="width:100%; height:300px; border:none; font-size:1.2rem; outline:none; padding:10px;" placeholder="쏟아내세요..."></textarea>
    </div>
    <script>
        const ta = document.getElementById('at');
        const pb = document.getElementById('prog-bar');
        let timer, timeLeft = 5000;
        function burn() {
            let val = ta.value.split(' ');
            if(val.length > 3) ta.value = val.slice(0, -3).join(' ');
            else ta.value = '';
            timeLeft = 5000; pb.style.width = '100%';
        }
        ta.addEventListener('input', () => {
            clearInterval(timer); timeLeft = 5000;
            timer = setInterval(() => {
                timeLeft -= 100; pb.style.width = (timeLeft/5000*100) + '%';
                if(timeLeft <= 0) { clearInterval(timer); burn(); }
            }, 100);
        });
    </script>
    """
    components.html(automaton_html, height=450)

# --- TAB 6: Babel Glitch (폰트 적용 및 실시간) ---
with tab6:
    st.markdown("<div class='instruction-box'><b>[바벨의 균열]</b> 실시간 비틀림을 느껴보세요.</div>", unsafe_allow_html=True)
    b_in = st.text_area("해부할 문장", key="b_in")
    if 'b_raw' not in st.session_state: st.session_state.b_raw = ""
    if st.button("🗼 무너뜨리기"): st.session_state.b_raw = b_in
    
    if st.session_state.b_raw:
        s1, s2 = st.columns(2); tilt = s1.slider("비틀림", 0, 45, 15); size = s2.slider("진동", 0.0, 1.0, 0.3)
        res_html = "<div style='padding:20px; border:3px solid #000; background:#fff;'>"
        fonts = ["f-eulyoo", "f-gmarket", "f-kyobo", "f-pixel"]
        for c in st.session_state.b_raw:
            f = random.choice(fonts) if random.random() > 0.6 else "f-eulyoo"
            deg = random.uniform(-tilt, tilt)
            res_html += f'<span class="{f}" style="display:inline-block; transform:rotate({deg}deg); font-size:{1.2 + random.uniform(-size, size)}rem;">{c}</span>'
        st.markdown(res_html + "</div>", unsafe_allow_html=True)

st.divider()
st.subheader("🏺 사전의 파편들")
samples = random.sample(NOUN_DICT, min(20, len(NOUN_DICT)))
st.write(" / ".join(samples))
