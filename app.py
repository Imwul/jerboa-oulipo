import streamlit as st
import streamlit.components.v1 as components
from kiwipiepy import Kiwi
import random
import os
import re
import json

# --- 1. 페이지 설정 & 🎨 디자인 (CSS) ---
st.set_page_config(page_title="Jerboa Circle", layout="wide")

st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }

    /* 을유1945 폰트 로드 */
    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    /* 제목(h1) 전용 */
    h1 {
        font-family: 'Trattatello', 'Apple Chancery', 'Chalkduster', cursive !important;
        font-size: 3.8rem !important; color: #000000 !important;
        text-align: center; margin-bottom: 1.5rem !important; padding-top: 1rem !important;
    }

    /* 그 외 모든 본문 및 요소 */
    * { font-family: 'Eulyoo1945-Regular', serif !important; color: #000000 !important; }

    /* 📱 모바일 대응 */
    @media (max-width: 768px) {
        h1 { font-size: 2.2rem !important; }
        .fragment-tag { padding: 4px 8px !important; margin: 4px !important; font-size: 0.8rem !important; }
    }

    /* 해부대(입력창): 검은 배경 & 하얀 글씨 */
    textarea {
        background-color: #111111 !important; color: #FFFFFF !important;
        border: 2px solid #000000 !important; caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }
    
    .instruction-box {
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem;
    }

    /* 유령의 군무 애니메이션 */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(1.5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    .fragment-tag {
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 5s ease-in-out infinite;
        font-weight: bold; cursor: default;
    }

    /* 버튼 스타일 */
    div.stButton > button { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border-radius: 0px !important; width: 100% !important;
        height: 3.5rem; font-size: 1.2rem !important;
    }
    div.stButton > button p { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

# --- 3. 사전 로딩 ---
@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각", "미학"]

NOUN_DICT = load_oulipo_dict()

# --- 4. 메인 타이틀 ---
st.title("Jerboa Circle: Surrealist Workshop")

# --- 5. 탭 구성 ---
tab1, tab2 = st.tabs(["🏺 Oulipo Engine (S+N)", "🔪 The Dissector (마그넷 & 나이프)"])

# ---------------------------------------------------------
# TAB 1: 기존 Oulipo Engine (S+N)
# ---------------------------------------------------------
with tab1:
    st.markdown("""
    <div class="instruction-box">
        <b>[울리포 엔진 가동 지침]</b><br>
        - <b>해부대:</b> 문장을 입력하세요. <b>줄 바꿈</b>과 <b>단어 사이의 여백</b>은 엄격히 보존됩니다.<br>
        - <b>S+N 거리:</b> 해당 명사를 사전에서 찾아, N번째 뒤에 위치한 단어로 치환합니다.<br>
        - <b>성역 보호:</b> <b>&lt;단어&gt;</b> 와 같이 꺽쇠로 감싼 부분은 변하지 않는 '성역'이 됩니다.<br>
        - <b>변환 확률:</b> 문장 속 모든 명사를 바꿀지, 일부만 무작위로 치환할지 결정합니다.<br>
        - <b>활자의 파동:</b> 진동과 비틀림을 조절하여 문장에 시각적 불안감을 부여하세요.
    </div>
    """, unsafe_allow_html=True)

    user_input = st.text_area("해부대", placeholder="문장을 해부대에 올리세요. 나는 <심연을> 보았다.", height=200, key="engine_input")

    col1, col2 = st.columns(2)
    with col1: shift_val = st.slider("S+N 거리", 1, 1000, 7, key="shift_val")
    with col2: prob_val = st.slider("변환 확률 (%)", 0, 100, 100, key="prob_val")

    col3, col4 = st.columns(2)
    with col3: bumpy_val = st.slider("진동", 0.0, 0.6, 0.15, key="bumpy_val")
    with col4: tilt_val = st.slider("비틀림", 0, 30, 10, key="tilt_val")

    def transform_with_logic(line, shift, prob):
        parts = re.split(r'(<.*?>)', line)
        d_len = len(NOUN_DICT)
        line_result = []
        
        for part in parts:
            if part.startswith('<') and part.endswith('>'):
                line_result.append(part[1:-1])
            elif part == '':
                continue
            else:
                leading_ws = re.match(r'^\s*', part).group()
                trailing_ws = re.search(r'\s*$', part).group()
                content = part.strip()
                
                if not content:
                    line_result.append(part)
                    continue
                
                tokens = kiwi.tokenize(content)
                sub_res = []
                for t in tokens:
                    if t.tag.startswith('N'):
                        if (hash(t.form) % 100) < prob:
                            if t.form in NOUN_DICT:
                                idx = (NOUN_DICT.index(t.form) + shift) % d_len
                                new_w = NOUN_DICT[idx]
                            else:
                                random.seed(hash(t.form))
                                new_w = NOUN_DICT[random.randint(0, d_len-1)]
                            sub_res.append((new_w, 'NNG'))
                        else: sub_res.append((t.form, t.tag))
                    else: sub_res.append((t.form, t.tag))
                
                line_result.append(leading_ws + kiwi.join(sub_res) + trailing_ws)
                
        return "".join(line_result)

    if st.button("✨ 문장 재단하기", key="engine_btn"):
        if user_input:
            lines = user_input.split('\n')
            st.subheader("🖼️ Resulting Fragment")
            html_res = '<div style="line-height: 2.3; word-wrap: break-word; padding: 25px; border: 3px solid #000000; background-color: #FFFFFF; white-space: pre-wrap;">'
            
            for line in lines:
                if not line.strip():
                    html_res += '\n'
                    continue
                transformed_line = transform_with_logic(line, shift_val, prob_val)
                for char in transformed_line:
                    if char == ' ': html_res += '&nbsp;'
                    else:
                        fs = 1.4 + random.uniform(-bumpy_val, bumpy_val)
                        rot = random.uniform(-tilt_val, tilt_val)
                        html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold;">{char}</span>'
                html_res += '\n'
            
            html_res += '</div>'
            st.markdown(html_res, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: The Dissector (커스텀 캔버스 로직)
# ---------------------------------------------------------
with tab2:
    st.markdown("""
    <div class="instruction-box">
        <b>[마그넷 & 나이프 해부 지침]</b><br>
        - <b>🧲 마그넷 모드:</b> 분리된 텍스트 덩어리를 캔버스 위에서 자유롭게 드래그하여 배치합니다.<br>
        - <b>🔪 칼 모드:</b> 상단의 스위치를 켜면 커서가 칼로 변합니다. 마그넷의 <b>글자와 글자 사이(특정 글자)</b>를 클릭하면 해당 위치에서 텍스트가 두동강 납니다.
    </div>
    """, unsafe_allow_html=True)

    user_input_2 = st.text_area("해부대 (마그넷 생성용)", placeholder="캔버스에 뿌릴 시를 입력하세요.", height=150, key="magnet_input")

    if st.button("🧲 캔버스에 마그넷 생성", key="create_magnet"):
        if user_input_2:
            # 줄바꿈과 공백을 기준으로 어절을 리스트화 (빈 문자열 제거)
            words = [w for w in re.split(r'\s+', user_input_2) if w]
            words_json = json.dumps(words)

            # HTML/JS 기반의 인터랙티브 캔버스 생성
            custom_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                @font-face {{
                    font-family: 'Eulyoo1945-Regular';
                    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
                }}
                body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 0; overflow: hidden; }}
                #toolbar {{ background: #000; padding: 10px; display: flex; align-items: center; justify-content: center; }}
                #knifeToggle {{ 
                    background: #fff; color: #000; border: 2px solid #fff; padding: 8px 20px; 
                    font-size: 1rem; font-weight: bold; cursor: pointer; font-family: inherit; transition: all 0.2s;
                }}
                #knifeToggle.active {{ background: #ff4d4d; color: #fff; border-color: #ff4d4d; }}
                
                #canvas-area {{ 
                    width: 100%; height: 600px; background: #fafafa; position: relative; 
                    border: 3px solid #000; border-top: none; cursor: default;
                }}
                
                /* 마그넷 기본 스타일 */
                .magnet {{
                    position: absolute; background: #fff; border: 2px solid #000; padding: 6px 10px;
                    font-size: 1.4rem; font-weight: bold; cursor: grab; user-select: none; 
                    white-space: nowrap; box-shadow: 4px 4px 0px #000; transition: transform 0.1s;
                }}
                .magnet:active {{ cursor: grabbing; transform: scale(1.05); z-index: 1000 !important; }}
                
                /* 칼 모드 스타일 */
                body.knife-mode #canvas-area {{ cursor: crosshair; }}
                body.knife-mode .magnet {{ cursor: crosshair; }}
                body.knife-mode .magnet:active {{ transform: none; cursor: crosshair; }}
                
                /* 칼 모드일 때 쪼갤 위치의 글자 강조 */
                .char {{ display: inline-block; transition: color 0.2s; }}
                body.knife-mode .char:hover {{ color: #ff4d4d; font-weight: 900; transform: translateY(-2px); }}
            </style>
            </head>
            <body>
                <div id="toolbar">
                    <button id="knifeToggle">🔪 칼 모드 (Off)</button>
                </div>
                <div id="canvas-area"></div>

                <script>
                    const initialWords = {words_json};
                    const canvas = document.getElementById('canvas-area');
                    const knifeBtn = document.getElementById('knifeToggle');
                    let knifeMode = false;
                    let zIndex = 10;

                    // 🔪 칼 모드 토글
                    knifeBtn.addEventListener('click', () => {{
                        knifeMode = !knifeMode;
                        knifeBtn.classList.toggle('active', knifeMode);
                        knifeBtn.innerText = knifeMode ? '🔪 칼 모드 (On: 글자를 클릭해 자르기)' : '🔪 칼 모드 (Off: 드래그 앤 드롭)';
                        document.body.classList.toggle('knife-mode', knifeMode);
                    }});

                    // 🧲 마그넷 생성 함수
                    function createMagnet(text, startX, startY) {{
                        if (!text) return;
                        const div = document.createElement('div');
                        div.className = 'magnet';
                        div.style.left = startX + 'px';
                        div.style.top = startY + 'px';
                        div.style.zIndex = ++zIndex;

                        // 칼질을 위해 글자(char) 단위로 span으로 감싸기
                        Array.from(text).forEach((char, index) => {{
                            const span = document.createElement('span');
                            span.className = 'char';
                            span.innerText = char;
                            span.dataset.index = index;
                            
                            // 클릭 시 쪼개기 이벤트
                            span.addEventListener('mousedown', (e) => {{
                                if (!knifeMode) return;
                                e.stopPropagation(); // 드래그 방지
                                
                                const clickedIdx = parseInt(e.target.dataset.index);
                                // 첫 글자를 자르면 앞이 비어버리므로 방지 (두 번째 글자부터 잘림)
                                if (clickedIdx === 0) return; 

                                const chars = Array.from(div.children);
                                const word1 = chars.slice(0, clickedIdx).map(s => s.innerText).join('');
                                const word2 = chars.slice(clickedIdx).map(s => s.innerText).join('');

                                // 현재 마그넷의 위치 값 가져오기
                                const rect = div.getBoundingClientRect();
                                const canvasRect = canvas.getBoundingClientRect();
                                const pX = rect.left - canvasRect.left;
                                const pY = rect.top - canvasRect.top;

                                // 기존 마그넷 삭제
                                div.remove();

                                // 두 개의 새로운 파편으로 분열
                                createMagnet(word1, pX, pY);
                                createMagnet(word2, pX + e.target.offsetLeft, pY + 15); // 살짝 아래로 어긋나게
                            }});
                            div.appendChild(span);
                        }});

                        makeDraggable(div);
                        canvas.appendChild(div);
                    }}

                    // 🖐 드래그 앤 드롭 로직
                    function makeDraggable(elmnt) {{
                        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
                        elmnt.onmousedown = dragMouseDown;

                        function dragMouseDown(e) {{
                            if (knifeMode) return; // 칼 모드일 땐 드래그 금지
                            e.preventDefault();
                            elmnt.style.zIndex = ++zIndex;
                            pos3 = e.clientX;
                            pos4 = e.clientY;
                            document.onmouseup = closeDragElement;
                            document.onmousemove = elementDrag;
                        }}

                        function elementDrag(e) {{
                            e.preventDefault();
                            pos1 = pos3 - e.clientX;
                            pos2 = pos4 - e.clientY;
                            pos3 = e.clientX;
                            pos4 = e.clientY;
                            elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
                            elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
                        }}

                        function closeDragElement() {{
                            document.onmouseup = null;
                            document.onmousemove = null;
                        }}
                    }}

                    // 초기 텍스트 흩뿌리기
                    initialWords.forEach((word, i) => {{
                        // 캔버스 내 랜덤 위치에 겹치지 않게 대략적인 그리드 배치
                        const x = 20 + (i % 5) * 120 + Math.random() * 20;
                        const y = 20 + Math.floor(i / 5) * 60 + Math.random() * 20;
                        createMagnet(word, x, y);
                    }});
                </script>
            </body>
            </html>
            """
            
            # HTML 렌더링 (높이를 여유롭게 700으로 설정)
            components.html(custom_html, height=700)

st.divider()

# --- 6. 🏺 따로 움직이는 파편들 (오리지널 디자인) ---
st.subheader("🏺 사전의 파편들")
washed_colors = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
samples = random.sample(NOUN_DICT, min(40, len(NOUN_DICT)))

html_tags = '<div style="text-align:center; padding-bottom: 50px;">'
for w in samples:
    color = random.choice(washed_colors)
    delay = random.uniform(0, 4)
    duration = random.uniform(5, 8)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; animation-delay: {delay}s; animation-duration: {duration}s;">{w}</span>'
html_tags += '</div>'

st.markdown(html_tags, unsafe_allow_html=True)
