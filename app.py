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

# --- 2. 🎨 캔버스 디자인: 애니메이션 & 비틀림 (CSS) ---
st.markdown("""
<style>
    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    * { font-family: 'Eulyoo1945-Regular', serif !important; }

    /* 🌊 유령처럼 떠다니는 애니메이션 정의 */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(1deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    /* 🏷️ 파편 태그 스타일 (다채로운 색상 적용 예정) */
    .fragment-tag {
        display: inline-block;
        padding: 8px 16px;
        margin: 10px;
        border-radius: 4px;
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 2px 4px 10px rgba(0,0,0,0.05);
        animation: float 4s ease-in-out infinite;
        transition: all 0.3s;
        cursor: crosshair;
    }
    .fragment-tag:hover {
        transform: scale(1.2) rotate(-5deg) !important;
        z-index: 100;
    }

    /* 금속 활자 버튼 */
    div.stButton > button {
        background-color: #ffffff !important;
        border: 2px solid #111111 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #111111 !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 엔진 코어 ---
@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

def fetch_words_new(kw, API_KEY):
    url = "http://api.kcisa.kr/openapi/service/rest/contents/getContents632"
    params = {"serviceKey": API_KEY, "numOfRows": 40, "keyword": kw}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
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
    except: return []

@st.cache_data(show_spinner=False)
def get_oulipo_dictionary():
    API_KEY = "8f778621-2475-45d2-955c-c4dc91543917"
    keywords = ["사람", "마음", "하늘", "시간", "기억", "공간", "거울", "파편", "심연"]
    total_words = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for words in executor.map(lambda kw: fetch_words_new(kw, API_KEY), keywords):
            total_words.extend(words)
    final_dict = sorted(list(set(total_words)))
    
    FALLBACK_DICT = sorted([
        "가면", "가구", "거리", "거울", "결말", "경계", "고독", "공백", "과거", "관념", 
        "광장", "궤도", "귀신", "그림", "그늘", "기억", "노을", "눈물", "느낌", "단어", 
        "달빛", "대화", "도시", "동화", "모습", "모서리", "무지개", "미로", "미래", "미학", 
        "바다", "바람", "배경", "백색", "별빛", "변화", "비밀", "사물", "사과", "사진", 
        "상상", "상처", "새벽", "생각", "생명", "세계", "세상", "소리", "소설", "순간", 
        "시계", "시간", "시선", "시체", "시작", "심장", "심연", "악의", "안개", "어둠", 
        "얼굴", "언어", "여백", "여행", "역사", "영혼", "오브제", "오후", "온도", "우주", 
        "우연", "운명", "웃음", "위치", "유리", "유령", "육체", "이름", "이유", "이별", 
        "이야기", "인연", "인간", "일기", "입술", "자루", "자유", "잔해", "장면", "장소", 
        "재회", "저녁", "전부", "전설", "절벽", "조각", "존재", "종이", "중심", "지도", 
        "지식", "직업", "질문", "차이", "찰나", "창문", "채집", "책방", "처음", "천사", 
        "철학", "초상", "추억", "축제", "출구", "침묵", "태양", "파도", "파편", "평화", 
        "표정", "풍경", "하늘", "하루", "햇살", "행복", "향기", "허무", "현실", "혈관", 
        "형식", "형태", "혜성", "호수", "혼란", "화가", "화분", "환상", "황금", "황혼", 
        "흔적", "희망", "희곡", "권태", "몽상", "균열", "착각", "구속"
    ])
    
    if len(final_dict) < 20: return FALLBACK_DICT, "FALLBACK"
    return final_dict, "ONLINE"

# --- 4. 메인 화면 ---
kiwi = load_kiwi()
with st.spinner("사전의 심연에서 움직이는 파편들을 채집 중..."):
    NOUN_DICT, load_mode = get_oulipo_dictionary()

st.title("🐦 저보아: 무한 울리포 엔진")
st.caption(f"사전에서 추출한 {len(NOUN_DICT):,}개의 명사가 장전되었습니다.")

# --- 5. 변환 및 통제판 ---
col_in, col_set = st.columns([2, 1])
with col_in:
    user_input = st.text_area("해부대에 올릴 문장을 입력해.", placeholder="나는 오늘 공원에서 사과를 먹었다.", height=150)
with col_set:
    shift_val = st.slider("사전 변조 거리 (S+N)", 1, 50, 7)
    bumpy_val = st.slider("활자의 진동 (크기)", 0.0, 0.5, 0.2)
    tilt_val = st.slider("활자의 비틀림 (각도)", 0, 30, 10)

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
            else:
                result.append((t.form, t.tag))
        
        transformed = kiwi.join(result)
        st.session_state.archive.append((user_input, transformed))
        
        # 💡 [복구] 비틀리고 진동하는 텍스트 렌더링
        st.subheader("🖼️ 변환 결과")
        html_res = '<div style="line-height: 2.5; word-wrap: break-word; padding: 20px;">'
        for char in transformed:
            if char == ' ':
                html_res += '&nbsp;'
                continue
            fs = 1.5 + random.uniform(-bumpy_val, bumpy_val)
            rot = random.uniform(-tilt_val, tilt_val)
            html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold;">{char}</span>'
        html_res += '</div>'
        st.markdown(html_res, unsafe_allow_html=True)

st.divider()

# --- 6. 아카이브 및 🏺 떠다니는 파편들 ---
if st.session_state.archive:
    with st.expander("📜 과거의 흔적 보기"):
        for orig, trans in reversed(st.session_state.archive):
            st.markdown(f"<small>{orig}</small><br><b>{trans}</b>", unsafe_allow_html=True)
            st.caption("---")

st.subheader("🏺 사전의 파편들")
# 💡 [복구] 파스텔톤 색상과 float 애니메이션이 적용된 단어들
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
samples = random.sample(NOUN_DICT, min(60, len(NOUN_DICT)))

html_tags = '<div style="text-align:center; padding: 40px 0;">'
for i, w in enumerate(samples):
    color = random.choice(washed_colors)
    delay = random.uniform(0, 4)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; animation-delay: {delay}s;">{w}</span>'
html_tags += '</div>'

st.markdown(html_tags, unsafe_allow_html=True)
