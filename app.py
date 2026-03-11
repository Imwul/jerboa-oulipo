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

# --- 2. 🎨 디자인 (CSS) ---
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
}
</style>
""", unsafe_allow_html=True)

# --- 3. 엔진 코어 부품 ---
@st.cache_resource
def load_kiwi():
    return Kiwi()

def fetch_words(kw, API_KEY):
    # 명세서에 따른 파라미터 구성 (keyword 포함 필수)
    url = "https://api.kcisa.kr/openapi/API_SOP_027/request"
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 100,
        "pageNo": 1,
        "keyword": kw
    }
    headers = {
        "Accept": "application/xml",
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        # verify=False는 SSL 인증서 오류 방지용
        res = requests.get(url, params=params, timeout=10, verify=False, headers=headers)
        if res.status_code == 200:
            # XML 파싱 시 네임스페이스 문제를 피하기 위해 태그명으로만 검색
            root = ET.fromstring(res.content)
            clean_words = []
            
            # 모든 item 내의 title 태그를 찾음
            for item in root.findall('.//item'):
                title = item.find('title')
                if title is not None and title.text:
                    # 괄호 및 특수기호 제거 후 단어만 추출
                    word = title.text.split('(')[0].strip()
                    word = word.replace('-', '').replace('^', '')
                    
                    # 2~4글자 순수 한글 명사 필터
                    if 2 <= len(word) <= 4 and all(ord('가') <= ord(c) <= ord('힣') for c in word):
                        clean_words.append(word)
            return clean_words
    except Exception:
        return []
    return []

@st.cache_data(show_spinner=False)
def diagnostic_load():
    # 사용자 제공 API 키
    API_KEY = "8f778621-2475-45d2-955c-c4dc91543917"
    
    # 기초 음절을 키워드로 활용하여 넓은 범위의 단축 수집
    keywords = [
        "가", "나", "다", "라", "마", "바", "사", "아", "자", "차", "카", "타", "파", "하",
        "물", "불", "산", "들", "길", "사람", "마음", "하늘", "바다"
    ]
    
    total_words = []
    # 병렬 처리를 통해 속도 향상
    with ThreadPoolExecutor(max_workers=5) as executor:
        for words in executor.map(lambda kw: fetch_words(kw, API_KEY), keywords):
            total_words.extend(words)
            
    final_dict = sorted(list(set(total_words)))
    status = "success"
    
    # 80개 이하일 경우 수집 실패로 간주하고 로컬 단어장으로 우회
    if len(final_dict) < 50:
        status = "fallback"
        final_dict = sorted([
            "거울", "파편", "심연", "공백", "권태", "기억", "망각", "미학", "시체", "악의",
            "오브제", "육체", "잔해", "향기", "형식", "황금", "시간", "공간", "존재", "허무",
            "환상", "몽상", "사람", "마음", "하루", "사랑", "친구", "세상", "이유", "생각",
            "바람", "하늘", "바다", "얼굴", "소리", "이야기", "노래", "마을", "도시", "나무",
            "우주", "역사", "미래", "과거", "눈물", "웃음", "약속", "여행", "사진", "그림",
            "새벽", "황혼", "노을", "구름", "별빛", "달빛", "햇살", "그림자", "골목", "계절",
            "침묵", "언어", "문장", "단어", "여백", "비밀", "거짓", "진실", "운명", "우연",
            "인연", "이별", "만남", "슬픔", "기쁨", "고독", "자유", "구속", "착각", "균열"
        ])
             
    return final_dict, status

# --- 4. 엔진 작동 및 메인 화면 ---
kiwi = load_kiwi()

with st.spinner("명세에 따라 사전을 재구성하는 중..."):
    NOUN_DICT, load_status = diagnostic_load()

if load_status == "fallback":
    st.toast("API 응답이 원활하지 않아 로컬 단어장으로 전환되었습니다.", icon="⚠️")

st.title("🐦 무한 울리포 엔진")
st.caption(f"사전에서 추출한 {len(NOUN_DICT):,}개의 명사가 장전되었습니다.")

st.subheader("⚙️ 통제판")
col1, col2, col3 = st.columns(3)
with col1:
    shift_val = st.slider("변조 거리 (S+N)", 1, 50, 7)
with col2:
    bumpy_level = st.slider("진동 크기", 0.0, 0.8, 0.2)
with col3:
    tilt_level = st.slider("비틀림 각도", 0, 30, 5)

user_input = st.text_area("문장을 입력하세요.", placeholder="여기에 텍스트를 넣으세요.")

def transform_engine(text, dictionary, shift):
    if not text.strip(): return ""
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

def render_styled_text(text, b_level, t_level):
    html = '<div style="line-height: 2.5; word-wrap: break-word;">'
    for char in text:
        if char == ' ':
            html += '&nbsp;'
            continue
        fs = 1.3 + random.uniform(-b_level, b_level)
        tilt = random.uniform(-t_level, t_level)
        html += f'<span style="font-size:{fs}rem; transform:rotate({tilt}deg); display:inline-block; font-weight:bold;">{char}</span>'
    html += '</div>'
    return html

if st.button("문장 변환"):
    if user_input:
        transformed = transform_engine(user_input, NOUN_DICT, shift_val)
        st.session_state.archive.append((user_input, transformed))
        st.markdown(render_styled_text(transformed, bumpy_level, tilt_level), unsafe_allow_html=True)

st.divider()

# --- 5. 시각화: 파편들 ---
st.subheader("🏺 사전의 파편들")
if len(NOUN_DICT) >= 70:
    visual_samples = random.sample(NOUN_DICT, 70)
    washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
    html_tags = ""
    for w in visual_samples:
        color = random.choice(washed_colors)
        html_tags += f'<span class="fragment-tag" style="background-color:{color};">{w}</span>'
    st.markdown(f'<div style="text-align:center;">{html_tags}</div>', unsafe_allow_html=True)
