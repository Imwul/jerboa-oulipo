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
         fallback_url = "https://
