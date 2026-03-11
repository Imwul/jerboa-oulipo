import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import random
from concurrent.futures import ThreadPoolExecutor

# 페이지 설정
st.set_page_config(page_title="Jerboa Oulipo Engine", page_icon="🐦", layout="wide")

# --- 상태 저장소 (아카이빙용) ---
if "archive" not in st.session_state:
    st.session_state.archive = []

# --- 폰트 및 라이트 모드 CSS ---
# 눈누에서 제공하는 을유1945 웹 폰트를 불러오고 자간을 -3%(-0.03em)로 줄임
st.markdown("""
<style>
@font-face {
    font-family: 'Eulyoo1945-Regular';
    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    font-weight: normal;
    font-style: normal;
}
html, body, [class*="css"]  {
    font-family: 'Eulyoo1945-Regular', serif;
    letter-spacing: -0.03em;
}
/* 라이트 모드 강제 적용 느낌 (스트림릿 테마가 다크여도 밝게 보이도록 일부 조정) */
.fragment-tag {
    display: inline-block;
    padding: 6px 14px;
    margin: 8px;
    border-radius: 4px;
    color: #333333; /* 글자는 진하게 */
    border: 1px solid #e0e0e0;
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
</style>
""", unsafe_allow_html=True)

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
            words = [node.text.replace('-', '').replace('^', '') for node in root.findall('.//item/word') if node.text]
            # 복합명사 배제를 위해 글자수 2~3자로 타이트하게 제한하고 띄어쓰기 철저히 배제
            return [w for w in words if ' ' not in w and 2 <= len(w) <= 3 and w.isalpha()]
    except: return []
    return []

@st.cache_data(show_spinner=False)
def diagnostic_load():
    base_dict = ["심연", "권태", "우울", "시체", "황금", "오브제", "거울", "파편", "공백", "소멸", "고독", "잔해", "악의", "관음", "육체"]
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    # 데이터베이스 대폭 확장 (단어 풀을 다양하게)
    keywords = ["예술", "파편", "거울", "그림자", "자동", "복제", "기계", "신체", "시선", "공백", "권태", "우울", "시체", "향기", "황금", "기억", "망각", "미학", "구조", "형식", "본질", "환상"]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda kw: fetch_words(kw, API_KEY), keywords))
    
    total = [w for sub in results for w in sub]
    final_dict = list(set(base_dict + total))
    # 💡 치명적 오류 수정: 정렬(가나다순)을 버리고 무작위로 섞어버림!
    random.shuffle(final_dict) 
    return final_dict

kiwi = load_kiwi()
with st.spinner("사전을 해체하고 재조립하는 중..."):
    NOUN_DICT = diagnostic_load()

# --- UI 레이아웃 ---
st.title("🐦 저보아: 무한 울리포 엔진")
st.caption(f"가나다순의 족쇄를 풀고 {len(NOUN_DICT)}개의 파편이 무작위로 흩어졌습니다.")

st.subheader("⚙️ 예술적 통제판")
col1, col2, col3 = st.columns(3)
with col1:
    shift_val = st.slider("사전 변조 거리 (S+N)", min_value=1, max_value=50, value=7)
with col2:
    bumpy_level = st.slider("활자의 진동 (크기)", min_value=0.0, max_value=0.8, value=0.2, step=0.05)
with col3:
    tilt_level = st.slider("활자의 비틀림 (각도)", min_value=0, max_value=30, value=5, step=1)

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

# 글자를 흔들고 틸트(기울기)를 주는 렌더러
def render_bumpy_text(text, b_level, t_level):
    html = '<div style="font-family: \'Eulyoo1945-Regular\', serif; line-height: 2; word-wrap: break-word; color:#2c3e50;">'
    for char in text:
        if char == ' ':
            html += '&nbsp;'
            continue
        fs = 1.2 + random.uniform(-b_level, b_level)
        tilt = random.uniform(-t_level, t_level)
        html += f'<span style="font-size: {fs}rem; transform: rotate({tilt}deg); display:inline-block; transition: all 0.2s;">{char}</span>'
    html += '</div>'
    return html

if st.button("✨ 문장 재단 및 아카이빙"):
    if user_input:
        transformed = transform_engine(user_input, NOUN_DICT, shift_val)
        st.session_state.archive.append((user_input, transformed))
        
        st.subheader("🖼️ 변환된 결과")
        # 실시간 슬라이더 값 반영 (크기 진동과 각도 비틀림)
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
        st.markdown(f"<span style='color:#888888; font-size:0.85rem;'>{orig}</span><br><b style='color:#333; font-size:1.1rem;'>{trans}</b>", unsafe_allow_html=True)
        st.caption("---")
else:
    st.info("아직 쌓인 흔적이 없어.")

st.divider()

# --- 시각화: 물 빠진 원색 파편들 ---
st.subheader(f"🏺 {len(NOUN_DICT)}개의 파편들")

visual_samples = random.sample(NOUN_DICT, min(70, len(NOUN_DICT)))

# 물 빠진 원색 (파스텔 톤 계열)
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]

html_tags = ""
for w in visual_samples:
    color = random.choice(washed_colors)
    font_size = 0.8 + (len(w) * 0.15)
    anim_delay = random.uniform(0, 3)
    
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; font-size:{font_size}rem; animation: float 4s ease-in-out infinite; animation-delay: {anim_delay}s;">{w}</span>'

st.markdown(f'<div style="text-align:center;">{html_tags}</div>', unsafe_allow_html=True)
