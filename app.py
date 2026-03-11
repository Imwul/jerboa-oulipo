import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import random
from concurrent.futures import ThreadPoolExecutor

# 페이지 설정 (반드시 최상단)
st.set_page_config(page_title="Jerboa Oulipo Engine", page_icon="🐦", layout="wide")

# --- 상태 저장소 (아카이빙용) ---
if "archive" not in st.session_state:
    st.session_state.archive = []

# --- 엔진 부품 ---
@st.cache_resource
def load_kiwi():
    return Kiwi()

def fetch_words(kw, API_KEY):
    url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q={kw}&target=1&num=100&advanced=y&method=include"
    try:
        res = requests.get(url, timeout=3, verify=False)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            # 기호 제거
            words = [node.text.replace('-', '').replace('^', '') for node in root.findall('.//item/word') if node.text]
            # 💡 이물의 지시: 띄어쓰기 없고 4글자 이하인 깔끔한 단어만 추출!
            return [w for w in words if ' ' not in w and len(w) <= 4]
    except: return []
    return []

# 캐시 데이터를 써서 로딩 속도를 극한으로 끌어올림
@st.cache_data(show_spinner=False)
def diagnostic_load():
    base_dict = ["심연", "권태", "우울", "시체", "황금", "피", "오브제", "거울", "파편", "공백", "소멸", "고독", "잔해", "악의", "꽃", "관음", "육체"]
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    # 키워드를 대폭 늘려서 데이터베이스 확장
    keywords = ["예술", "파편", "흔적", "거울", "그림자", "자동", "복제", "기계", "신체", "시선", "공백", "권태", "우울", "시체", "꽃", "향기", "황금", "피", "잔해", "기억"]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda kw: fetch_words(kw, API_KEY), keywords))
    
    total = [w for sub in results for w in sub]
    final_dict = sorted(list(set(base_dict + total)))
    return final_dict

kiwi = load_kiwi()
with st.spinner("엔진 예열 및 단어 정제 중..."):
    NOUN_DICT = diagnostic_load()

# --- UI 레이아웃 ---
st.title("🐦 저보아: 무한 울리포 엔진")
st.caption(f"현재 {len(NOUN_DICT)}개의 정제된 단어가 장전되었습니다.")

st.subheader("⚙️ 예술적 통제판")
col1, col2 = st.columns(2)
with col1:
    shift_val = st.slider("사전 변조 거리 (S+N)", min_value=1, max_value=50, value=7)
with col2:
    bumpy_level = st.slider("활자의 진동(울룩불룩) 강도", min_value=0.0, max_value=0.5, value=0.15, step=0.05)

user_input = st.text_area("해부대에 올릴 문장을 입력해.", placeholder="나는 오늘 공원을 거닐며 사과를 베어 물었다.")

# --- 변환 로직 ---
def transform_engine(text, dictionary, shift):
    if not text.strip(): return "입력된 공백."
    tokens = kiwi.tokenize(text)
    result = []
    for t in tokens:
        if t.tag.startswith('N'):
            if t.form in dictionary:
                idx = (dictionary.index(t.form) + shift) % len(dictionary)
                new_word = dictionary[idx]
            else:
                random.seed(hash(t.form))
                new_word = random.choice(dictionary)
            result.append((new_word, 'NNG'))
        else:
            result.append((t.form, t.tag))
    return kiwi.join(result)

# 글자를 미세하게 흔들어주는 시각 효과 함수
def render_bumpy_text(text, level):
    html = '<div style="line-height: 2; word-wrap: break-word;">'
    for char in text:
        if char == ' ':
            html += '&nbsp;'
            continue
        # 기준 폰트 1.2rem에 강도만큼 무작위 진동 부여
        fs = 1.2 + random.uniform(-level, level)
        html += f'<span style="font-size: {fs}rem; display:inline-block; transition: all 0.2s;">{char}</span>'
    html += '</div>'
    return html

if st.button("✨ 엔진 가동 및 아카이빙"):
    if user_input:
        transformed = transform_engine(user_input, NOUN_DICT, shift_val)
        # 과거의 흔적에 기록
        st.session_state.archive.append((user_input, transformed))
        
        st.subheader("🖼️ 변환된 결과")
        st.markdown(render_bumpy_text(transformed, bumpy_level), unsafe_allow_html=True)
    else:
        st.warning("문장을 먼저 입력해야 해.")

st.divider()

# --- 아카이브: 과거의 흔적 ---
if st.session_state.archive:
    st.subheader("📜 과거의 흔적 (공동 시집)")
    for orig, trans in reversed(st.session_state.archive):
        st.markdown(f"<span style='color:gray; font-size:0.9rem;'>{orig}</span><br><b>{trans}</b>", unsafe_allow_html=True)
        st.caption("---")

st.divider()

# --- 시각화: 보들레르의 심연 ---
st.subheader(f"🏺 {len(NOUN_DICT)}개의 파편들: 설치 미술 모드")

# 화면이 꽉 차지 않게 60개만 샘플링
visual_samples = random.sample(NOUN_DICT, min(60, len(NOUN_DICT)))

# 보들레르의 색조: 칠흑, 금빛, 핏빛
baudelaire_colors = ["#111111", "#1A1A1A", "#8A0303", "#660000", "#D4AF37", "#C5B358", "#3b0000"]

# 떠다니는 애니메이션 CSS
css = """
<style>
@keyframes float {
    0% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-8px) rotate(1deg); }
    100% { transform: translateY(0px) rotate(0deg); }
}
.fragment-tag {
    display: inline-block;
    padding: 6px 14px;
    margin: 8px;
    border-radius: 4px; /* 살짝 날카로운 예술적 마감 */
    color: #f1f3f5;
    border: 1px solid #222;
    box-shadow: 2px 4px 10px rgba(0,0,0,0.6);
}
.fragment-tag:hover {
    transform: scale(1.15) !important;
    opacity: 1 !important;
    z-index: 10;
    cursor: crosshair;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

html_tags = ""
for w in visual_samples:
    color = random.choice(baudelaire_colors)
    # 💡 이물의 지시: 글자 수에 따라 폰트 크기를 다르게!
    font_size = 0.7 + (len(w) * 0.2) 
    # 각 단어마다 떠오르는 타이밍을 무작위로 주어 불규칙하게 떠다니게 함
    anim_delay = random.uniform(0, 4)
    
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; font-size:{font_size}rem; animation: float 4s ease-in-out infinite; animation-delay: {anim_delay}s;">{w}</span>'

st.markdown(f'<div style="text-align:center;">{html_tags}</div>', unsafe_allow_html=True)
