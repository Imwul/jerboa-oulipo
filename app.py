import streamlit as st
from kiwipiepy import Kiwi
import random
import os

# --- 1. 페이지 설정 및 칠흑의 미학 ---
st.set_page_config(page_title="Jerboa Oulipo", layout="wide")

st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }
    /* ❗ 글자색을 칠흑 같은 검정으로 고정 */
    * { font-family: 'Eulyoo1945-Regular', serif !important; color: #000000 !important; }
    
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(2deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    .fragment-tag {
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 5s ease-in-out infinite;
        font-weight: bold; cursor: help;
    }
    div.stButton > button { background-color: #000000 !important; color: #FFFFFF !important; border-radius: 0px !important; }
    div.stButton > button p { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

# --- 2. 💡 정제된 사전 로딩 ---
@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각"]

NOUN_DICT = load_oulipo_dict()

# --- 3. 메인 화면 ---
st.title("🐦 저보아: 경량화 마스터 엔진")
st.success(f"✅ {len(NOUN_DICT):,}개의 명사가 로딩되었습니다.")

user_input = st.text_area("해부대에 올릴 문장", placeholder="텍스트를 입력하세요.", height=150)
col1, col2, col3 = st.columns(3)
with col1: shift_val = st.slider("사전 변조 거리 (S+N)", 1, 1000, 7)
with col2: bumpy_val = st.slider("활자의 진동", 0.0, 0.8, 0.2)
with col3: tilt_val = st.slider("활자의 비틀림", 0, 40, 15)

if st.button("✨ 문장 재단하기"):
    if user_input:
        tokens = kiwi.tokenize(user_input)
        result = []
        d_len = len(NOUN_DICT)
        for t in tokens:
            if t.tag.startswith('N'):
                if t.form in NOUN_DICT:
                    idx = (NOUN_DICT.index(t.form) + shift_val) % d_len
                    new_w = NOUN_DICT[idx]
                else:
                    random.seed(hash(t.form))
                    new_w = NOUN_DICT[random.randint(0, d_len-1)]
                result.append((new_w, 'NNG'))
            else: result.append((t.form, t.tag))
        
        transformed = kiwi.join(result)
        st.session_state.archive = st.session_state.get('archive', []) + [(user_input, transformed)]
        
        st.subheader("🖼️ 변환 결과")
        html_res = '<div style="line-height: 2.8; word-wrap: break-word; padding: 30px; border: 3px solid #000000;">'
        for char in transformed:
            fs = 1.8 + random.uniform(-bumpy_val, bumpy_val)
            rot = random.uniform(-tilt_val, tilt_val)
            html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold;">{char}</span>'
        html_res += '</div>'
        st.markdown(html_res, unsafe_allow_html=True)

st.divider()
st.subheader("🏺 떠다니는 파편들")
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
samples = random.sample(NOUN_DICT, min(40, len(NOUN_DICT)))
html_tags = '<div style="text-align:center; padding: 50px 0;">'
for w in samples:
    html_tags += f'<span class="fragment-tag" style="background-color:{random.choice(washed_colors)};">{w}</span>'
html_tags += '</div>'
st.markdown(html_tags, unsafe_allow_html=True)
