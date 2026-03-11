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

# --- 2. 🎨 칠흑과 순백의 미학 (CSS) ---
st.markdown("""
<style>
    /* 다크모드 무시 및 완전한 백색 배경 강제 */
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        background-color: #FFFFFF !important;
    }

    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    /* ❗ 모든 글자를 칠흑 같은 검정(#000000)으로 강제 */
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
        border: 2px solid #000000;
        animation: float 5s ease-in-out infinite;
        cursor: crosshair;
        font-weight: bold;
    }

    /* 입력창 디자인 (검은 글자 가독성 극대화) */
    textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    .stSlider label, .stTextArea label, .stMarkdown p { color: #000000 !important; }

    /* 금속 활자 버튼 (검은 배경에 흰 글자) */
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #888888 !important;
        font-weight: bold !important;
    }
    div.stButton > button * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. 엔진 코어: XLS/CSV 통합 포식기 ---
@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

@st.cache_data(show_spinner=False)
def load_local_dictionary():
    all_nouns = []
    # 💡 XLS, XLSX, CSV 파일을 모두 탐색
    target_exts = ('.xls', '.xlsx', '.csv')
    data_files = [f for f in os.listdir('.') if f.lower().endswith(target_exts)]
    
    if not data_files:
        # 파일이 없을 때만 비상용 단어장 가동
        return sorted(["거울", "파편", "심연", "공백", "기억", "망각", "미학", "시체", "악의", "오브제", "육체", "잔해", "향기", "형식", "시간", "공간", "존재", "허무", "환상"]), "FALLBACK"

    for f in data_files:
        try:
            # 확장자에 따라 읽기 방식 결정
            if f.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(f)
            else:
                # CSV의 경우 인코딩 여러 번 시도
                for enc in ['utf-8-sig', 'cp949', 'euc-kr']:
                    try:
                        df = pd.read_csv(f, encoding=enc)
                        break
                    except: continue
            
            # 표제어와 품사 열이 있는지 확인
            if '품사' in df.columns and '표제어' in df.columns:
                nouns_df = df[df['품사'].fillna('').str.contains('명사')]
                for word in nouns_df['표제어'].astype(str):
                    clean_word = word.strip().replace('-', '').replace('^', '')
                    if 2 <= len(clean_word) <= 4 and re.match(r'^[가-힣]+$', clean_word):
                        all_nouns.append(clean_word)
        except: continue
                
    final_dict = sorted(list(set(all_nouns)))
    return final_dict, "SUCCESS"

# 사전 장전
with st.spinner("XLS 사전의 모든 파편을 해독하는 중..."):
    NOUN_DICT, load_status = load_local_dictionary()

# --- 4. 메인 화면 ---
st.title("🐦 저보아: XLS 전권 탑재 엔진")
st.caption(f"사전 탐색 완료: {len(NOUN_DICT):,}개의 명사가 칠흑의 활자로 장전되었습니다.")

user_input = st.text_area("해부대에 올릴 문장", placeholder="여기에 텍스트를 넣으세요.", height=150)

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
        st.session_state.archive.append((user_input, transformed))
        
        st.subheader("🖼️ 변환 결과")
        # 💡 칠흑 같은 검은색 글자가 역동적으로 춤추는 결과창
        html_res = '<div style="line-height: 2.8; word-wrap: break-word; padding: 30px; border: 3px solid #000000; background-color: #FFFFFF;">'
        for char in transformed:
            if char == ' ': html_res += '&nbsp;'
            else:
                fs = 1.8 + random.uniform(-bumpy_val, bumpy_val)
                rot = random.uniform(-tilt_val, tilt_val)
                html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color:#000000 !important;">{char}</span>'
        html_res += '</div>'
        st.markdown(html_res, unsafe_allow_html=True)

st.divider()

# --- 5. 🏺 떠다니는 파편들 (애니메이션) ---
st.subheader("🏺 사전의 파편들")
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
samples = random.sample(NOUN_DICT, min(60, len(NOUN_DICT)))

html_tags = '<div style="text-align:center; padding: 50px 0; background-color: #FFFFFF;">'
for i, w in enumerate(samples):
    color = random.choice(washed_colors)
    delay = random.uniform(0, 5)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; color:#000000 !important; animation-delay: {delay}s;">{w}</span>'
html_tags += '</div>'
st.markdown(html_tags, unsafe_allow_html=True)
