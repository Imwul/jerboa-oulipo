import streamlit as st
from kiwipiepy import Kiwi
import requests
import random

# 페이지 설정
st.set_page_config(page_title="Jerboa Oulipo Engine", page_icon="🐦", layout="wide")

# --- 상태 저장소 ---
if "archive" not in st.session_state:
    st.session_state.archive = []

# --- 🎨 라이트 모드 & 을유1945 폰트 ---
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
</style>
""", unsafe_allow_html=True)

# --- 엔진 부품 ---
@st.cache_data(show_spinner=False)
def diagnostic_load():
    # 💡 최후의 보루 (비상용 단어장)
    base_dict = [
        "가방", "거울", "고독", "공백", "권태", "기억", "망각", "미학", 
        "시체", "심연", "악의", "오브제", "육체", "잔해", "파편", "향기", 
        "형식", "황금", "시간", "공간", "존재", "허무", "환상", "몽상"
    ]
    
    # 한국어 명사 리스트 깃허브 주소
    url = "https://raw.githubusercontent.com/naver/korean-wordlist/master/nouns.txt"
    
    raw_words = []
    try:
        res = requests.get(url, timeout=5, verify=False)
        # 💡 방어막 1: 서버가 '정상(200)' 응답을 줄 때만 텍스트를 읽음
        if res.status_code == 200:
            raw_words = res.text.split('\n')
        else:
            raw_words = base_dict
    except:
        raw_words = base_dict

    clean_words = []
    for w in raw_words:
        w = w.strip()
        # 💡 방어막 2: 철저한 필터링 (띄어쓰기 없고, 2~4글자)
        if 2 <= len(w) <= 4 and ' ' not in w:
            # 영어 404 에러 메시지가 섞이는 걸 막기 위해, 완벽한 '한글(가-힣)'만 허용
            if all(ord('가') <= ord(char) <= ord('힣') for char in w):
                clean_words.append(w)
                
    # 💡 방어막 3: 만약 통신 오류로 필터링된 단어가 10개도 안 남았다면 비상 식량 투입
    if len(clean_words) < 10:
        clean_words = base_dict
        
    final_dict = sorted(list(set(clean_words)))
    return final_dict
    # 완벽한 오리지널 S+7을 위해 '가나다순'으로 철저히 정렬
    final_dict = sorted(list(set(clean_words)))
    return final_dict

kiwi = load_kiwi()
with st.spinner("사전의 뼈대를 조립하는 중..."):
    NOUN_DICT = diagnostic_load()

# --- UI 레이아웃 ---
st.title("🐦 저보아: 무한 울리포 엔진")
st.caption(f"가나다순으로 엄격하게 정렬된 {len(NOUN_DICT):,}개의 순수 명사가 장전되었습니다.")

st.subheader("⚙️ 예술적 통제판")
col1, col2, col3 = st.columns(3)
with col1:
    shift_val = st.slider("사전 변조 거리 (S+N)", min_value=1, max_value=50, value=7)
with col2:
    bumpy_level = st.slider("활자의 진동 (크기)", min_value=0.0, max_value=0.8, value=0.2, step=0.05)
with col3:
    tilt_level = st.slider("활자의 비틀림 (각도)", min_value=0, max_value=30, value=5, step=1)

user_input = st.text_area("해부대에 올릴 문장을 입력해.", placeholder="나는 오늘 공원에서 사과를 먹었다.")

# --- 변환 로직 (오리지널 S+7) ---
def transform_engine(text, dictionary, shift):
    if not text.strip(): return "입력된 공백."
    tokens = kiwi.tokenize(text)
    result = []
    dict_len = len(dictionary)
    
    for t in tokens:
        if t.tag.startswith('N'):
            # 진짜 S+N: 현재 단어가 사전에 있으면 완벽하게 N번째 뒤의 단어로 이동
            if t.form in dictionary:
                idx = (dictionary.index(t.form) + shift) % dict_len
                new_word = dictionary[idx]
            else:
                # 사전에 없는 단어라도 해시를 이용해 규칙적으로 변환 (무작위성 통제)
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

# 파편이 너무 많으므로 무작위로 70개만 전시
visual_samples = random.sample(NOUN_DICT, min(70, len(NOUN_DICT)))
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]

html_tags = ""
for w in visual_samples:
    color = random.choice(washed_colors)
    font_size = 0.8 + (len(w) * 0.15)
    anim_delay = random.uniform(0, 3)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; font-size:{font_size}rem; animation: float 4s ease-in-out infinite; animation-delay: {anim_delay}s;">{w}</span>'

st.markdown(f'<div style="text-align:center;">{html_tags}</div>', unsafe_allow_html=True)
