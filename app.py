import streamlit as st
from kiwipiepy import Kiwi
import random
import os
import re

# --- 1. 페이지 설정 및 폰트 ---
st.set_page_config(page_title="Jerboa Oulipo", layout="wide")

# --- 2. 🎨 디자인: 칠흑의 활자 & 독립적 애니메이션 (CSS) ---
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
        .fragment-tag { padding: 4px 8px !important; margin: 4px !important; font-size: 0.8rem !important; }
        h1 { font-size: 1.6rem !important; }
    }

    /* ❗ 해부대(입력창): 검은 배경 & 하얀 글씨 */
    textarea {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }
    
    .instruction-box {
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem;
    }

    /* 🌊 유령의 군무 애니메이션 */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(1.5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    .fragment-tag {
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 5s ease-in-out infinite;
        font-weight: bold; cursor: crosshair;
    }

    /* 버튼 스타일 */
    div.stButton > button { 
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

# --- 3. 사전 로딩 ---
@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각"]

NOUN_DICT = load_oulipo_dict()

# --- 4. 메인 화면 ---
st.title("🐀 저보아 서클 시즌 2: 울리포 엔진")

st.markdown("""
<div class="instruction-box">
    <b>[울리포 엔진 가동 지침]</b><br>
    - <b>해부대:</b> 문장을 입력하세요. <b>줄 바꿈</b>과 <b>단어 사이의 여백</b>은 엄격히 보존됩니다.<br>
    - <b>성역 보호:</b> 변하지 않길 원하는 단어는 <b>&lt;단어&gt;</b> 와 같이 꺽쇠로 감싸세요. 꺽쇠 전후의 공백 또한 그대로 유지됩니다.<br>
    - <b>변환 확률:</b> 문장 속 모든 명사를 바꿀지, 일부만 무작위로 치환할지 결정합니다.<br>
    - <b>활자의 파동:</b> 진동과 비틀림을 조절하여 문장에 시각적 불안감을 부여하세요.
</div>
""", unsafe_allow_html=True)

user_input = st.text_area("문장을 해부대에 올리세요", placeholder="예: <나>는 오늘 <심연> 속에서 <사과>를 보았다.", height=200)

col1, col2 = st.columns(2)
with col1: shift_val = st.slider("S+N 거리 (사전 변조)", 1, 1000, 7)
with col2: prob_val = st.slider("변환 확률 (%)", 0, 100, 100)

col3, col4 = st.columns(2)
with col3: bumpy_val = st.slider("진동 (활자 크기)", 0.0, 0.6, 0.15)
with col4: tilt_val = st.slider("비틀림 (활자 각도)", 0, 30, 10)

def transform_with_protection(line, shift, prob):
    # 꺽쇠로 감싸진 성역과 일반 텍스트 분리
    parts = re.split(r'(<.*?>)', line)
    d_len = len(NOUN_DICT)
    line_result = []
    
    for part in parts:
        if part.startswith('<') and part.endswith('>'):
            # 성역: 꺽쇠만 제거하고 단어는 보존
            line_result.append(part[1:-1])
        elif part == '':
            continue
        else:
            # 일반 텍스트: 앞뒤 공백을 명시적으로 포착하여 보존
            leading_ws = re.match(r'^\s*', part).group()
            trailing_ws = re.search(r'\s*$', part).group()
            content = part.strip()
            
            if not content:
                line_result.append(part)
                continue
            
            tokens = kiwi.tokenize(content)
            sub_res = []
            for t in tokens:
                if t.tag.startswith('N'):
                    # 💡 확률 체크: 단어마다 고유한 해시값으로 결정하여 설정이 같으면 결과도 일정하게 유지
                    if (hash(t.form) % 100) < prob:
                        if t.form in NOUN_DICT:
                            idx = (NOUN_DICT.index(t.form) + shift) % d_len
                            new_w = NOUN_DICT[idx]
                        else:
                            random.seed(hash(t.form))
                            new_w = NOUN_DICT[random.randint(0, d_len-1)]
                        sub_res.append((new_w, 'NNG'))
                    else:
                        sub_res.append((t.form, t.tag))
                else:
                    sub_res.append((t.form, t.tag))
            
            # 원래의 공백과 함께 결합
            line_result.append(leading_ws + kiwi.join(sub_res) + trailing_ws)
            
    return "".join(line_result)

if st.button("✨ 문장 재단하기"):
    if user_input:
        lines = user_input.split('\n')
        st.subheader("🖼️ 변환 결과")
        html_res = '<div style="line-height: 2.3; word-wrap: break-word; padding: 25px; border: 3px solid #000000; background-color: #FFFFFF; white-space: pre-wrap;">'
        
        for line in lines:
            if not line.strip():
                html_res += '\n'
                continue
            transformed_line = transform_with_protection(line, shift_val, prob_val)
            for char in transformed_line:
                if char == ' ': 
                    html_res += '&nbsp;'
                else:
                    fs = 1.4 + random.uniform(-bumpy_val, bumpy_val)
                    rot = random.uniform(-tilt_val, tilt_val)
                    html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color:#000000 !important;">{char}</span>'
            html_res += '\n'
        
        html_res += '</div>'
        st.markdown(html_res, unsafe_allow_html=True)

st.divider()

# --- 5. 🏺 따로 움직이는 파편들 ---
st.subheader("🏺 사전의 파편들")
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
samples = random.sample(NOUN_DICT, min(40, len(NOUN_DICT)))

html_tags = '<div style="text-align:center; padding-bottom: 50px;">'
for w in samples:
    color = random.choice(washed_colors)
    delay = random.uniform(0, 4)
    duration = random.uniform(4, 7)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; animation-delay: {delay}s; animation-duration: {duration}s;">{w}</span>'
html_tags += '</div>'

st.markdown(html_tags, unsafe_allow_html=True)
