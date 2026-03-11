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
        - <b>🧲 마그넷:</b> 자유롭게 드래그하여 배치합니다. 뿌리가 같은 파편은 고유의 색상을 공유합니다.<br>
        - <b>🔪 칼 툴:</b> 켜진 상태로 마그넷의 특정 글자를 클릭하면, 그 위치에서 텍스트가 잘려나갑니다.<br>
        - <b>🧴 풀 툴:</b> 켜진 상태로 두 마그넷을 클릭하면 붙습니다. 서로 다른 색상도 모자이크처럼 유지됩니다.<br>
        - <b>✨ 영감 (셔플):</b> 파편들을 임의의 행(3~5개)으로 재배치하여 우연의 시를 만듭니다.<br>
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
                
                #toolbar {{ background: #000; padding: 10px; display: flex; gap: 10px; align-items: center; justify-content: center; flex-wrap: wrap; }}
                .tool-btn {{ 
                    background: #fff; color: #000; border: 2px solid #fff; padding: 8px 16px; 
                    font-size: 0.95rem; font-weight: bold; cursor: pointer; font-family: inherit; transition: all 0.2s;
                }}
                .tool-btn.active-knife {{ background: #ff4d4d; color: #fff; border-color: #ff4d4d; }}
                .tool-btn.active-glue {{ background: #4d79ff; color: #fff; border-color: #4d79ff; }}
                #shuffleBtn {{ background: #ffe3b3; color: #000; border-color: #ffe3b3; }}
                #shuffleBtn:active {{ transform: scale(0.95); }}
                
                #canvas-area {{ 
                    width: 100%; height: 650px; background: #fafafa; position: relative; 
                    border: 3px solid #000; border-top: none; cursor: default; overflow: hidden;
                }}
                
                /* 마그넷: 이제 내부 글자들의 색을 보여주기 위해 투명한 플렉스 박스가 됨 */
                .magnet {{
                    position: absolute; border: 2px solid #000; padding: 0; display: flex;
                    font-size: 1.4rem; font-weight: bold; cursor: grab; 
                    white-space: nowrap; box-shadow: 4px 4px 0px #000; transition: transform 0.1s, box-shadow 0.2s;
                    background: transparent;
                }}
                .magnet:active {{ cursor: grabbing; transform: scale(1.05); z-index: 1000 !important; }}
                
                /* 개별 글자 스타일 */
                .char {{ 
                    display: inline-block; padding: 6px 3px; transition: color 0.2s; 
                }}
                .char:first-child {{ padding-left: 8px; }}
                .char:last-child {{ padding-right: 8px; }}
                
                body.knife-mode #canvas-area, body.knife-mode .magnet {{ cursor: crosshair; }}
                body.knife-mode .magnet:active {{ transform: none; cursor: crosshair; }}
                body.knife-mode .char:hover {{ color: #ff4d4d; font-weight: 900; transform: translateY(-2px); }}
                
                body.glue-mode #canvas-area, body.glue-mode .magnet {{ cursor: cell; }}
                body.glue-mode .magnet:active {{ transform: none; cursor: cell; }}
                body.glue-mode .char {{ pointer-events: none; }}
                .magnet.glue-selected {{ box-shadow: 0 0 15px 5px #4d79ff !important; border-color: #4d79ff; transform: scale(1.05); }}
                
            </style>
            </head>
            <body>
                <div id="toolbar">
                    <button id="knifeToggle" class="tool-btn">🔪 칼 툴 (Off)</button>
                    <button id="glueToggle" class="tool-btn">🧴 풀 툴 (Off)</button>
                    <button id="shuffleBtn" class="tool-btn">✨ 영감 (셔플)</button>
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
                    let historyStack = [];

                    const knifeBtn = document.getElementById('knifeToggle');
                    const glueBtn = document.getElementById('glueToggle');
                    const shuffleBtn = document.getElementById('shuffleBtn');

                    // 🛠 툴 토글
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

                    // DOM에서 마그넷 데이터(글자+색상 배열) 추출
                    function getCharData(magnetEl) {{
                        return Array.from(magnetEl.children).map(span => ({{
                            char: span.innerText,
                            bg: span.style.backgroundColor
                        }}));
                    }}

                    // 💾 상태 저장
                    function saveState() {{
                        const state = Array.from(document.querySelectorAll('.magnet')).map(m => ({{
                            charData: getCharData(m),
                            left: m.style.left,
                            top: m.style.top
                        }}));
                        historyStack.push(state);
                    }}

               
                    // 🧲 마그넷 생성 (charDataArray = [{char: '가', bg: 'red'}, ...])
                    function createMagnet(charDataArray, startX, startY, save = true) {{
                        if (!charDataArray || charDataArray.length === 0) return;
                        if (save) saveState();

                        const div = document.createElement('div');
                        div.className = 'magnet';
                        div.style.left = startX + 'px';
                        div.style.top = startY + 'px';
                        div.style.zIndex = ++zIndex;

                        charDataArray.forEach((item, index) => {{
                            const span = document.createElement('span');
                            span.className = 'char';
                            span.innerText = item.char;
                            span.style.backgroundColor = item.bg; // 개별 글자에 색상 부여
                            span.dataset.index = index;
                            
                            // 🔪 자르기 이벤트
                            span.addEventListener('mousedown', (e) => {{
                                if (!knifeMode) return;
                                e.stopPropagation(); 
                                
                                const clickedIdx = parseInt(e.target.dataset.index);
                                if (clickedIdx === 0) return; // 첫 글자 방지

                                const currentData = getCharData(div);
                                const part1 = currentData.slice(0, clickedIdx);
                                const part2 = currentData.slice(clickedIdx);

                                const pX = parseFloat(div.style.left);
                                const pY = parseFloat(div.style.top);

                                saveState();
                                div.remove();

                                createMagnet(part1, pX, pY, false);
                                createMagnet(part2, pX + e.target.offsetLeft + 5, pY + 15, false);
                            }});
                            div.appendChild(span);
                        }});

                        // 🧴 풀 툴 & 드래그
                        div.addEventListener('mousedown', (e) => {{
                            if (knifeMode) return;

                            if (glueMode) {{
                                e.stopPropagation();
                                if (!glueTarget) {{
                                    glueTarget = div;
                                    div.classList.add('glue-selected');
                                }} else if (glueTarget !== div) {{
                                    saveState();
                                    const data1 = getCharData(glueTarget);
                                    const data2 = getCharData(div);
                                    
                                    const t1X = parseFloat(glueTarget.style.left);
                                    const t2X = parseFloat(div.style.left);
                                    
                                    // 왼쪽에 있는 것을 앞으로
                                    const combinedData = t1X <= t2X ? data1.concat(data2) : data2.concat(data1);
                                    const newX = Math.min(t1X, t2X);
                                    const newY = parseFloat(glueTarget.style.top);
                                    
                                    glueTarget.remove();
                                    div.remove();
                                    glueTarget = null;
                                    
                                    createMagnet(combinedData, newX, newY, false);
                                }} else {{
                                    clearGlueTarget();
                                }}
                                return;
                            }}

                            // 드래그
                            e.preventDefault();
                            saveState();
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

                    // ✨ 영감 (셔플) 로직
                    shuffleBtn.addEventListener('click', () => {{
                        saveState();
                        let allMagnets = Array.from(document.querySelectorAll('.magnet'));
                        let dataList = allMagnets.map(m => getCharData(m));

                        // 배열 무작위 섞기
                        for (let i = dataList.length - 1; i > 0; i--) {{
                            const j = Math.floor(Math.random() * (i + 1));
                            [dataList[i], dataList[j]] = [dataList[j], dataList[i]];
                        }}

                        canvas.innerHTML = ''; // 캔버스 초기화
                        clearGlueTarget();

                        let currentY = 50;
                        let currentX = 50;
                        let countInRow = 0;
                        let targetInRow = Math.floor(Math.random() * 3) + 3; // 3~5개

                        dataList.forEach((charData) => {{
                            createMagnet(charData, currentX, currentY, false);
                            currentX += (charData.length * 28) + 30; // 글자 수 기반 대략적인 간격
                            countInRow++;

                            // 캔버스 오른쪽을 벗어나거나 설정된 행의 개수를 채우면 줄바꿈
                            if (countInRow >= targetInRow || currentX > canvas.offsetWidth - 150) {{
                                currentY += 75;
                                currentX = 40 + Math.random() * 60; // 다음 줄 시작 위치도 약간 무작위로
                                countInRow = 0;
                                targetInRow = Math.floor(Math.random() * 3) + 3;
                            }}
                        }});
                    }});

                    // 초기 생성 시 단어를 charDataArray 형태로 변환 후 배치
                    initialWords.forEach((word, i) => {{
                        const x = 30 + (i % 6) * 110 + Math.random() * 30;
                        const y = 30 + Math.floor(i / 6) * 70 + Math.random() * 30;
                        const initialColor = colorPalette[Math.floor(Math.random() * colorPalette.length)];
                        
                        // 단어를 글자 단위로 쪼개고 동일한 배경색 부여
                        const charDataArray = Array.from(word).map(c => ({{ char: c, bg: initialColor }}));
                        createMagnet(charDataArray, x, y, false);
                    }});
                </script>
            </body>
            </html>
            """
            
            components.html(custom_html, height=750)

st.divider()

# --- 6. 🏺 따로 움직이는 파편들 ---
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
