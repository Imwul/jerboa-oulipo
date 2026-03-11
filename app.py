import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET

# 1. 페이지 설정 (반드시 최상단)
st.set_page_config(page_title="Jerboa Network Diagnostic", page_icon="🐦")

# 2. Kiwi 엔진 로드 함수 (캐싱 처리)
@st.cache_resource
def load_kiwi_engine():
    try:
        return Kiwi()
    except Exception as e:
        st.error(f"Kiwi 로드 실패: {e}")
        return None

# 3. 메인 진단 및 단어 로드 함수
def diagnostic_load():
    kiwi = load_kiwi_engine()
    
    # 기본 단어장
    base_dict = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파편", "공백", "소멸"]
    
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    
    # ⚠️ 이 부분의 들여쓰기가 위 코드들과 일치해야 해!
    keywords = [
        "오브제", "파편", "흔적", "심연", "거울", "그림자", 
        "자동", "복제", "기계", "신체", "시선", "공백"
    ]
    
    total_ext_words = []

    try:
        for kw in keywords:
            # API 호출 시 num=100으로 최대치 확보
            url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q={kw}&target=1&num=100&advanced=y&method=include"
            res = requests.get(url, timeout=10, verify=False)
            
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                words = [node.text.replace('-', '') for node in root.findall('.//item/word') if node.text]
                total_ext_words.extend(words)
        
        final_dict = sorted(list(set(base_dict + total_ext_words)))
        status = f"✅ 성공! (총 {len(final_dict)}개 장전)"
        return kiwi, final_dict, status

    except Exception as e:
        return kiwi, base_dict, f"⚠️ 통신 장애: {str(e)}"

# --- 실행부 ---
kiwi, NOUN_DICT, network_status = diagnostic_load()

st.title("🐦 저보아: 무한 울리포 엔진")

# 사이드바 상태 표시
if "✅" in network_status:
    st.sidebar.success(network_status)
else:
    st.sidebar.warning(network_status)

st.write(f"현재 장전된 단어: **{len(NOUN_DICT):,}개**")

# 만약 단어가 너무 적으면 경고창 띄우기
if len(NOUN_DICT) < 50:
    st.info("단어 공급이 원활하지 않습니다. '저보아 서클'의 창의성이 위험합니다!")

# 확인용 리스트 (일부만)
with st.expander("장전된 단어 샘플 보기"):
    st.write(", ".join(NOUN_DICT[:50]) + " ...")

import random

# --- (이전 로직 생략: kiwi, NOUN_DICT, network_status가 정의된 상태) ---

st.divider() # 시각적 구분선

# 🎨 1. 입력창: 사용자의 '텍스트 오브제'를 받는 곳
st.subheader("📝 텍스트 투입")
user_input = st.text_area(
    "변환할 문장을 입력해봐 (예: 나는 오늘 공원을 산책하며 사과를 먹었다.)",
    placeholder="여기에 문장을 입력하면 저보아가 해부해줄 거야...",
    height=150
)

# ⚙️ 2. 변환 로직: 명사만 추출해서 교체
def transform_engine(text, dictionary):
    if not text.strip():
        return "입력된 문장이 없네, 이물. 공백은 '울리포'의 적이야."
    
    # Kiwi로 형태소 분석
    tokens = kiwi.tokenize(text)
    result = []
    
    for t in tokens:
        # NN(명사) 계열의 태그를 가진 단어만 교체
        if t.tag.startswith('N'):
            new_word = random.choice(dictionary)
            # 원본 단어와 교체된 단어가 같으면 한 번 더 섞기
            if new_word == t.form and len(dictionary) > 1:
                new_word = random.choice(dictionary)
            result.append(new_word)
        else:
            result.append(t.form)
            
    # 형태소들을 자연스럽게 다시 합치기 (kiwi.join 활용)
    return kiwi.join(result)

# 🚀 3. 변환 버튼 및 결과 출력
if st.button("✨ 무한 울리포 엔진 가동"):
    if user_input:
        with st.spinner("단어 파편들을 재조립하는 중..."):
            transformed_text = transform_engine(user_input, NOUN_DICT)
            
            st.subheader("🖼️ 변환된 결과")
            st.success(transformed_text)
            
            # 설치 미술적인 느낌을 주기 위한 인용구 스타일
            st.info(f"💡 이 문장에는 {len(NOUN_DICT)}개의 파편 중 일부가 무작위로 침투했어.")
    else:
        st.warning("
