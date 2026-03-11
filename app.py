import streamlit as st
from kiwipiepy import Kiwi
import pandas as pd
import re
import random
import os

# --- 1. 페이지 설정 및 강제 화이트 테마 ---
st.set_page_config(page_title="Jerboa Oulipo Engine", page_icon="🐦", layout="wide")

# 세션 상태 초기화
if "archive" not in st.session_state:
    st.session_state.archive = []

# --- 2. 🎨 시각적 고정: 칠흑의 활자 & 순백의 배경 (CSS) ---
st.markdown("""
<style>
    /* 시스템 다크모드를 완전히 무시하고 라이트 모드 강제 */
    :root { color-scheme: light !important; }
    
    /* 배경은 완전한 백색, 글자는 완전한 검정 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 을유1945 폰트 설정 */
    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    /* 모든 텍스트 요소를 검정색으로 강제 */
    * { 
        font-family: 'Eulyoo1945-Regular', serif !important; 
        color: #000000 !important; 
    }

    /* 알림창(Success, Info 등) 배경과 글자색 수정 */
    .stAlert, [data-testid="stNotificationContent"] {
        background-color: #F0F2F6 !important;
        border: 1px solid #000000 !important;
    }
    .stAlert p, .stAlert span { color: #000000 !important; }

    /* 🌊 움직이는 파편 애니메이션 */
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

    /* 입력창 및 UI 요소 */
    textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* 금속 활자 버튼 (검은 배경에 흰 글자) */
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #888888 !important;
        border: none !important;
    }
    div.stButton > button p { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. 엔진 코어: 모든 사전 파일 강제 탐색 ---
@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

@st.cache_data(show_spinner=False)
def load_comprehensive_dictionary():
    all_nouns = []
    # 💡 폴더 내의 모든 파일을 훑어서 '30000'이나 '14936'이 들어간 파일을 찾음
    all_files = os.listdir('.')
    target_files = [f for f in all_files if any(p in f for p in ['30000', '14936', 'xls', 'csv'])]
    
    for f in target_files:
        try:
            # 엑셀 혹은 CSV로 읽기 시도
            if f.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(f)
            else:
                for enc in ['utf-8-sig', 'cp949', 'euc-kr']:
                    try:
                        df = pd.read_csv(f, encoding=enc)
                        break
                    except: continue
            
            # '표제어'와 '품사' 열이 존재하는지 확인
            if '품사' in df.columns and '표제어' in df.columns:
                nouns_df = df[df['품사'].fillna('').str.contains('명사')]
                for word in nouns_df['표제어'].astype(str):
                    clean_word = word.strip().replace('-', '').replace('^', '')
                    # 2~4글자 순수 한글 필터
                    if 2 <= len(clean_word) <= 4 and re.match(r'^[가-힣]+$', clean_word):
                        all_nouns.append(clean_word)
        except: continue
                
    final_dict = sorted(list(set(all_nouns)))
    
    # 💡 만약 데이터가 여전히 없으면(실패 시) 보들레르 스타일의 비상 단어장
    if len(final_dict) < 50:
        return sorted(["거울", "파편", "심연", "공백", "권태", "기억", "망각", "미학", "시체", "악의", "오브제", "육체", "잔해", "향기", "형식", "시간", "공간", "존재", "허무", "환상", "몽상", "균열", "착각", "구속", "여백", "침묵", "단어", "운명", "안개", "촛불", "가면", "보석", "칼날", "유리", "유령", "철학", "초상", "축제", "풍경", "햇살", "호수", "화가", "흔적", "희망", "희곡"]), "FALLBACK"
    
    return final_dict, "SUCCESS"

# 사전 장전
with st.spinner("언어의 성채를 짓는 중..."):
    NOUN_DICT, load_status = load_comprehensive_dictionary()

# --- 4. 메인 화면 ---
st.title("🐦 저보아: XLS 전권 탑재 엔진")
st.success(f"✅ 사전 탐색 완료: {len(NOUN_DICT):,}개의 명사가 칠흑의 활자로 장전되었습니다.")

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
        # 칠흑의 활자 렌더링
        html_res = '<div style="line-height: 2.8; word-wrap: break-word; padding: 30px; border: 3px solid #000000;">'
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

html_tags = '<div style="text-align:center; padding: 50px 0;">'
for i, w in enumerate(samples):
    color = random.choice(washed_colors)
    delay = random.uniform(0, 5)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; color:#000000 !important; animation-delay: {delay}s;">{w}</span>'
html_tags += '</div>'
st.markdown(html_tags, unsafe_allow_html=True)

# 디버깅용 (사이드바)
with st.sidebar:
    st.write("### 🔍 탐색된 파일 목록")
    st.write(os.listdir('.'))
