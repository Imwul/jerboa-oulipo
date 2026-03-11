import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import random
import time
from concurrent.futures import ThreadPoolExecutor

# --- 1. 페이지 설정 및 상태 관리 ---
st.set_page_config(page_title="Jerboa Oulipo Engine", page_icon="🐦", layout="wide")

if "archive" not in st.session_state:
    st.session_state.archive = []

# --- 2. 🎨 디자인: 을유1945 폰트 & 강제 라이트 모드 (CSS) ---
st.markdown("""
<style>
    /* 1. 시스템 다크모드 완전 차단 및 라이트모드 고정 */
    :root { color-scheme: light !important; }
    
    /* 2. 전체 배경 및 글자색 강제 고정 (흰 배경, 검은 글자) */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        background-color: #FFFFFF !important;
        color: #111111 !important;
    }

    /* 3. 을유1945 폰트 적용 */
    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
        font-weight: normal; font-style: normal;
    }

    * {
        font-family: 'Eulyoo1945-Regular', serif !important;
        color: #111111 !important;
    }

    /* 4. 입력창 및 슬라이더 가독성 (다크모드에서도 보이게) */
    textarea, [data-testid="stMarkdownContainer"] p, .stSlider {
        color: #111111 !important;
    }
    textarea {
        background-color: #F8F9FA !important;
        border: 1px solid #DCDCDC !important;
    }

    /* 5. 🏗️ 금속 활자 버튼 (Metal Movable Type Style) */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 2px solid #111111 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #111111 !important;
        font-weight: bold !important;
        transition: all 0.1s;
    }
    div.stButton > button:hover {
        transform: translate(2px, 2px);
        box-shadow: 1px 1px 0px #111111 !important;
    }

    /* 6. 파편 태그 디자인 (Surrealist Fragments) */
    .fragment-tag {
        display: inline-block;
        padding: 6px 14px;
        margin: 6px;
        border-radius: 2px;
        background-color: #FDFDFD;
        border: 1px solid #E0E0E0;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 엔진 코어 부품 ---
@st.cache_resource
def load_kiwi():
    return Kiwi()

def fetch_words_final(kw, API_KEY):
    # 이물이 찾은 Swagger 명세 기반 최신 주소
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
    except:
        return []

@st.cache_data(show_spinner=False)
def get_oulipo_dictionary():
    API_KEY = "8f778621-2475-45d2-955c-c4dc91543917"
    keywords = ["사람", "마음", "하늘", "바다", "시간", "기억", "공간", "거울", "파편"]
    
    total_words = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for words in executor.map(lambda kw: fetch_words_final(kw, API_KEY), keywords):
            total_words.extend(words)
            
    final_dict = sorted(list(set(total_words)))
    
    # 💡 [예술적 안전망] 서버 연결 실패 시 가동될 니치한 단어장
    # 보들레르, 페렉, 키냐르의 세계관을 반영한 명사들
    FALLBACK_ART_DICT = [
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
        "흔적", "희망", "희곡", "권태", "몽상", "균열", "착각", "구속", "여로", "안부"
    ]
    
    if len(final_dict) < 20:
        return sorted(list(set(FALLBACK_ART_DICT))), "FALLBACK_ARTISTIC"
    return final_dict, "ONLINE_NEW"

# --- 4. 메인 화면 가동 ---
kiwi = load_kiwi()
with st.spinner("사전의 심연에서 파편을 채집하는 중..."):
    NOUN_DICT, load_mode = get_oulipo_dictionary()

st.title("🐦 저보아: NEW 울리포 엔진")

if load_mode == "FALLBACK_ARTISTIC":
    st.info("🌐 서버가 응답하지 않아 우리 서클만의 '예술적 단어장'을 장전했습니다.")
else:
    st.success(f"✅ 실시간 사전 연결 성공! {len(NOUN_DICT)}개의 파편이 준비되었습니다.")

st.divider()

# --- 5. 변환 인터페이스 ---
col_in, col_set = st.columns([2, 1])
with col_in:
    user_input = st.text_area("해부대에 올릴 문장을 입력해.", placeholder="나는 오늘 공원에서 사과를 먹었다.", height=150)
with col_set:
    shift_val = st.slider("사전 변조 거리 (S+N)", 1, 50, 7)
    st.caption("사전 속에서 명사를 N단계 뒤의 단어로 교체합니다.")
    bumpy_val = st.slider("활자의 진동 (크기)", 0.0, 0.5, 0.1)

if st.button("✨ 문장 재단 및 아카이빙"):
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
        
        # 결과 렌더링
        st.subheader("🖼️ 변환 결과")
        html_res = '<div style="line-height: 2.2; word-wrap: break-word;">'
        for char in transformed:
            fs = 1.4 + random.uniform(-bumpy_val, bumpy_val)
            html_res += f'<span style="font-size:{fs}rem; font-weight:bold;">{char}</span>'
        html_res += '</div>'
        st.markdown(html_res, unsafe_allow_html=True)
    else:
        st.warning("문장을 먼저 입력해줘.")

st.divider()

# --- 6. 아카이브 및 시각화 ---
col_log, col_del = st.columns([4, 1])
with col_log: st.subheader("📜 과거의 흔적")
with col_del: 
    if st.button("🗑️ 로그 삭제"):
        st.session_state.archive = []
        st.rerun()

if st.session_state.archive:
    for orig, trans in reversed(st.session_state.archive):
        st.markdown(f"<small style='color:#888;'>{orig}</small><br><b>{trans}</b>", unsafe_allow_html=True)
        st.caption("---")

st.divider()
st.subheader("🏺 현재 엔진의 파편들")
samples = random.sample(NOUN_DICT, min(50, len(NOUN_DICT)))
html_tags = "".join([f'<span class="fragment-tag">{w}</span>' for w in samples])
st.markdown(f'<div style="text-align:center;">{html_tags}</div>', unsafe_allow_html=True)
