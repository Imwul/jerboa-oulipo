import streamlit as st
import time

# 1. 페이지 설정 (가장 먼저 와야 해!)
st.set_page_config(page_title="Jerboa Oulipo Machine", page_icon="🐦")

st.title("🐦 저보아 서클: 울리포 머신")
st.write("로딩 중입니다... 잠시만 기다려 주세요.")

# 2. 라이브러리 로드 체크
try:
    from kiwipiepy import Kiwi
    st.success("✅ 엔진(Kiwi) 로드 성공!")
except Exception as e:
    st.error(f"❌ 엔진 로드 실패: {e}")
    st.stop()

# 3. 모델 초기화
@st.cache_resource
def load_kiwi():
    return Kiwi()

with st.spinner("알고리즘을 재구성하는 중..."):
    try:
        kiwi = load_kiwi()
        st.success("✅ 모델 초기화 완료!")
    except Exception as e:
        st.error(f"❌ 모델 초기화 중 오류 발생: {e}")
        st.stop()

# 4. 울리포 로직 (명사 사전)
NOUN_DICT = sorted([
    "알바트로스", "심연", "권태", "악의꽃", "사체", "아편", "유령", "몽유병",
    "해부대", "재봉틀", "우산", "마네킹", "자동기술", "무의식", "초현실",
    "파편", "공백", "소멸", "기억", "퍼즐", "오브제", "레디메이드", "몽타주"
])

# 5. UI 구성
st.sidebar.header("⚙️ 설정")
shift_n = st.sidebar.slider("치환 간격 (n)", 1, 15, 7)

user_input = st.text_area("해체할 문장을 입력하세요:", placeholder="예: 예술은 인생의 안주다.", height=150)

if st.button("시적 변환 실행"):
    if user_input:
        tokens = kiwi.tokenize(user_input)
        result = []
        for token in tokens:
            if token.tag in ['NNG', 'NNP'] and token.form in NOUN_DICT:
                idx = NOUN_DICT.index(token.form)
                result.append(NOUN_DICT[(idx + shift_n) % len(NOUN_DICT)])
            else:
                result.append(token.form)
        
        st.markdown("### ✨ 변환 결과")
        st.info("".join(result))
    else:
        st.warning("문장을 입력해 주세요.")
