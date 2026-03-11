import streamlit as st
from kiwipiepy import Kiwi
import pandas as pd
import re
import random
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Jerboa Oulipo Engine", page_icon="🐦", layout="wide")

if "archive" not in st.session_state:
    st.session_state.archive = []

# --- 2. 🎨 칠흑의 활자와 역동적인 캔버스 (CSS) ---
st.markdown("""
<style>
    /* 다크모드 무시 및 완전한 백색 배경 고정 */
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        background-color: #FFFFFF !important;
    }

    /* 을유1945 폰트 및 칠흑색 활자 강제 */
    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    * { 
        font-family: 'Eulyoo1945-Regular', serif !important; 
        color: #000000 !important; 
    }

    /* 🌊 유령처럼 떠다니는 파편 애니메이션 */
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
        border: 1px solid #000000;
        animation: float 5s ease-in-out infinite;
        cursor: crosshair;
        font-weight: bold;
    }

    /* 입력창 및 UI 요소 가시성 확보 */
    textarea {
        background-color: #FDFDFD !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    .stSlider label, .stTextArea label { color: #000000 !important; }

    /* 금속 활자 버튼 */
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #888888 !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 엔진 코어: 로컬 사전 파싱 ---
@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

@st.cache_data(show_spinner=False)
def load_local_dictionary():
    # 이물이 올린 3개의 파일 이름
    files = [
        "1_30000_20260226.xls - Sheet0.csv",
        "2_30000_20260226.xls - Sheet0.csv",
        "3_14936_20260226.xls - Sheet0.csv"
    ]
    
    all_nouns = []
    for f in files:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f)
                # '품사' 열에서 '명사' 포함 행 추출, '표제어' 열에서 단어 추출
                nouns_df = df[df['품사'].fillna('').str.contains('명사')]
                for word in nouns_df['표제어'].astype(str):
                    # 사전 기호(-, ^) 제거 및 2~4글자 한글 필터링
                    clean_word = word.strip().replace('-', '').replace('^', '')
                    if 2 <= len(clean_word) <= 4 and re.match(r'^[가-힣]+$', clean_word):
                        all_nouns.append(clean_word)
            except: pass
            
    final_dict = sorted(list(set(all_nouns)))
    
    # 만약 파일이 없거나 수집에 실패할 경우를 대비한 최소한의 안전망
    if not final_dict:
        final_dict = sorted(["거울", "파편", "심연", "공백", "권태", "기억", "망각", "미학", "시체", "악의", "오브제", "육체", "잔해", "향기", "형식", "시간", "공간", "존재", "허무", "환상"])
    
    return final_dict

# 사전 장전
with st.spinner("방대한 사전의 심연을 데이터베이스로 구축하는 중..."):
    NOUN_DICT = load_local_dictionary()

# --- 4. 메인 화면 ---
st.title("🐦 저보아: 사전 전권 탑재 엔진")
st.caption(f"로컬 사전에서 추출한 {len(NOUN_DICT):,}개의 순수 명사가 장전되었습니다. 네트워크 장애는 이제 없습니다.")

# 인터페이스 구성
user_input = st.text_area("해부대에 올릴 문장", placeholder="여기에 텍스트를 넣으세요.", height=150)

col1, col2, col3 = st.columns(3)
with col1: shift_val = st.slider("사전 변조 거리 (S+N)", 1, 100, 7)
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
            else:
                result.append((t.form, t.tag))
        
        transformed = kiwi.join(result)
        st.session_state.archive.append((user_input, transformed))
        
        st.subheader("🖼️ 변환 결과")
        # 💡 검은 글자가 비틀거리며 춤추는 렌더링
        html_res = '<div style="line-height: 2.8; word-wrap: break-word; padding: 30px; border: 3px solid #000000; background-color: #FFFFFF;">'
        for char in transformed:
            if char == ' ':
                html_res += '&nbsp;'
                continue
            fs = 1.8 + random.uniform(-bumpy_val, bumpy_val)
            rot = random.uniform(-tilt_val, tilt_val)
            html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color:#000000 !important;">{char}</span>'
        html_res += '</div>'
        st.markdown(html_res, unsafe_allow_html=True)

st.divider()

# --- 5. 🏺 떠다니는 파편들 (애니메이션) ---
st.subheader("🏺 사전의 파편들")
# 파스텔 색상 배경에 칠흑 글씨의 파편들
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
# 2.6만개 중 50개만 랜덤 시각화
samples = random.sample(NOUN_DICT, min(50, len(NOUN_DICT)))

html_tags = '<div style="text-align:center; padding: 50px 0; background-color: #FFFFFF;">'
for i, w in enumerate(samples):
    color = random.choice(washed_colors)
    delay = random.uniform(0, 5)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; color:#000000 !important; animation-delay: {delay}s;">{w}</span>'
html_tags += '</div>'

st.markdown(html_tags, unsafe_allow_html=True)
