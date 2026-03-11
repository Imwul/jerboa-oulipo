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
    st.session_state.raw_xml = ""

# --- 2. 🎨 디자인 (CSS) ---
st.markdown("""
<style>
@font-face {
    font-family: 'Eulyoo1945-Regular';
    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    font-weight: normal; font-style: normal;
}
.stApp { background-color: #FFFFFF !important; }
html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #111111 !important; font-family: 'Eulyoo1945-Regular', serif !important;
}
.fragment-tag {
    display: inline-block; padding: 6px 14px; margin: 8px; border-radius: 4px;
    color: #222222 !important; border: 1px solid #dcdcdc;
}
div.stButton > button {
    background-color: #ffffff !important; color: #111111 !important;
    border: 2px solid #111111 !important; border-radius: 0px !important;
    box-shadow: 3px 3px 0px #111111 !important; font-weight: bold !important;
}
.debug-box {
    background-color: #f0f0f0; border: 1px dashed #ff0000; padding: 10px; font-family: monospace; font-size: 0.8rem; overflow: auto;
}
</style>
""", unsafe_allow_html=True)

# --- 3. 엔진 코어 부품 ---
@st.cache_resource
def load_kiwi():
    return Kiwi()

def fetch_words_new(kw, API_KEY):
    url = "http://api.kcisa.kr/openapi/service/rest/contents/getContents632"
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 50,
        "pageNo": 1,
        "keyword": kw
    }
    
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            # 💡 디버깅을 위해 생 XML 저장
            st.session_state.raw_xml = res.text[:800] 
            
            root = ET.fromstring(res.content)
            items = []
            
            # 💡 네임스페이스를 완전히 무시하고 모든 요소 순회
            for elem in root.iter():
                # 태그명에서 '{url}tag' 중 'tag'만 추출
                tag_name = elem.tag.split('}')[-1]
                
                # KCISA NEW API는 단어명을 title 혹은 word에 담음
                if tag_name in ['title', 'word']:
                    if elem.text:
                        # 괄호 및 부제 제거
                        w = elem.text.split('(')[0].strip().replace('-', '').replace('^', '')
                        # 2~4글자 순수 한글 필터
                        if 2 <= len(w) <= 4 and all(ord('가') <= ord(c) <= ord('힣') for c in w):
                            items.append(w)
            return items
        else:
            return []
    except:
        return []

@st.cache_data(show_spinner=False)
def diagnostic_load():
    API_KEY = "8f778621-2475-45d2-955c-c4dc91543917"
    # 수집 범위를 좁히되 확실한 키워드들
    keywords = ["가", "나", "다", "라", "마", "바", "사", "아", "자", "차", "카", "타", "파", "하"]
    
    total_words = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for words in executor.map(lambda kw: fetch_words_new(kw, API_KEY), keywords):
            total_words.extend(words)
            
    final_dict = sorted(list(set(total_words)))
    status = "success"
    
    # 실패 시 80개 초현실주의 비상 단어장
    base_dict = sorted([
        "거울", "파편", "심연", "공백", "권태", "기억", "망각", "미학", "시체", "악의",
        "오브제", "육체", "잔해", "향기", "형식", "황금", "시간", "공간", "존재", "허무",
        "환상", "몽상", "사람", "마음", "하루", "사랑", "친구", "세상", "이유", "생각",
        "바람", "하늘", "바다", "얼굴", "소리", "이야기", "노래", "마을", "도시", "나무",
        "우주", "역사", "미래", "과거", "눈물", "웃음", "약속", "여행", "사진", "그림",
        "새벽", "황혼", "노을", "구름", "별빛", "달빛", "햇살", "그림자", "골목", "계절",
        "침묵", "언어", "문장", "단어", "여백", "비밀", "거짓", "진실", "운명", "우연",
        "인연", "이별", "만남", "슬픔", "기쁨", "고독", "자유", "구속", "착각", "균열"
    ])
    
    if len(final_dict) < 20:
        status = "fallback"
        final_dict = base_dict
             
    return final_dict, status

# --- 4. 메인 화면 ---
kiwi = load_kiwi()

with st.spinner("NEW API의 네임스페이스를 해킹하는 중..."):
    NOUN_DICT, load_status = diagnostic_load()

st.title("🐦 저보아: NEW 울리포 엔진")

if load_status == "fallback":
    st.error("⚠️ NEW API에서 데이터를 찾지 못했습니다. 비상 단어장으로 가동합니다.")
    # 💡 서버가 보낸 날것의 데이터를 보여줌 (디버깅용)
    with st.expander("🔍 서버 응답 분석 (디버깅 정보)"):
        st.write("서버에서 받은 XML의 일부입니다. 단어가 어디 있는지 확인해보세요:")
        st.code(st.session_state.raw_xml, language="xml")
else:
    st.success(f"성공! 'NEW' 엔진이 {len(NOUN_DICT):,}개의 순수 명사를 발굴했습니다.")

st.divider()

# --- 5. 통제 및 변환 ---
col1, col2, col3 = st.columns(3)
with col1: shift_val = st.slider("사전 변조 거리 (S+N)", 1, 50, 7)
with col2: bumpy_level = st.slider("활자의 진동", 0.0, 0.8, 0.2)
with col3: tilt_level = st.slider("활자의 비틀림", 0, 30, 5)

user_input = st.text_area("해부대에 올릴 문장", placeholder="나는 오늘 공원에서 사과를 먹었다.")

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
visual_samples = random.sample(NOUN_DICT, min(70, len(NOUN_DICT)))
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
html_tags = "".join([f'<span class="fragment-tag" style="background-color:{random.choice(washed_colors)};">{w}</span>' for w in visual_samples])
st.markdown(f'<div style="text-align:center;">{html_tags}</div>', unsafe_allow_html=True)
