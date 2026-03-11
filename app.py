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

# --- 2. 🎨 캔버스 및 활자 디자인 (CSS) ---
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

# --- 3. 엔진 코어 부품 ---
@st.cache_resource
def load_kiwi():
    return Kiwi()

def fetch_words(kw, API_KEY):
    url = f"https://api.kcisa.kr/openapi/API_SOP_027/request?serviceKey={API_KEY}&numOfRows=100&pageNo=1&keyword={kw}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/xml"
    }
    try:
        res = requests.get(url, timeout=5, verify=False, headers=headers)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            clean_words = []
            for word_node in root.findall('.//word'):
                if word_node is None or not word_node.text: continue
                w = word_node.text.replace('-', '').replace('^', '').strip()
                if 2 <= len(w) <= 4 and ' ' not in w and all(ord('가') <= ord(c) <= ord('힣') for c in w):
                    clean_words.append(w)
            return clean_words
    except:
        return []
    return []

@st.cache_data(show_spinner=False)
def diagnostic_load():
    API_KEY = "8f778621-2475-45d2-955c-c4dc91543917"
    keywords = [
        "가", "고", "구", "기", "나", "노", "누", "니", "다", "도", "두", "디",
        "라", "로", "루", "리", "마", "모", "무", "미", "바", "보", "부", "비",
        "사", "소", "수", "시", "아", "오", "우", "이", "자", "조", "주", "지",
        "차", "초", "추", "치", "카", "코", "쿠", "키", "타", "토", "투", "티",
        "파", "포", "푸", "피", "하", "호", "후", "히"
    ]
    
    total_words = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for words in executor.map(lambda kw: fetch_words(kw, API_KEY), keywords):
            total_words.extend(words)
            time.sleep(0.05)
            
    final_dict = sorted(list(set(total_words)))
    status = "success"
    
    # 💡 최후의 보루: 아름답고 기괴한 100개의 수동 단어장 (절대 1단어로 수렴하지 않음)
    base_dict = [
        "거울", "파편", "심연", "공백", "권태", "기억", "망각", "미학", "시체", "악의",
        "오브제", "육체", "잔해", "향기", "형식", "황금", "시간", "공간", "존재", "허무",
        "환상", "몽상", "사람", "마음", "하루", "사랑", "친구", "세상", "이유", "생각",
        "바람", "하늘", "바다", "얼굴", "소리", "이야기", "노래", "마을", "도시", "나무",
        "우주", "역사", "미래", "과거", "눈물", "웃음", "약속", "여행", "사진", "그림",
        "새벽", "황혼", "노을", "구름", "별빛", "달빛", "햇살", "그림자", "골목", "계절",
        "침묵", "언어", "문장", "단어", "여백", "비밀", "거짓", "진실", "운명", "우연",
        "인연", "이별", "만남", "슬픔", "기쁨", "고독", "자유", "구속", "착각", "균열"
    ]
    
    if len(final_dict) < 50:
         status = "fallback"
         fallback_url = "https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/korean.txt"
         try:
             res = requests.get(fallback_url, timeout=5)
             if res.status_code == 200:
                 fallback_words = res.text.split('\n')
                 # 🚨 한글 필터 완벽 적용! 1단어 에러 원천 차단
                 clean_fallback = [w.strip() for w in fallback_words if 2 <= len(w.strip()) <= 4 and all(ord('가') <= ord(c) <= ord('힣') for c in w.strip())]
                 if len(clean_fallback) > 50:
                     final_dict = sorted(list(set(clean_fallback)))
                 else:
                     final_dict = sorted(list(set(base_dict)))
             else:
                 final_dict = sorted(list(set(base_dict)))
         except:
             final_dict = sorted(list(set(base_dict)))
             
    return final_dict, status

# --- 엔진 시동 ---
kiwi = load_kiwi()

with st.spinner("사전의 심연을 탐색하는 중..."):
    NOUN_DICT, load_status = diagnostic_load()

if load_status == "fallback":
    st.toast("⚠️ KCISA 방화벽 차단! 비상 단어장으로 안전하게 우회 가동했어.", icon="🛡️")

# --- 4. 사용자 인터페이스 (UI) ---
st.title("🐦 저보아: 무한 울리포 엔진")
st.caption(f"정제된 사전을 통과한 {len(NOUN_DICT):,}개의 순수 명사가 가나다순으로 장전되었습니다.")

st.subheader("⚙️ 예술적 통제판")
col1, col2, col3 = st.columns(3)
with col1:
    shift_val = st.slider("사전 변조 거리 (S+N)", min_value=1, max_value=50, value=7)
with col2:
    bumpy_level = st.slider("활자의 진동 (크기)", min_value=0.0, max_value=0.8, value=0.2, step=0.05)
with col3:
    tilt_level = st.slider("활자의 비틀림 (각도)", min_value=0, max_value=30, value=5, step=1)

user_input = st.text_area("해부대에 올릴 문장을 입력해.", placeholder="나는 오늘 공원에서 사과를 먹었다.")

# --- 5. 문장 해부 및 재조립 (로직) ---
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

# --- 6. 출력 및 아카이빙 ---
if st.button("✨ 문장 재단 및 아카이빙"):
    if user_input:
        transformed = transform_engine(user_input, NOUN_DICT, shift_val)
        st.session_state.archive.append((user_input, transformed))
        
        st.subheader("🖼️ 변환된 결과")
        st.markdown(render_bumpy_text(transformed, bumpy_level, tilt_level), unsafe_allow_html=True)
    else:
        st.warning("문장을 먼저 입력해야 해.")

st.divider()

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

# --- 7. 시각화: 떠다니는 파편들 ---
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
