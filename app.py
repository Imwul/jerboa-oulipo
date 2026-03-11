import streamlit as st
from kiwipiepy import Kiwi
import random
import os
import re

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Jerboa Oulipo", layout="wide")

# --- 2. 🎨 디자인: 모바일 최적화 & 칠흑 미학 (CSS) ---
st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }

    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    * { font-family: 'Eulyoo1945-Regular', serif !important; color: #000000 !important; }
    
    /* 📱 모바일 대응 */
    @media (max-width: 768px) {
        .stSlider { padding: 0 5px !important; }
        .fragment-tag { padding: 4px 8px !important; margin: 3px !important; font-size: 0.75rem !important; }
        h1 { font-size: 1.6rem !important; }
        .instruction-box { font-size: 0.85rem !important; }
    }

    /* ❗ 해부대(입력창): 검은 배경 & 하얀 글씨 */
    textarea {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        caret-color: #FFFFFF !important;
        font-size: 1.05rem !important;
    }
    
    /* 안내문 상자 */
    .instruction-box {
        background-color: #F9F9F9;
        padding: 15px;
        border-left: 4px solid #000000;
        margin-bottom: 20px;
        line-height: 1.6;
    }

    /* 🌊 유령의 군무 애니메이션 */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(1.5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    }
    .fragment-tag {
        display: inline-block; padding: 6px 12px; margin: 8px; border-radius: 2px;
        border: 1px solid #000000; animation: float 6s ease-in-out infinite;
        font-weight: bold; font-size: 0.9rem;
    }

    /* 버튼 */
    div.stButton > button { 
        background-color: #000000 !important; 
        color: #FFFFFF !important; 
        border-radius: 0px !important; 
        width: 100% !important;
        height: 3rem;
        font-size: 1.1rem !important;
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
    return ["거울", "파편", "심연", "공백", "기억", "망각", "미학"]

NOUN_DICT = load_oulipo_dict()

# --- 4. 메인 화면 ---
st.title("🐀 저보아 서클 시즌 2: 울리포 엔진(The Oulipo Engine)")

# 📖 안내문(Manifesto) 추가
st.markdown("""
<div class="instruction-box">
    <b>[울리포 엔진 이용 안내]</b><br>
    1. 해부대에 문장을 입력하세요. 줄 바꿈은 그대로 보존됩니다.<br>
    2. 변화를 원치 않는 단어는 <b>&lt;단어&gt;</b> 와 같이 꺽쇠로 감싸 보호하세요. (예: &lt;나&gt;는 오늘 &lt;파리&gt;에 갔다.)<br>
    3. 슬라이더를 통해 활자의 진동과 비틀림을 조절하여 초현실주의적 질감을 완성하세요.
</div>
""", unsafe_allow_html=True)

# 입력 섹션
user_input = st.text_area("해부대에 문장을 올리세요", placeholder="여기에 문장을 넣으세요. <보호할 단어>는 그대로 유지됩니다.", height=200)

col1, col2, col3 = st.columns([1, 1, 1])
with col1: shift_val = st.slider("S+N 거리", 1, 1000, 7)
with col2: bumpy_val = st.slider("진동", 0.0, 0.5, 0.1)
with col3: tilt_val = st.slider("비틀림", 0, 25, 8)

def transform_with_protection(line, shift):
    # 💡 정규표현식으로 <단어> 부분과 일반 텍스트 분리
    parts = re.split(r'(<.*?>)', line)
    d_len = len(NOUN_DICT)
    line_result = []

    for part in parts:
        if part.startswith('<') and part.endswith('>'):
            # 보호된 단어: 꺽쇠만 제거하고 그대로 유지
            protected_word = part[1:-1]
            line_result.append(protected_word)
        else:
            # 일반 텍스트: 형태소 분석 및 변환
            if not part.strip():
                line_result.append(part)
                continue
            tokens = kiwi.tokenize(part)
            sub_res = []
            for t in tokens:
                if t.tag.startswith('N'):
                    if t.form in NOUN_DICT:
                        idx = (NOUN_DICT.index(t.form) + shift) % d_len
                        new_w = NOUN_DICT[idx]
                    else:
                        random.seed(hash(t.form))
                        new_w = NOUN_DICT[random.randint(0, d_len-1)]
                    sub_res.append((new_w, 'NNG'))
                else:
                    sub_res.append((t.form, t.tag))
            line_result.append(kiwi.join(sub_res))
    
    return "".join(line_result)

if st.button("✨ 문장 재단하기"):
    if user_input:
        lines = user_input.split('\n')
        st.subheader("🖼️ 변환 결과")
        
        # 줄바꿈 유지 및 칠흑의 활자 렌더링
        html_res = '<div style="line-height: 2.2; word-wrap: break-word; padding: 20px; border: 3px solid #000000; background-color: #FFFFFF; white-space: pre-wrap;">'
        
        for line in lines:
            if not line.strip():
                html_res += '\n'
                continue
            transformed_line = transform_with_protection(line, shift_val)
            for char in transformed_line:
                if char == ' ':
                    html_res += '&nbsp;'
                else:
                    # 💡 폰트 사이즈 소폭 축소 (1.4rem 베이스)
                    fs = 1.35 + random.uniform(-bumpy_val, bumpy_val)
                    rot = random.uniform(-tilt_val, tilt_val)
                    html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color:#000000 !important;">{char}</span>'
            html_res += '\n'
        
        html_res += '</div>'
        st.markdown(html_res, unsafe_allow_html=True)
        st.session_state.archive = st.session_state.get('archive', []) + [(user_input, "변환 완료")]

st.divider()
st.subheader("🏺 떠다니는 파편들")
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
samples = random.sample(NOUN_DICT, min(25, len(NOUN_DICT)))
html_tags = '<div style="text-align:center;">'
for w in samples:
    html_tags += f'<span class="fragment-tag" style="background-color:{random.choice(washed_colors)};">{w}</span>'
html_tags += '</div>'
st.markdown(html_tags, unsafe_allow_html=True)
