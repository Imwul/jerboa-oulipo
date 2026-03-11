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
if "raw_xml" not in st.session_state:
    st.session_state.raw_xml = "아직 수집된 데이터가 없습니다."

# --- 2. 🎨 시각적 가독성 완전 정복 CSS ---
st.markdown("""
<style>
/* 1. 시스템 다크모드 무시 및 라이트모드 강제 */
:root { color-scheme: light !important; }

/* 2. 전체 배경과 모든 텍스트 색상 강제 (흰 배경, 검은 글자) */
[data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
    background-color: #FFFFFF !important;
    color: #111111 !important;
}

/* 3. 폰트 및 공통 글자색 */
@font-face {
    font-family: 'Eulyoo1945-Regular';
    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
}

* {
    font-family: 'Eulyoo1945-Regular', serif !important;
    color: #111111 !important;
}

/* 4. 에러 메시지 상자 가독성 (분홍 배경, 검은 글자) */
[data-testid="stNotification"] {
    background-color: #FFE4E1 !important;
    color: #111111 !important;
    border: 1px solid #FFC0CB !important;
}

/* 5. 💡 코드 블록(st.code) 시인성 확보 (밝은 배경으로 강제) */
[data-testid="stCodeBlock"], code, pre {
    background-color: #F8F9FA !important;
    color: #CC0000 !important; /* XML 태그는 붉은색 계열로 도드라지게 */
    border: 1px solid #E9ECEF !important;
}

/* 6. 익스펜더(st.expander) 내부 색상 */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DCDCDC !important;
}

/* 7. 입력창 및 슬라이더 */
textarea, [data-testid="stMarkdownContainer"] p {
    color: #111111 !important;
}

/* 8. 버튼 디자인 */
div.stButton > button {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 2px solid #111111 !important;
    box-shadow: 3px 3px 0px #111111 !important;
}

/* 9. 파편 태그 */
.fragment-tag {
    display: inline-block;
    padding: 6px 14px;
    margin: 8px;
    border-radius: 4px;
    background-color: #F0F2F6;
    border: 1px solid #dcdcdc;
    color: #111111 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 3. 엔진 코어 부품 ---
@st.cache_resource
def load_kiwi():
    return Kiwi()

def fetch_words_new(kw, API_KEY):
    # KCISA NEW API 엔드포인트
    url = "http://api.kcisa.kr/openapi/service/rest/contents/getContents632"
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 40,
        "pageNo": 1,
        "keyword": kw
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            # 원본 XML 저장 (디버깅용)
            st.session_state.raw_xml = res.text[:1000]
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
        return []
    except Exception as e:
        st.session_state.raw_xml = f"통신 에러 발생: {str(e)}"
        return []

@st.cache_data(show_spinner=False)
def diagnostic_load():
    API_KEY = "8f778621-2475-45d2-955c-c4dc91543917"
    keywords = ["가", "나", "다", "라", "마", "바", "사", "아", "자", "차"]
    
    total_words = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for words in executor.map(lambda kw: fetch_words_new(kw, API_KEY), keywords):
            total_words.extend(words)
            
    final_dict = sorted(list(set(total_words)))
    status = "success"
    
    if len(final_dict) < 20:
        status = "fallback"
        final_dict = sorted([
            "거울", "파편", "심연", "공백", "권태", "기억", "망각", "미학", "시체", "악의",
            "오브제", "육체", "잔해", "향기", "형식", "황금", "시간", "공간", "존재", "허무",
            "환상", "몽상", "사람", "마음", "하루", "사랑", "친구", "세상", "이유", "생각",
            "바람", "하늘", "바다", "얼굴", "소리", "이야기", "노래", "마을", "도시", "나무"
        ])
    return final_dict, status

# --- 4. 메인 화면 ---
kiwi = load_kiwi()
with st.spinner("사전 데이터를 정밀 분석 중..."):
    NOUN_DICT, load_status = diagnostic_load()

st.title("🐦 저보아: NEW 울리포 엔진")

if load_status == "fallback":
    st.error("⚠️ NEW API 데이터 수집 실패. 비상 단어장으로 가동 중입니다.")
    with st.expander("🔍 서버 응답 분석 (이 내용을 확인해줘!)"):
        st.write("서버에서 받은 XML 원본입니다:")
        # 💡 배경색과 글자색이 강제된 코드 블록
        st.code(st.session_state.raw_xml, language="xml")
else:
    st.success(f"성공! 'NEW' 엔진이 {len(NOUN_DICT):,}개의 순수 명사를 발굴했습니다.")

st.divider()

# --- 5. 통제 및 변환 ---
col1, col2, col3 = st.columns(3)
with col1: shift_val = st.slider("사전 변조 거리 (S+N)", 1, 50, 7)
with col2: bumpy_level = st.slider("활자의 진동", 0.0, 0.8, 0.2)
with col3: tilt_level = st.slider("활자의 비틀림", 0, 30, 5)

user_input = st.text_area("해부대에 올릴 문장", placeholder="여기에 텍스트를 넣으세요.")

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
        if char == ' ': html += '&nbsp;'
        else:
            fs = 1.3 + random.uniform(-b_level, b_level)
            tilt = random.uniform(-t_level, t_level)
            html += f'<span style="font-size:{fs}rem; transform:rotate({tilt}deg); display:inline-block; font-weight:bold;">{char}</span>'
    html += '</div>'
    return html

if st.button("✨ 문장 재단하기"):
    if user_input:
        transformed = transform_engine(user_input, NOUN_DICT, shift_val)
        st.session_state.archive.append((user_input, transformed))
        st.markdown(render_styled_text(transformed, bumpy_level, tilt_level), unsafe_allow_html=True)

st.divider()

# --- 6. 아카이브 및 시각화 ---
st.subheader("🏺 사전의 파편들")
visual_samples = random.sample(NOUN_DICT, min(40, len(NOUN_DICT)))
html_tags = "".join([f'<span class="fragment-tag">{w}</span>' for w in visual_samples])
st.markdown(f'<div style="text-align:center;">{html_tags}</div>', unsafe_allow_html=True)
