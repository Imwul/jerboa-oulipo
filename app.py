import streamlit as st
from kiwipiepy import Kiwi
import random
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Jerboa Oulipo", layout="wide")

# --- 2. 🎨 모바일 최적화 & 시각적 고정 (CSS) ---
st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }

    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    /* 기본 설정: 모든 글자 칠흑색 */
    * { font-family: 'Eulyoo1945-Regular', serif !important; color: #000000 !important; }
    
    /* 📱 모바일 대응: 화면 크기에 따른 폰트 및 패딩 조절 */
    @media (max-width: 768px) {
        .stSlider { padding: 0 10px !important; }
        .fragment-tag { padding: 4px 8px !important; margin: 4px !important; font-size: 0.8rem !important; }
        h1 { font-size: 1.8rem !important; }
    }

    /* ❗ 해부대(입력창): 검은 배경 & 하얀 글씨 */
    textarea {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }
    
    /* 🌊 애니메이션: 파편들 */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(1deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    .fragment-tag {
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 6s ease-in-out infinite;
        font-weight: bold; cursor: help;
    }

    /* 버튼 스타일 */
    div.stButton > button { 
        background-color: #000000 !important; 
        color: #FFFFFF !important; 
        border-radius: 0px !important; 
        width: 100% !important; /* 모바일에서 누르기 편하게 확장 */
    }
    div.stButton > button p { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

# --- 3. 사전 로딩 ---
@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각"]

NOUN_DICT = load_oulipo_dict()

# --- 4. 메인 화면 ---
st.title("🐦 저보아: 모바일 해부 엔진")
st.success(f"✅ {len(NOUN_DICT):,}개의 명사가 탑재되었습니다.")

# 입력 섹션
user_input = st.text_area("해부대에 문장을 올리세요 (줄바꿈이 유지됩니다)", 
                         placeholder="여기에 텍스트를 넣으세요.", height=200)

col1, col2, col3 = st.columns([1, 1, 1])
with col1: shift_val = st.slider("S+N 거리", 1, 1000, 7)
with col2: bumpy_val = st.slider("진동", 0.0, 0.6, 0.15)
with col3: tilt_val = st.slider("비틀림", 0, 30, 10)

def transform_text(input_text, shift):
    # 💡 줄바꿈을 유지하기 위해 라인 단위로 처리
    lines = input_text.split('\n')
    transformed_lines = []
    d_len = len(NOUN_DICT)
    
    for line in lines:
        if not line.strip():
            transformed_lines.append("")
            continue
        tokens = kiwi.tokenize(line)
        result = []
        for t in tokens:
            if t.tag.startswith('N'):
                if t.form in NOUN_DICT:
                    idx = (NOUN_DICT.index(t.form) + shift) % d_len
                    new_w = NOUN_DICT[idx]
                else:
                    random.seed(hash(t.form))
                    new_w = NOUN_DICT[random.randint(0, d_len-1)]
                result.append((new_w, 'NNG'))
            else:
                result.append((t.form, t.tag))
        transformed_lines.append(kiwi.join(result))
    return transformed_lines

if st.button("✨ 문장 재단하기"):
    if user_input:
        transformed_lines = transform_text(user_input, shift_val)
        
        st.subheader("🖼️ 변환 결과")
        # 💡 결과창 폰트 소폭 축소 및 줄바꿈 유지(pre-wrap)
        html_res = '<div style="line-height: 2.2; word-wrap: break-word; padding: 20px; border: 3px solid #000000; background-color: #FFFFFF; white-space: pre-wrap;">'
        for line in transformed_lines:
            for char in line:
                if char == ' ':
                    html_res += '&nbsp;'
                else:
                    fs = 1.4 + random.uniform(-bumpy_val, bumpy_val) # 1.8에서 1.4로 축소
                    rot = random.uniform(-tilt_val, tilt_val)
                    html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color:#000000 !important;">{char}</span>'
            html_res += '\n'
        html_res += '</div>'
        st.markdown(html_res, unsafe_allow_html=True)

st.divider()
st.subheader("🏺 떠다니는 파편들")
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
samples = random.sample(NOUN_DICT, min(30, len(NOUN_DICT)))
html_tags = '<div style="text-align:center;">'
for w in samples:
    html_tags += f'<span class="fragment-tag" style="background-color:{random.choice(washed_colors)};">{w}</span>'
html_tags += '</div>'
st.markdown(html_tags, unsafe_allow_html=True)
