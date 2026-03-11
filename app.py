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

    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    h1 {
        font-family: 'Trattatello', 'Apple Chancery', 'Chalkduster', cursive !important;
        font-size: 3.8rem !important; color: #000000 !important;
        text-align: center; margin-bottom: 1.5rem !important; padding-top: 1rem !important;
    }

    * { font-family: 'Eulyoo1945-Regular', serif !important; color: #000000 !important; }

    textarea {
        background-color: #111111 !important; color: #FFFFFF !important;
        border: 2px solid #000000 !important; caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }
    
    .instruction-box {
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem;
    }

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

@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각", "미학"]

NOUN_DICT = load_oulipo_dict()
# 이물이 좋아하는 파스텔 톤 팔레트
WASHED_COLORS = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]

st.title("Jerboa Circle: Surrealist Workshop")

tab1, tab2 = st.tabs(["🏺 Oulipo Engine (S+N)", "🔪 The Dissector (마그넷 & 나이프)"])

# ---------------------------------------------------------
# TAB 1: 기존 Oulipo Engine (S+N)
# ---------------------------------------------------------
with tab1:
    st.markdown("""
    <div class="instruction-box">
        <b>[울리포 엔진 가동 지침]</b><br>
        - <b>해부대:</b> 문장을 입력하세요. <b>줄 바꿈</b>과 <b>단어 사이의 여백</b>은 보존됩니다.<br>
        - <b>S+N 거리:</b> 해당 명사를 사전에서 찾아, N번째 뒤에 위치한 단어로 치환합니다.<br>
        - <b>성역 보호:</b> <b>&lt;단어&gt;</b> 와 같이 꺽쇠로 감싼 부분은 '성역'이 됩니다.
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
            if part.startswith('<') and part.endswith('>'): line_result.append(part[1:-1])
            elif part == '': continue
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
                    if t.tag.startswith('N') and (hash(t.form) % 100) < prob:
                        if t.form in NOUN_DICT:
                            idx = (NOUN_DICT.index(t.form) + shift) % d_len
                            new_w = NOUN_DICT[idx]
                        else:
                            random.seed(hash(t.form))
                            new_w = NOUN_DICT[random.randint(0, d_len-1)]
                        sub_res.append((new_w, 'NNG'))
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
        - <b>🧲 마그넷:</b> 자유롭게 드래그하여 배치합니다. 뿌리가 같은 파편은 색상을 공유합니다.<br>
        - <b>🔪 칼 툴:</b> 켜진 상태로 마그넷의 <b>글자를 클릭</b>하면, 그 위치에서 텍스트가 잘려나갑니다.<br>
        - <b>🧴 풀 툴:</b> 켜진 상태로 두 마그넷을 순서대로 클릭하면 하나의 파편으로 다시 붙습니다.<br>
        - <b>🔄 되돌리기:</b> 키보드 <b>[Ctrl + Z]</b>를 누르면 이전 상태로 돌아갑니다.
    </div>
    """, unsafe_allow_html=True)

    user_input_2 = st.text_area("해부대 (마그넷 생성용)", placeholder="캔버스에 뿌릴 시를 입력하세요.", height=150, key="magnet_input")

    if st.button("🧲 캔버스에 마그넷 생성", key="create_magnet"):
        if user_input_2:
            words = [w for w in re.split(r'\s+', user_input_2) if w]
            words_json = json.dumps(words)
            colors_json = json.dumps(WASHED_COLORS)

            custom_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                @font-face {{
                    font-family: 'Eulyoo1945-Regular';
                    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
                }}
                body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 0; overflow: hidden; user-select: none; }}
                
                #toolbar {{ background: #000; padding: 10px; display: flex; gap: 10px; align-items: center; justify-content: center; }}
                .tool-btn {{ 
                    background: #fff; color: #000; border: 2px solid #fff; padding: 8px 20px; 
                    font-size: 1rem; font-weight: bold; cursor: pointer; font-family: inherit; transition: all 0.2s;
                }}
                .tool-btn.active-knife {{ background: #ff4d4d; color: #fff; border-color: #ff4d4d; }}
                .tool-btn.active-glue {{ background: #4d79ff; color: #fff; border-color: #4d79ff; }}
                
                #canvas-area {{ 
                    width: 100%; height: 650px; background: #fafafa; position: relative; 
                    border: 3px solid #000; border-top: none; cursor: default;
                }}
                
                /* 마그넷 기본 스타일 */
                .magnet {{
                    position: absolute; border: 2px solid #000; padding: 6px 10px;
                    font-size: 1.4rem; font-weight: bold; cursor: grab; 
                    white-space: nowrap; box-shadow: 4px 4px 0px #000; transition: transform 0.1s, box-shadow 0.2s;
                }}
                .magnet:active {{ cursor: grabbing; transform: scale(1.05); z-index: 1000 !important; }}
                
                /* 칼 모드 */
                body.knife-mode #canvas-area {{ cursor: crosshair; }}
                body.knife-mode .magnet {{ cursor: crosshair; }}
                body.knife-mode .magnet:active {{ transform: none; cursor: crosshair; }}
                .char {{ display: inline-block; transition: color 0.2s; }}
                body.knife-mode .char:hover {{ color: #ff4d4d; font-weight: 900; transform: translateY(-2px); }}
                
                /* 풀 모드 */
                body.glue-mode #canvas-area {{ cursor: cell; }}
                body.glue-mode .magnet {{ cursor: cell; }}
                body.glue-mode .magnet:active {{ transform: none; cursor: cell; }}
                body.glue-mode .char {{ pointer-events: none; }} /* 풀 모드에선 개별 글자 클릭 무시 */
                .magnet.glue-selected {{ box-shadow: 0 0 15px 5px #4d79ff !important; border-color: #4d79ff; transform: scale(1.05); }}
                
            </style>
            </head>
            <body>
                <div id="toolbar">
                    <button id="knifeToggle" class="tool-btn">🔪 칼 툴 (Off)</button>
                    <button id="glueToggle" class="tool-btn">🧴 풀 툴 (Off)</button>
                    <span style="color:#fff; font-size:0.9rem; margin-left:15px;">※ 되돌리기: Ctrl+Z</span>
                </div>
                <div id="canvas-area"></div>

                <script>
                    const initialWords = {words_json};
                    const colorPalette = {colors_json};
                    const canvas = document.getElementById('canvas-area');
                    
                    let knifeMode = false;
                    let glueMode = false;
                    let glueTarget = null;
                    let zIndex = 10;
                    let historyStack = []; // Ctrl+Z를 위한 상태 저장소

                    const knifeBtn = document.getElementById('knifeToggle');
                    const glueBtn = document.getElementById('glueToggle');

                    // 🛠 툴 토글 로직
                    knifeBtn.addEventListener('click', () => {{
                        knifeMode = !knifeMode;
                        if(knifeMode) {{ glueMode = false; clearGlueTarget(); updateButtons(); }}
                        updateButtons();
                    }});

                    glueBtn.addEventListener('click', () => {{
                        glueMode = !glueMode;
                        if(glueMode) {{ knifeMode = false; updateButtons(); }}
                        else {{ clearGlueTarget(); }}
                        updateButtons();
                    }});

                    function updateButtons() {{
                        document.body.classList.toggle('knife-mode', knifeMode);
                        document.body.classList.toggle('glue-mode', glueMode);
                        knifeBtn.classList.toggle('active-knife', knifeMode);
                        glueBtn.classList.toggle('active-glue', glueMode);
                        knifeBtn.innerText = knifeMode ? '🔪 칼 툴 (On)' : '🔪 칼 툴 (Off)';
                        glueBtn.innerText = glueMode ? '🧴 풀 툴 (On)' : '🧴 풀 툴 (Off)';
                    }}

                    function clearGlueTarget() {{
                        if (glueTarget) glueTarget.classList.remove('glue-selected');
                        glueTarget = null;
                    }}

                    // 💾 상태 저장 (Undo용)
                    function saveState() {{
                        const state = Array.from(document.querySelectorAll('.magnet')).map(m => ({{
                            text: Array.from(m.children).map(c => c.innerText).join(''),
                            left: m.style.left,
                            top: m.style.top,
                            bg: m.style.backgroundColor
                        }}));
                        historyStack.push(state);
                    }}

                    

                    // 🧲 마그넷 생성 함수 (save 매개변수로 Undo 기록 여부 결정)
                    function createMagnet(text, startX, startY, bgColor, save = true) {{
                        if (!text) return;
                        if (save) saveState();

                        const div = document.createElement('div');
                        div.className = 'magnet';
                        div.style.left = startX + 'px';
                        div.style.top = startY + 'px';
                        div.style.backgroundColor = bgColor;
                        div.style.zIndex = ++zIndex;

                        // 칼질을 위한 span 감싸기
                        Array.from(text).forEach((char, index) => {{
                            const span = document.createElement('span');
                            span.className = 'char';
                            span.innerText = char;
                            span.dataset.index = index;
                            
                            // 🔪 쪼개기 이벤트 (칼 모드일 때만 span에서 처리)
                            span.addEventListener('mousedown', (e) => {{
                                if (!knifeMode) return;
                                e.stopPropagation(); 
                                
                                const clickedIdx = parseInt(e.target.dataset.index);
                                if (clickedIdx === 0) return; // 첫 글자 자르기 방지

                                const chars = Array.from(div.children);
                                const word1 = chars.slice(0, clickedIdx).map(s => s.innerText).join('');
                                const word2 = chars.slice(clickedIdx).map(s => s.innerText).join('');

                                const pX = parseFloat(div.style.left);
                                const pY = parseFloat(div.style.top);

                                saveState(); // 자르기 전 상태 저장
                                div.remove();

                                // 자식 파편들은 부모의 색상을 그대로 상속받음
                                createMagnet(word1, pX, pY, bgColor, false);
                                createMagnet(word2, pX + e.target.offsetLeft + 5, pY + 15, bgColor, false);
                            }});
                            div.appendChild(span);
                        }});

                        // 🧴 풀 툴 이벤트 & 드래그 이벤트 (div 레벨에서 처리)
                        div.addEventListener('mousedown', (e) => {{
                            if (knifeMode) return; // 칼 모드면 span 이벤트로 넘어감

                            if (glueMode) {{
                                e.stopPropagation();
                                if (!glueTarget) {{
                                    glueTarget = div;
                                    div.classList.add('glue-selected');
                                }} else if (glueTarget !== div) {{
                                    saveState(); // 붙이기 전 상태 저장
                                    const text1 = Array.from(glueTarget.children).map(c=>c.innerText).join('');
                                    const text2 = Array.from(div.children).map(c=>c.innerText).join('');
                                    
                                    // 캔버스 상에서 더 왼쪽에 있는 단어가 앞부분으로 옴 (물리적 직관성)
                                    const t1X = parseFloat(glueTarget.style.left);
                                    const t2X = parseFloat(div.style.left);
                                    const combinedText = t1X <= t2X ? text1 + text2 : text2 + text1;
                                    
                                    // 색상은 첫 번째 타겟의 색상을 상속
                                    const combinedBg = glueTarget.style.backgroundColor;
                                    const newX = Math.min(t1X, t2X);
                                    const newY = parseFloat(glueTarget.style.top);
                                    
                                    glueTarget.remove();
                                    div.remove();
                                    glueTarget = null;
                                    
                                    createMagnet(combinedText, newX, newY, combinedBg, false);
                                }} else {{
                                    // 자기 자신을 다시 누르면 취소
                                    clearGlueTarget();
                                }}
                                return;
                            }}

                            // 🖐 일반 드래그 로직
                            e.preventDefault();
                            saveState(); // 드래그 시작 전 위치 저장
                            div.style.zIndex = ++zIndex;
                            let pos3 = e.clientX, pos4 = e.clientY;
                            
                            document.onmouseup = () => {{ document.onmouseup = null; document.onmousemove = null; }};
                            document.onmousemove = (ev) => {{
                                ev.preventDefault();
                                let pos1 = pos3 - ev.clientX;
                                let pos2 = pos4 - ev.clientY;
                                pos3 = ev.clientX; pos4 = ev.clientY;
                                div.style.top = (div.offsetTop - pos2) + "px";
                                div.style.left = (div.offsetLeft - pos1) + "px";
                            }};
                        }});

                        canvas.appendChild(div);
                    }}

                    // 초기 텍스트 흩뿌리기 (이때 랜덤 파스텔톤 부여)
                    initialWords.forEach((word, i) => {{
                        const x = 30 + (i % 6) * 110 + Math.random() * 30;
                        const y = 30 + Math.floor(i / 6) * 70 + Math.random() * 30;
                        const initialColor = colorPalette[Math.floor(Math.random() * colorPalette.length)];
                        createMagnet(word, x, y, initialColor, false);
                    }});
                </script>
            </body>
            </html>
            """
            
            components.html(custom_html, height=750)

st.divider()

# --- 6. 🏺 따로 움직이는 파편들 (오리지널 디자인 복구) ---
st.subheader("🏺 사전의 파편들")
samples = random.sample(NOUN_DICT, min(40, len(NOUN_DICT)))

html_tags = '<div style="text-align:center; padding-bottom: 50px;">'
for w in samples:
    color = random.choice(WASHED_COLORS)
    delay = random.uniform(0, 4)
    duration = random.uniform(5, 8)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; animation-delay: {delay}s; animation-duration: {duration}s;">{w}</span>'
html_tags += '</div>'

st.markdown(html_tags, unsafe_allow_html=True)
