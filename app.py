import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import random
import time

# --- 1. 다크모드 박살내기 & 시각 복구 (CSS) ---
st.set_page_config(page_title="Jerboa Oulipo", layout="wide")

st.markdown("""
<style>
    /* 시스템 설정을 무시하고 강제로 화이트 테마 적용 */
    :root { color-scheme: light !important; }
    .stApp { background-color: white !important; }
    
    /* 모든 글자를 진한 검정색으로 고정 */
    h1, h2, h3, p, span, div, label, .stMarkdown {
        color: #111111 !important;
        font-family: sans-serif !important;
    }
    
    /* 입력창 배경과 글자색 대비 강화 */
    textarea {
        background-color: #f0f2f6 !important;
        color: #111111 !important;
    }
    
    /* 버튼 디자인 */
    div.stButton > button {
        background-color: white !important;
        color: black !important;
        border: 2px solid black !important;
        box-shadow: 4px 4px 0px black !important;
    }
    
    /* 디버깅 로그 박스 */
    .debug-box {
        background-color: #fff3cd;
        padding: 15px;
        border: 1px solid #ffeeba;
        color: #856404 !important;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. 엔진 부품 ---
@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

# --- 3. 데이터 수집 로직 (명세서 기반) ---
@st.cache_data(show_spinner=False)
def fetch_master_words():
    # 스크린샷에 나온 정확한 API 키와 URL
    API_KEY = "8f778621-2475-45d2-955c-c4dc91543917"
    URL = "https://api.kcisa.kr/openapi/API_SOP_027/request"
    
    # 명세서에 나온 대로 딱 필요한 인자만 구성
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 100,
        "pageNo": 1
    }
    
    try:
        # 💡verify=False를 빼고 정식 https 통신 시도
        res = requests.get(URL, params=params, timeout=10)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            words = []
            # 명세서 설명에 나온 '단어명'은 보통 <title> 태그에 담김
            for item in root.findall('.//item'):
                title = item.find('title')
                if title is not None and title.text:
                    w = title.text.split('(')[0].strip()
                    if 2 <= len(w) <= 4 and all(ord('가') <= ord(c) <= ord('힣') for c in w):
                        words.append(w)
            return sorted(list(set(words))), "SUCCESS", res.url
        return [], f"ERROR_{res.status_code}", res.url
    except Exception as e:
        return [], "EXCEPTION", str(e)

# --- 4. 메인 화면 ---
st.title("🐦 저보아: 명세서 정밀 타격 엔진")

# 데이터 로딩
with st.spinner("명세서의 경로를 따라 사전 데이터를 긁어오는 중..."):
    NOUN_DICT, status, target_url = fetch_master_words()

# 💡 만약 데이터가 없으면 비상 단어장 가동
if not NOUN_DICT:
    st.warning("⚠️ API에서 단어를 가져오지 못했습니다. 비상용 초현실 단어장을 가동합니다.")
    NOUN_DICT = sorted(["거울", "파편", "심연", "공백", "권태", "기억", "망각", "미학", "시체", "악의", "오브제", "육체", "잔해", "향기", "형식", "황금", "시간", "공간", "존재", "허무", "환상", "몽상", "사람", "마음", "하루", "사랑", "친구", "세상", "이유", "생각", "바람", "하늘", "바다", "얼굴", "소리", "이야기", "노래", "나무"])
    
    with st.expander("🔍 개발자용 디버깅 정보 (문제가 생기면 여기를 확인!)"):
        st.write("**요청 결과:**", status)
        st.write("**시도한 주소:**", target_url)
        st.info("위 주소를 복사해서 브라우저 주소창에 직접 넣어보세요. XML이 나오는지 확인이 필요합니다.")
else:
    st.success(f"✅ 명세서대로 {len(NOUN_DICT)}개의 순수 명사를 성공적으로 장전했습니다!")

st.divider()

# --- 5. 변환 인터페이스 ---
user_input = st.text_area("해부대에 올릴 문장을 입력해.", placeholder="나는 오늘 공원에서 사과를 먹었다.")
shift_val = st.slider("사전 변조 거리 (S+N)", 1, 50, 7)

if st.button("✨ 문장 재단하기"):
    if user_input:
        tokens = kiwi.tokenize(user_input)
        result = []
        d_len = len(NOUN_DICT)
        for t in tokens:
            if t.tag.startswith('N'):
                # S+N 로직
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
        st.subheader("🖼️ 결과")
        st.markdown(f"### {transformed}")
    else:
        st.error("문장을 입력해야 해!")

# --- 6. 시각화 (파편들) ---
st.divider()
st.subheader("🏺 사전의 파편들")
st.write(", ".join(random.sample(NOUN_DICT, min(50, len(NOUN_DICT)))))
