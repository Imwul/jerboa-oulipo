import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Jerboa Infinite Engine", page_icon="🐦")

@st.cache_resource
def load_vast_ocean():
    kiwi = Kiwi()
    
    # 1. 1차 방어선: 이물의 취향을 담은 니치 단어 리스트 (인터넷 안 돼도 작동)
    base_words = [
        "심연", "권태", "알바트로스", "오브제", "몽유병", "유령", "해부대", "재봉틀", 
        "우산", "마네킹", "자동기술", "무의식", "초현실", "파편", "공백", "소멸", 
        "보들레르", "페렉", "키냐르", "누보로망", "사체", "예술", "인생", "사랑",
        "해부", "메스", "처방", "청진기", "세포", "증식", "마취", "신경", "혈관"
    ]
    
    # 2. 2차 방어선: 다중 외부 주소 시도 (가나다순 정렬된 안정적인 주소들)
    mirrors = [
        "https://raw.githubusercontent.com/naver/korean-wordlist/master/nouns.txt",
        "https://raw.githubusercontent.com/monologg/korean-wordlist/master/nouns.txt",
        "https://raw.githubusercontent.com/loosie/doraemon/master/data/nouns.txt"
    ]
    
    # "나 진짜 사람이야!"라고 속이는 헤더 추가
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    
    final_set = set(base_words)
    success_msg = "⚠️ 외부 연결 실패, 로컬 모드 가동"

    for url in mirrors:
        try:
            # 타임아웃을 15초로 넉넉하게 줘서 스트림릿이 인내심을 갖게 해
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                words = [w.strip() for w in r.text.split('\n') if len(w.strip()) > 1]
                # 404 에러 메시지가 섞여 들어오지 않았는지 마지막 검증
                if "404" not in words[0]:
                    final_set.update(words)
                    success_msg = f"✅ 외부 바다 연결 성공! (출처: {url.split('/')[3]})"
                    break
        except:
            continue
            
    return kiwi, sorted(list(final_set)), success_msg

kiwi, NOUN_DICT, status = load_vast_ocean()

st.title("🐦 저보아: 무한 울리포 엔진")
st.sidebar.info(status
