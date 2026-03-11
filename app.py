import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import random
import time
from concurrent.futures import ThreadPoolExecutor

# 페이지 설정
st.set_page_config(page_title="Jerboa Oulipo Engine", page_icon="🐦", layout="wide")

# --- 상태 저장소 ---
if "archive" not in st.session_state:
    st.session_state.archive = []

# --- 🎨 라이트 모드 & 을유1945 폰트 & 버튼 디자인 ---
st.markdown("""
<style>
@font-face {
    font-family: 'Eulyoo1945-Regular';
    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    font-weight: normal;
    font-style: normal;
}
.stApp { background-color: #FFFFFF !important; }
html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #111111 !important;
    font-family: 'Eulyoo1945-Regular', serif !important;
    letter-spacing: -0.03em !important;
}
.fragment-tag {
    display: inline-block;
    padding: 6px 14px;
    margin: 8px;
    border-radius: 4px;
    color: #222222 !important; 
    border: 1px solid #dcdcdc;
    box-shadow: 1px 2px 5px rgba(0,0,0,0.05);
}
.fragment-tag:hover {
    transform: scale(1.15) !important;
    z-index: 10;
    cursor: crosshair;
}
@keyframes float {
    0% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-8px) rotate(1deg); }
    100% { transform: translateY(0px) rotate(0deg); }
}
.stTextArea textarea, .stSlider > div {
    background-color: #f9f9f9 !important;
    color: #111111 !important;
    border: 1px solid #cccccc !important;
}
div.stButton > button {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 2px solid #111111 !important;
    border-radius: 0px !important;
    box-shadow: 3px 3px 0px #111111 !important;
    font-family: 'Eulyoo1945-Regular', serif !important;
    font-weight: bold !important;
    transition: all 0.1s ease-in-out;
}
div.stButton > button:hover {
    transform: translate(2px, 2px);
    box-shadow: 1px 1px 0px #111111 !important;
    background-color: #f1f1f1 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 엔진 부품 ---
@st.cache_resource
def load_kiwi():
    return Kiwi()

def fetch_words(kw, API_KEY):
    url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q={kw}&target=1&num=100&advanced=y&method=include&pos=1&sort=popular"
    try:
        res = requests.get(url, timeout=5, verify=False)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            words = [node.text.replace('-', '').replace('^', '') for node in root.findall('.//item/word') if node.text]
            # 💡 이물의 지시: 4글자 이상 전면 차단! (2~3글자만 허용), 띄어쓰기 없음, 완벽한 한글
            return [w for w in words if 2 <= len(w) <= 3 and ' ' not in w and all(ord('가') <= ord(c) <= ord('힣') for c in w)]
    except:
        return []
    return []

@st.cache_data(show_spinner=False)
def diagnostic_load():
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    
    # 💡 이물의 지시 반영: 너무 니치한 것을 빼고, 일상적이고 감성적인 '대중 픽' 키워드로 전면 교체
    keywords = [
        "사람", "마음", "시간", "하루", "사랑", "친구", "세상", "이유", "생각", "기억", 
        "바람", "하늘", "바다", "얼굴", "소리", "가족", "이야기", "노래", "마을", "도시", 
        "나무", "우주", "역사", "미래", "과거", "눈물", "웃음", "약속", "여행", "사진"
    ]
    
    total_words = []
    my_bar = st.progress(0, text="대중적이고 익숙한 일상 단어들을 수집하는 중...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i, words in enumerate(executor.map(lambda kw: fetch_words(kw, API_KEY), keywords)):
            total_words.extend(words)
            my_bar.progress((i + 1) / len(keywords), text=f"일상 파편 발굴 중... (현재 {len(total_words)}개 수집)")
            time.sleep(0.05)
            
    my_bar.empty()
    
    final_dict = sorted(list(set(total_words)))
    
    if len(final_dict) < 50:
         # 비상용 단어들도 아주 일상적인 것으로 교체
         base_dict = ["사람", "마음", "시간", "하루", "사랑", "친구", "세상", "이유", "생각", "기억", "바람", "하늘", "바다", "얼굴", "소리", "이야기", "노래", "마을", "도시", "나무"]
         final_dict = sorted(list(set(final_dict + base_dict)))
         
    return final_dict
    
    # 5개씩 부드럽게 병렬 처리 (서버 차단 방지 및 속도 확보)
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i, words in enumerate(executor.map(lambda kw: fetch_words(kw, API_KEY), keywords)):
            total_words.extend(words)
            my_bar.progress((i + 1) / len(keywords), text=f"국립국어원에서 파편 발굴 중... (현재 {len(total_words)}개 수집)")
            time.sleep(0.05)
            
    my_bar.empty()
    
    # 오리지널 S+N을 위한 철저한 가나다순 정렬 및 중복 제거
    final_dict = sorted(list(set(total_words)))
    
    if len(final_dict) < 50:
         base_dict = ["가방", "거울", "고독", "공백", "권태", "기억", "망각", "미학", "시체", "심연", "악의", "오브제", "육체", "잔해", "파편", "향기", "형식", "황금"]
         final_dict = sorted(list(set(final_dict + base_dict)))
         
    return final_dict

kiwi = load_kiwi()
NOUN_DICT = diagnostic_load()

# --- UI 레이아웃 ---
st.title("🐦 저보아: 무한 울리포 엔진")
st.caption(f"국립국어원에서 추출한 {len(NOUN_DICT):,}개의 순수 명사가 가나다순으로 장전되었습니다.")

st.subheader("⚙️ 예술적 통제판")
col1, col2, col3 = st.columns(3)
with col1:
    shift_val = st.slider("사전 변조 거리 (S+N)", min_value=1, max_value=50, value=7)
with col2:
    bumpy_level = st.slider("활자의 진동 (크기)", min_value=0.0, max_value=0.8, value=0.2, step=0.05)
with col3:
    tilt_level = st.slider("활자의 비틀림 (각도)", min_value=0, max_value=30, value=5, step=1)

user_input = st.text_area("해부대에 올릴 문장을 입력해.", placeholder="나는 오늘 공원에서 사과를 먹었다.")

# --- 변환 로직 (오리지널 S+N) ---
def transform_engine(text, dictionary, shift):
    if not text.strip(): return "입력된 공백."
    tokens = kiwi.tokenize(text)
    result = []
    dict_len = len(dictionary)
    
    for t in tokens:
        if t.tag.startswith('N'):
            if t.form in dictionary:
                idx = (dictionary.index(t.form) + shift) % dict_len
                new_word = dictionary[idx]
            else:
                random.seed(hash(t.form))
                idx = (random.randint(0, dict_len - 1) + shift) % dict_len
                new_word = dictionary[idx]
            result.append((new_word, 'NNG'))
        else:
            result.append((t.form, t.tag))
    return kiwi.join(result)

# 글자 렌더링
def render_bumpy_text(text, b_level, t_level):
    html = '<div style="line-height: 2.5; word-wrap: break-word;">'
    for char in text:
        if char == ' ':
            html += '&nbsp;'
            continue
        fs = 1.3 + random.uniform(-b_level, b_level)
        tilt = random.uniform(-t_level, t_level)
        html += f'<span style="font-size: {fs}rem; transform: rotate({tilt}deg); display:inline-block; transition: all 0.2s; font-weight: bold;">{char}</span>'
    html += '</div>'
    return html

if st.button("✨ 문장 재단 및 아카이빙"):
    if user_input:
        transformed = transform_engine(user_input, NOUN_DICT, shift_val)
        st.session_state.archive.append((user_input, transformed))
        
        st.subheader("🖼️ 변환된 결과")
        st.markdown(render_bumpy_text(transformed, bumpy_level, tilt_level), unsafe_allow_html=True)
    else:
        st.warning("문장을 먼저 입력해야 해.")

st.divider()

# --- 아카이브 (로그) ---
col_log1, col_log2 = st.columns([4, 1])
with col_log1:
    st.subheader("📜 과거의 흔적 (공동 시집)")
with col_log2:
    if st.button("🗑️ 로그 전체 삭제"):
        st.session_state.archive = []
        st.rerun()

if st.session_state.archive:
    for orig, trans in reversed(st.session_state.archive):
        st.markdown(f"<span style='color:#777777; font-size:0.9rem;'>{orig}</span><br><b style='color:#111111; font-size:1.1rem;'>{trans}</b>", unsafe_allow_html=True)
        st.caption("---")
else:
    st.info("아직 쌓인 흔적이 없어.")

st.divider()

# --- 시각화: 물 빠진 원색 파편들 ---
st.subheader(f"🏺 {len(NOUN_DICT):,}개의 파편들 중 일부")

visual_samples = random.sample(NOUN_DICT, min(70, len(NOUN_DICT)))
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]

html_tags = ""
for w in visual_samples:
    color = random.choice(washed_colors)
    font_size = 0.8 + (len(w) * 0.15)
    anim_delay = random.uniform(0, 3)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; font-size:{font_size}rem; animation: float 4s ease-in-out infinite; animation-delay: {anim_delay}s;">{w}</span>'

st.markdown(f'<div style="text-align:center;">{html_tags}</div>', unsafe_allow_html=True)
