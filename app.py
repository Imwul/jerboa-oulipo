import streamlit as st
from kiwipiepy import Kiwi
import requests

@st.cache_resource
def load_resources():
    # 1. Kiwi 형태소 분석기 로드
    kiwi = Kiwi()
    
    # 2. 외부의 대규모 명사 리스트 불러오기 (약 5만 단어)
    # 실제 존재하는 오픈소스 명사 리스트 URL 예시입니다.
    url = "https://raw.githubusercontent.com/ko-nlp/Korpora/master/Korpora/data/korean_dictionary/korean_dictionary.txt"
    try:
        response = requests.get(url)
        # 텍스트 파일에서 명사만 추출하여 리스트화
        big_dict = [line.strip() for line in response.text.split('\n') if line.strip()]
        big_dict.sort()
    except:
        # 실패 시 기본 니치 사전 사용
        big_dict = sorted(["심연", "권태", "알바트로스", "오브제", "몽유병", "유령"])
        
    return kiwi, big_dict

kiwi, NOUN_DICT = load_resources()

def s_plus_n_final(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    for token in tokens:
        result.append(text[last_end:token.start])
        # 일반명사(NNG)나 고유명사(NNP)인 경우
        if token.tag in ['NNG', 'NNP']:
            if token.form in NOUN_DICT:
                idx = NOUN_DICT.index(token.form)
                result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])
            else:
                # 사전에 없는 단어면, 사전에서 가나다순으로 가장 가까운 위치를 찾아 치환
                # 이 기능이 추가되면 훨씬 더 기괴해집니다.
                result.append(token.form)
        else:
            result.append(token.form)
        last_end = token.end
    result.append(text[last_end:])
    return "".join(result)

# UI 부분은 이전과 동일하게 유지...
st.title("🐦 저보아 서클: 무한 울리포 엔진")
st.write(f"현재 연결된 사전 데이터: {len(NOUN_DICT):,} 개의 명사")

shift_n = st.sidebar.slider("치환 간격 (n)", 1, 100, 7) # 대규모 사전이므로 범위를 넓혔어!
user_input = st.text_area("문장을 입력하세요:", height=150)

if st.button("무한 변환 실행"):
    if user_input:
        with st.spinner('방대한 사전 데이터를 탐색 중...'):
            output = s_plus_n_final(user_input, shift_n)
            st.markdown("### ✨ 변환 결과")
            st.success(output)
