import streamlit as st
from kiwipiepy import Kiwi

@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

# 1. 사전에 테스트용 단어 '예술', '인생', '안주'를 추가했어!
NOUN_DICT = sorted([
    "예술", "인생", "안주", "알바트로스", "심연", "권태", "악의꽃", "사체", 
    "아편", "유령", "몽유병", "해부대", "재봉틀", "우산", "마네킹", "자동기술", 
    "무의식", "초현실", "파편", "공백", "소멸", "기억", "퍼즐", "오브제", 
    "레디메이드", "몽타주", "단절", "우연", "구조", "필연", "미궁", "거울"
])

def s_plus_n_pro(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    for token in tokens:
        # 띄어쓰기 보존 로직 추가
        result.append(text[last_end:token.start])
        
        if token.tag in ['NNG', 'NNP'] and token.form in NOUN_DICT:
            idx = NOUN_DICT.index(token.form)
            # n만큼 뒤의 단어로 치환
            result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])
        else:
            result.append(token.form)
        last_end = token.end
    result.append(text[last_end:])
    return "".join(result)

st.set_page_config(page_title="Jerboa Oulipo Machine", page_icon="🐦")
st.title("저보아 서클 시즌2: 울리포 머신")
st.write("---")

shift_n = st.sidebar.slider("치환 간격 (n)", 1, 15, 7)
user_input = st.text_area("해체할 문장을 입력하세요:", placeholder="예: 예술은 인생의 안주다.", height=150)

if st.button("시적 변환 실행"):
    if user_input:
        output = s_plus_n_pro(user_input, shift_n)
        st.markdown("### ✨ 변환 결과")
        st.success(output)
    else:
        st.warning("문장을 입력해 주세요, 이물.")
