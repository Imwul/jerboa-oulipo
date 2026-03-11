import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import random
import time
from concurrent.futures import ThreadPoolExecutor

# --- 1. 페이지 및 상태 설정 ---
st.set_page_config(page_title="Jerboa Oulipo Engine", page_icon="🐦", layout="wide")

if "archive" not in st.session_state:
    st.session_state.archive = []

# --- 2. 🎨 심연의 미학 (CSS) ---
st.markdown("""
<style>
    /* 1. 어두운 배경 강제 고정 */
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #0E1117 !important;
    }

    /* 2. 을유1945 폰트 및 모든 글자 하얀색 강제 */
    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    * { 
        font-family: 'Eulyoo1945-Regular', serif !important; 
        color: #FFFFFF !important; /* 모든 글자를 하얗게 */
    }

    /* 3. 유령처럼 떠다니는 애니메이션 */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(2deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    .fragment-tag {
        display: inline-block;
        padding: 8px 16px;
        margin: 10px;
        border-radius: 2px;
        border: 1px solid rgba(255,255,255,0.3);
        animation: float 5s ease-in-out infinite;
        cursor: crosshair;
        font-weight: bold;
    }

    /* 4. 입력창 디자인 (어두운 배경에 대비) */
    textarea {
        background-color: #1A1C24 !important;
        color: #FFFFFF !important;
        border: 1px solid #3D4450 !important;
    }

    /* 5. 버튼 디자인 (흰색 배경에 검은 글자) */
    div.stButton > button {
        background-color: #E0E0E0 !important;
        color: #0E1117 !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #555555 !important;
        font-weight: bold !important;
    }
    
    /* 슬라이더 라벨 등 특수 요소 색상 */
    .stSlider label, .stTextArea label { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. 엔진 코어 ---
@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

def fetch_words_new(kw, API_KEY):
    # 💡 이물이 찾아준 Swagger 명세 반영: getContents632 경로 사용
    url = "http://api.kcisa.kr/openapi/service/rest/contents/getContents632"
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 40,
        "pageNo": 1,
        "keyword": kw  # 💡 명세에 따라 반드시 keyword 포함
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            items = []
            for elem in root.iter():
                tag_name = elem.tag.split('}')[-1]
                if tag_name in ['title', 'word']:
                    if elem.text:
                        w = elem.text.split('(')[0].strip().replace('-', '').replace('^', '')
                        if 2 <= len(w) <= 4 and all(ord('가') <= ord(c) <= ord('힣') for c in w):
                            items.append(w)
            return items
    except: pass
    return []

@st.cache_data(show_spinner=False)
def get_oulipo_dictionary():
    API_KEY = "8f778621-2475-45d2-955c-c4dc91543917"
    # 명세서 규칙에 따라 핵심 키워드로 수집
    keywords = ["심연", "거울", "파편", "공백", "기억", "망각", "미학", "시체", "악의"]
    total_words = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for words in executor.map(lambda kw: fetch_words_new(kw, API_KEY), keywords):
            total_words.extend(words)
    
    final_dict = sorted(list(set(total_words)))
    
    # [예술적 안전망] 수집 실패 시 가동될 니치한 단어장 (이물의 안목 반영)
    FALLBACK = sorted(["가면", "공백", "거울", "심연", "파편", "권태", "몽상", "미학", "시체", "악의", "오브제", "육체", "잔해", "향기", "형식", "시간", "공간", "존재", "허무", "환상", "그늘", "기억", "노을", "비밀", "새벽", "영혼", "어둠", "여백", "침묵", "단어", "운명", "균열"])
    
    if len(final_dict) < 20: return FALLBACK, "FALLBACK"
    return final_dict, "ONLINE"

# --- 4. 메인 가동 ---
NOUN_DICT, load_mode = get_oulipo_dictionary()

st.title("🐦 저보아: NEW 울리포 엔진")
st.caption("심연의 명사들이 당신의 해부대를 기다립니다.")

# --- 5. 변환 인터페이스 ---
user_input = st.text_area("해부대에 올릴 문장", placeholder="여기에 텍스트를 넣으세요.", height=150)

col1, col2, col3 = st.columns(3)
with col1: shift_val = st.slider("사전 변조 거리 (S+N)", 1, 50, 7)
with col2: bumpy_val = st.slider("활자의 진동", 0.0, 0.6, 0.2)
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
            else:
                result.append((t.form, t.tag))
        
        transformed = kiwi.join(result)
        st.session_state.archive.append((user_input, transformed))
        
        st.subheader("🖼️ 변환 결과")
        # 💡 비틀린 활자 효과 재구현
        html_res = '<div style="line-height: 2.8; word-wrap: break-word; padding: 30px; border: 1px solid rgba(255,255,255,0.1);">'
        for char in transformed:
            if char == ' ':
                html_res += '&nbsp;'
                continue
            fs = 1.8 + random.uniform(-bumpy_val, bumpy_val)
            rot = random.uniform(-tilt_val, tilt_val)
            html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color:#FFFFFF;">{char}</span>'
        html_res += '</div>'
        st.markdown(html_res, unsafe_allow_html=True)

st.divider()

# --- 6. 아카이브 및 🏺 떠다니는 파편들 ---
st.subheader("🏺 사전의 파편들")
# 파스텔 색상 입힌 움직이는 파편들
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
samples = random.sample(NOUN_DICT, min(50, len(NOUN_DICT)))

html_tags = '<div style="text-align:center; padding: 50px 0;">'
for i, w in enumerate(samples):
    color = random.choice(washed_colors)
    delay = random.uniform(0, 5)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; color:#111 !important; animation-delay: {delay}s;">{w}</span>'
html_tags += '</div>'

st.markdown(html_tags, unsafe_allow_html=True)
