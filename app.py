import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import random

# 1. 페이지 설정
st.set_page_config(page_title="Jerboa Network Diagnostic", page_icon="🐦")

# 2. 엔진 시동 (Kiwi 및 데이터 로드)
@st.cache_resource
def load_kiwi_engine():
    try:
        return Kiwi()
    except Exception as e:
        st.error(f"Kiwi 로드 실패: {e}")
        return None

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
                words = [node.text.replace('-', '') for node in root.findall('.//item/word') if node.text]
                total_ext_words.extend(words)
        final_dict = sorted(list(set(base_dict + total_ext_words)))
        return kiwi, final_dict, f"✅ 성공! ({len(final_dict)}개 장전)"
    except Exception as e:
        return kiwi, base_dict, f"⚠️ 통신 장애: {str(e)}"

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
st.divider()
st.subheader("🏺 746개의 파편들: 설치 미술 모드")
visual_samples = random.sample(NOUN_DICT, min(50, len(NOUN_DICT)))
fragment_html = "".join([f'<span style="display:inline-block; padding:5px 12px; margin:4px; background-color:#f0f2f6; border-radius:20px; font-size:0.9rem; border:1px solid #d1d5db;">{word}</span>' for word in visual_samples])
st.markdown(fragment_html, unsafe_allow_html=True)
