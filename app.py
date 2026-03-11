import streamlit as st
from kiwipiepy import Kiwi
import random
import os
import re

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Jerboa Circle", layout="wide")

# --- 2. 🎨 디자인: Trattatello 미학 & 모바일 최적화 (CSS) ---
st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }

    /* 폰트 설정: Trattatello를 우선 적용하고 시스템 폰트와 세리프 계열을 폴백으로 설정 */
    * { 
        font-family: 'Trattatello', 'Apple Chancery', 'Palatino', 'serif' !important; 
        color: #000000 !important; 
    }
    
    /* 📱 모바일 대응 */
    @media (max-width: 768px) {
        .fragment-tag { padding: 4px 8px !important; margin: 4px !important; font-size: 0.8rem !important; }
        h1 { font-size: 1.8rem !important; }
        .stSlider { padding: 0 10px !important; }
    }

    /* ❗ 해부대(입력창): 검은 배경 & 하얀 글씨 */
    textarea {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }
    
    .instruction-box {
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem;
    }

    /* 🌊 유령의 군무 애니메이션 (개별 소자들을 위한 정의) */
    @keyframes float {
        0%
