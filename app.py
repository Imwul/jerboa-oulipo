import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import random
from concurrent.futures import ThreadPoolExecutor # 병렬 처리를 위한 부품

# 1. 페이지 설정
st.set_page_config(page_title="Jerboa Network Diagnostic", page_icon="🐦")

# 2. 엔진 시동 (Kiwi 및 데이터 로드)
@st.cache_resource
def load_kiwi_engine():
    return Kiwi()

# 단일 API 호출을 담당하는 함수
def fetch_words(kw, API_KEY):
    url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q={kw}&target=1&num=100&advanced=y&method=include"
    try:
        res = requests.get(url, timeout=5, verify=False)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            return [node.text.replace('-', '').replace('^', ' ') for node in root.findall('.//item/word') if node.text]
    except:
        return []
    return []

@st.cache_resource
def diagnostic_load():
    kiwi = load_kiwi_engine()
    base_dict = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파편", "공백", "소멸"]
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    keywords = ["오브제", "파편", "흔적", "심연", "거울", "그림자", "자동", "복제", "기계", "신체", "시선", "공백"]
    
    total_ext_words = []
    
    # 🚀 병렬 엔진 가동: 12개의 키워드를 동시에 요청함
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda kw: fetch_words(kw, API_KEY), keywords))
    
    for words in results:
        total_ext_words.extend(words)
        
    final_dict = sorted(list(set(base_dict + total_ext_words)))
    return kiwi, final_dict, f"✅ 초고속 로드 완료! ({len(final_dict)}개)"

# 데이터 불러오기
kiwi, NOUN_DICT, network_status = diagnostic_load()

# 3. UI 레이아웃
st.title("🐦 저보아: 무한 울리포 엔진")
st.sidebar.title("🔍 시스템 상태")
st.sidebar.write(network_status)

st.subheader("📝 텍스트 투입")
user_input = st.text_area("변환할 문장을 입력해봐.", placeholder="예: 나는 오늘 공원을 산책했다.")

# 4. 변환 엔진
def transform_engine(text, dictionary):
    tokens = kiwi.tokenize(text)
    result = []
    for t in tokens:
        if t.tag.startswith('N'):
            result.append(random.choice(dictionary))
        else:
            result.append(t.form)
    return kiwi.join(result)

# 5. 실행 버튼
if st.button("✨ 무한 울리포 엔진 가동"):
    if user_input:
        transformed = transform_engine(user_input, NOUN_DICT)
        st.subheader("🖼️ 변환된 결과")
        st.success(transformed)
    else:
        st.warning("먼저 문장을 입력해야 엔진을 돌릴 수 있어!")

# 6. 시각화 (파편의 벽)
# --- (이전 로직 동일: import, set_page_config, load_kiwi_engine) ---

def diagnostic_load():
    kiwi = load_kiwi_engine()
    base_dict = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파편", "공백", "소멸"]
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    keywords = ["오브제", "파편", "흔적", "심연", "거울", "그림자", "자동", "복제", "기계", "신체", "시선", "공백"]
    
    total_ext_words = []
    try:
        for kw in keywords:
            url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q={kw}&target=1&num=100&advanced=y&method=include"
            res = requests.get(url, timeout=10, verify=False)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                # 🛠️ 수리 1: ^ 기호를 공백으로 교체
                words = [node.text.replace('-', '').replace('^', ' ') for node in root.findall('.//item/word') if node.text]
                total_ext_words.extend(words)
        final_dict = sorted(list(set(base_dict + total_ext_words)))
        return kiwi, final_dict, f"✅ 성공! ({len(final_dict)}개 장전)"
    except Exception as e:
        return kiwi, base_dict, f"⚠️ 통신 장애: {str(e)}"

# 데이터 불러오기
kiwi, NOUN_DICT, network_status = diagnostic_load()

# --- (UI 레이아웃 및 transform_engine 동일) ---

# --- 🎨 4. 시각화: 파편의 심연 (Depth of Fragments) ---
st.divider()
st.subheader("🏺 746개의 파편들: 설치 미술 모드")
st.write("네 안목을 반영해 기호를 씻어내고, 색채의 다양성을 심었어. 클릭할 때마다 배치가 달라지지.")

# 746개 중 50개 랜덤 샘플
visual_samples = random.sample(NOUN_DICT, min(50, len(NOUN_DICT)))

# 🛠️ 수리 2: 무작위 심연 색상 생성 함수
def get_random_deep_color():
    # 어두운 색상 세트 (회색조, 숯색, 짙은 쑥색, 짙은 구리, 짙은 보라)
    deep_colors = [
        "#3a3f4a", "#2c3e50", "#444950", "#31433f", "#4f413a", "#4a3c5a"
    ]
    return random.choice(deep_colors)

# CSS를 활용해 무작위 색상의 태그 클라우드 만들기
st.markdown("""
    <style>
    .fragment-tag {
        display: inline-block;
        padding: 5px 12px;
        margin: 4px;
        border-radius: 20px;
        font-size: 0.9rem;
        color: #f1f3f5; /* 밝은 텍스트 */
        border: 1px solid #1f1f1f; /* 어두운 테두리 */
        transition: all 0.3s ease;
        opacity: 0.9;
    }
    .fragment-tag:hover {
        opacity: 1;
        transform: scale(1.1) rotate(2deg);
        box-shadow: 0 4px 10px rgba(0,0,0,0.5); /* 어두운 그림자 */
    }
    </style>
    """, unsafe_allow_html=True)

# HTML 태그 생성 (각 태그에 무작위 색상 할당)
fragment_html = "".join([f'<span class="fragment-tag" style="background-color:{get_random_deep_color()};">{word}</span>' for word in visual_samples])
st.markdown(fragment_html, unsafe_allow_html=True)

if st.button("♻️ 파편 재배치"):
    st.rerun()
