import streamlit as st
from kiwipiepy import Kiwi

# 1. Kiwi 형태소 분석기 초기화
@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

# 2. 저보아 서클 전용: 보들레르 & 초현실주의 니치 사전
# 괄호와 쉼표 오타를 방지하기 위해 깔끔하게 정리했어.
NOUN_DICT = [
    "알바트로스", "심연", "권태", "악의꽃", "사체", "아편", "유령", "몽유병",
    "해부대", "재봉틀", "우산", "마네킹", "자동기술", "무의식", "초현실",
    "파편", "공백", "소멸", "기억", "퍼즐", "오브제", "레디메이드", "몽타주",
    "단절", "우연", "구조", "필연", "미궁", "거울", "나르시스", "에로스",
    "밤", "향기", "음울", "태양", "검은색", "몰락", "환각", "침묵"
]
NOUN_DICT.sort()

def s_plus_n_kiwi(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    
    for token in tokens:
        # 명사일 경우에만 치환 로직 수행
        if token.tag in ['NNG', 'NNP'] and token.form in NOUN_DICT:
            current_idx = NOUN_DICT.index(token.form)
            new_idx = (current_idx + n) % len(NOUN_DICT)
            result.append(NOUN_DICT[new_idx])
