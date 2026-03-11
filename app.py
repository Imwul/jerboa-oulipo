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

tab1, tab2, tab3 = st.tabs(["🏺 Oulipo Engine (S+N)", "🔪 The Dissector (마그넷)", "🔥 The Automaton (자동 기술)"])

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

            custom_html_2 = f"""
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
                .tool-btn {{ background: #fff; color: #000; border: 2px solid #fff; padding: 8px 16px; font-size: 0.95rem; font-weight: bold; cursor: pointer; transition: all 0.2s; }}
                .tool-btn.active-knife {{ background: #ff4d4d; color: #fff; border-color: #ff4d4d; }}
                .tool-btn.active-glue {{ background: #4d79ff; color: #fff; border-color: #4d79ff; }}
                #shuffleBtn {{ background: #ffe3b3; color: #000; border-color: #ffe3b3; }}
                #shuffleBtn:active {{ transform: scale(0.95); }}
                #canvas-area {{ width: 100%; height: 650px; background: #fafafa; position: relative; border: 3px solid #000; border-top: none; cursor: default; overflow: hidden; }}
                .magnet {{ position: absolute; border: 2px solid #000; padding: 0; display: flex; font-size: 1.4rem; font-weight: bold; cursor: grab; white-space: nowrap; box-shadow: 4px 4px 0px #000; transition: transform 0.1s, box-shadow 0.2s; background: transparent; }}
                .magnet:active {{ cursor: grabbing; transform: scale(1.05); z-index: 1000 !important; }}
                .char {{ display: inline-block; padding: 6px 3px; transition: color 0.2s; }}
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
                    let knifeMode = false; let glueMode = false; let glueTarget = null; let zIndex = 10;
                    const knifeBtn = document.getElementById('knifeToggle');
                    const glueBtn = document.getElementById('glueToggle');
                    const shuffleBtn = document.getElementById('shuffleBtn');

                    knifeBtn.addEventListener('click', () => {{ knifeMode = !knifeMode; if(knifeMode) {{ glueMode = false; clearGlueTarget(); updateButtons(); }} updateButtons(); }});
                    glueBtn.addEventListener('click', () => {{ glueMode = !glueMode; if(glueMode) {{ knifeMode = false; updateButtons(); }} else {{ clearGlueTarget(); }} updateButtons(); }});

                    function updateButtons() {{
                        document.body.classList.toggle('knife-mode', knifeMode);
                        document.body.classList.toggle('glue-mode', glueMode);
                        knifeBtn.classList.toggle('active-knife', knifeMode);
                        glueBtn.classList.toggle('active-glue', glueMode);
                        knifeBtn.innerText = knifeMode ? '🔪 칼 툴 (On)' : '🔪 칼 툴 (Off)';
                        glueBtn.innerText = glueMode ? '🧴 풀 툴 (On)' : '🧴 풀 툴 (Off)';
                    }}

                    function clearGlueTarget() {{ if (glueTarget) glueTarget.classList.remove('glue-selected'); glueTarget = null; }}
                    function getCharData(magnetEl) {{ return Array.from(magnetEl.children).map(span => ({{ char: span.innerText, bg: span.style.backgroundColor }})); }}

                    function createMagnet(charDataArray, startX, startY) {{
                        if (!charDataArray || charDataArray.length === 0) return;
                        const div = document.createElement('div'); div.className = 'magnet'; div.style.left = startX + 'px'; div.style.top = startY + 'px'; div.style.zIndex = ++zIndex;
                        charDataArray.forEach((item, index) => {{
                            const span = document.createElement('span'); span.className = 'char'; span.innerText = item.char; span.style.backgroundColor = item.bg; span.dataset.index = index;
                            span.addEventListener('mousedown', (e) => {{
                                if (!knifeMode) return; e.stopPropagation(); 
                                const clickedIdx = parseInt(e.target.dataset.index); if (clickedIdx === 0) return;
                                const currentData = getCharData(div);
                                const part1 = currentData.slice(0, clickedIdx); const part2 = currentData.slice(clickedIdx);
                                const pX = parseFloat(div.style.left); const pY = parseFloat(div.style.top);
                                div.remove();
                                createMagnet(part1, pX, pY); createMagnet(part2, pX + e.target.offsetLeft + 5, pY + 15);
                            }});
                            div.appendChild(span);
                        }});

                        div.addEventListener('mousedown', (e) => {{
                            if (knifeMode) return;
                            if (glueMode) {{
                                e.stopPropagation();
                                if (!glueTarget) {{ glueTarget = div; div.classList.add('glue-selected'); }} 
                                else if (glueTarget !== div) {{
                                    const data1 = getCharData(glueTarget); const data2 = getCharData(div);
                                    const t1X = parseFloat(glueTarget.style.left); const t2X = parseFloat(div.style.left);
                                    const combinedData = t1X <= t2X ? data1.concat(data2) : data2.concat(data1);
                                    const newX = Math.min(t1X, t2X); const newY = parseFloat(glueTarget.style.top);
                                    glueTarget.remove(); div.remove(); glueTarget = null;
                                    createMagnet(combinedData, newX, newY);
                                }} else {{ clearGlueTarget(); }}
                                return;
                            }}
                            e.preventDefault(); div.style.zIndex = ++zIndex; let pos3 = e.clientX, pos4 = e.clientY;
                            document.onmouseup = () => {{ document.onmouseup = null; document.onmousemove = null; }};
                            document.onmousemove = (ev) => {{
                                ev.preventDefault(); let pos1 = pos3 - ev.clientX; let pos2 = pos4 - ev.clientY; pos3 = ev.clientX; pos4 = ev.clientY;
                                div.style.top = (div.offsetTop - pos2) + "px"; div.style.left = (div.offsetLeft - pos1) + "px";
                            }};
                        }});
                        canvas.appendChild(div);
                    }}

                    shuffleBtn.addEventListener('click', () => {{
                        let allMagnets = Array.from(document.querySelectorAll('.magnet'));
                        let dataList = allMagnets.map(m => getCharData(m));
                        for (let i = dataList.length - 1; i > 0; i--) {{
                            const j = Math.floor(Math.random() * (i + 1)); [dataList[i], dataList[j]] = [dataList[j], dataList[i]];
                        }}
                        canvas.innerHTML = ''; clearGlueTarget();
                        let currentY = 50; let currentX = 50; let countInRow = 0; let targetInRow = Math.floor(Math.random() * 3) + 3;
                        dataList.forEach((charData) => {{
                            createMagnet(charData, currentX, currentY); currentX += (charData.length * 28) + 30; countInRow++;
                            if (countInRow >= targetInRow || currentX > canvas.offsetWidth - 150) {{
                                currentY += 75; currentX = 40 + Math.random() * 60; countInRow = 0; targetInRow = Math.floor(Math.random() * 3) + 3;
                            }}
                        }});
                    }});

                    initialWords.forEach((word, i) => {{
                        const x = 30 + (i % 6) * 110 + Math.random() * 30; const y = 30 + Math.floor(i / 6) * 70 + Math.random() * 30;
                        const initialColor = colorPalette[Math.floor(Math.random() * colorPalette.length)];
                        const charDataArray = Array.from(word).map(c => ({{ char: c, bg: initialColor }}));
                        createMagnet(charDataArray, x, y);
                    }});
                </script>
            </body>
            </html>
            """
            components.html(custom_html_2, height=750)

# ---------------------------------------------------------
# TAB 3: The Automaton (무의식의 방 & 불타는 캔버스 - Text Only Burn Edition)
# ---------------------------------------------------------
with tab3:
    st.markdown("""
    <div class="instruction-box">
        <b>[자동 기술 지침: 파편의 증발]</b><br>
        - <b>무의식의 흐름:</b> 텍스트를 입력하세요. 5초간 키보드가 멈추면 <b>최근 당신이 쏟아낸 3~5개의 어절</b>만 붉게 타오르며 사라집니다.<br>
        - <b>이성의 차단:</b> 백스페이스(수정)를 누르려면 3~5번을 미친 듯이 연타해야 겨우 한 글자가 지워집니다.<br>
        - 캔버스의 틀은 견고합니다. 사라진 파편은 우연의 흔적으로 남으니 계속 나아가세요.
    </div>
    """, unsafe_allow_html=True)

    automaton_html_updated = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @font-face {
            font-family: 'Eulyoo1945-Regular';
            src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
        }
        body { font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 0; background: #fafafa; user-select: none; }
        
        #progress-container { width: 100%; height: 8px; background: #ddd; }
        #progress-bar { width: 100%; height: 100%; background: #000; transition: width 0.1s linear, background 1s ease; }
        .danger #progress-bar { background: #ff4d4d; }
        
        /* 캔버스 래퍼: 여기서 견고한 테두리와 그림자를 담당 */
        #editor-wrapper { 
            position: relative; width: 100%; height: 500px; 
            border: 3px solid #000; box-shadow: 4px 4px 0px #000; 
            background: transparent; box-sizing: border-box; overflow: hidden;
        }
        
        /* 입력창과 오버레이는 완전히 겹쳐지게 설정 */
        textarea, #overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            padding: 20px; box-sizing: border-box; margin: 0;
            font-family: 'Eulyoo1945-Regular', serif; font-size: 1.5rem; line-height: 1.8; 
            border: none; outline: none; background: transparent;
            white-space: pre-wrap; word-wrap: break-word; overflow-y: auto;
        }
        
        textarea { color: #000; resize: none; z-index: 2; cursor: text; }
        /* 오버레이는 평소엔 투명하고 이벤트 무시 */
        #overlay { color: transparent; z-index: 1; pointer-events: none; }
        
        /* 특정 파편만 타들어가는 마법의 CSS */
        .burning-text {
            display: inline-block;
            animation: burnTextOnly 1.5s forwards ease-in;
        }
        
        @keyframes burnTextOnly {
            0% { color: #ff4d4d; text-shadow: 0 0 0px #ff0000; filter: blur(0px); opacity: 1; transform: translateY(0px); }
            40% { color: #ff3333; text-shadow: 0 -3px 8px #ff9900; filter: blur(2px); transform: translateY(-2px); }
            100% { color: transparent; text-shadow: 0 -15px 25px #ff0000; filter: blur(6px); opacity: 0; transform: translateY(-8px); }
        }
        
        #bs-warning { position: absolute; top: 20px; right: 20px; color: #ff4d4d; font-weight: bold; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 100; }
    </style>
    </head>
    <body>
        <div id="progress-container"><div id="progress-bar"></div></div>
        
        <div id="editor-wrapper">
            <div id="overlay"></div>
            <textarea id="auto-text" placeholder="의식의 검열을 멈추고 쏟아내세요. 5초 뒤 최근 쓴 단어들이 불탑니다..."></textarea>
            <div id="bs-warning">이성이 저항합니다! 연타하세요!</div>
        </div>

        <script>
            const textarea = document.getElementById('auto-text');
            const overlay = document.getElementById('overlay');
            const progressBar = document.getElementById('progress-bar');
            const bsWarning = document.getElementById('bs-warning');
            
            const TIME_LIMIT = 5000; // 5초
            let timerInterval;
            let timeRemaining = TIME_LIMIT;
            let isBurning = false;
            
            let bsCount = 0;
            let bsRequired = Math.floor(Math.random() * 3) + 3;

            function startTimer() {
                clearInterval(timerInterval);
                timeRemaining = TIME_LIMIT;
                isBurning = false;
                
                document.getElementById('progress-container').classList.remove('danger');
                progressBar.style.width = '100%';

                timerInterval = setInterval(() => {
                    if(textarea.value.trim() === '') return; 

                    timeRemaining -= 100;
                    const percentage = (timeRemaining / TIME_LIMIT) * 100;
                    progressBar.style.width = percentage + '%';

                    if (timeRemaining <= 2000) {
                        document.getElementById('progress-container').classList.add('danger');
                    }

                    if (timeRemaining <= 0) {
                        clearInterval(timerInterval);
                        triggerPartialBurn();
                    }
                }, 100);
            }

            // ❗ 부분 삭제 및 오버레이 애니메이션 로직
            function triggerPartialBurn() {
                if(isBurning) return;
                isBurning = true;
                
                const val = textarea.value;
                const numToDelete = Math.floor(Math.random() * 3) + 3; // 3~5 단어 삭제
                
                // 뒤에서부터 단어 개수를 세어 잘라낼 위치(Index)를 찾는 안전한 로직
                let wordCount = 0;
                let splitIndex = 0;
                let inWord = false;
                
                for(let i = val.length - 1; i >= 0; i--) {
                    if (/\\s/.test(val[i])) {
                        inWord = false;
                    } else {
                        if (!inWord) { wordCount++; inWord = true; }
                    }
                    if (wordCount > numToDelete) {
                        splitIndex = i + 1;
                        break;
                    }
                }
                
                const safePart = val.substring(0, splitIndex);
                const burningPart = val.substring(splitIndex);
                
                // 특수문자 안전 처리 (HTML 렌더링용)
                const escapeHTML = (str) => str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                
                // 애니메이션 준비: 입력창 글자는 숨기고, 오버레이에 분리된 텍스트 렌더링
                overlay.innerHTML = `<span style="color: #000;">${escapeHTML(safePart)}</span><span class="burning-text">${escapeHTML(burningPart)}</span>`;
                overlay.scrollTop = textarea.scrollTop; // 스크롤 위치 동기화
                
                textarea.style.color = 'transparent'; // 원본 텍스트 숨김 (테두리는 wrapper에 있으니 영향 없음)
                textarea.disabled = true; // 타는 동안 입력 방지
                
                // 1.5초 후 재가 된 텍스트 제거하고 캔버스 복구
                setTimeout(() => {
                    textarea.value = safePart;
                    textarea.style.color = '#000';
                    textarea.disabled = false;
                    overlay.innerHTML = '';
                    
                    progressBar.style.width = '100%';
                    document.getElementById('progress-container').classList.remove('danger');
                    isBurning = false;
                    textarea.focus();
                    
                    if(textarea.value.trim() !== '') startTimer();
                }, 1500);
            }

            textarea.addEventListener('input', () => {
                if (textarea.composing) { clearInterval(timerInterval); return; }
                if(!isBurning) startTimer();
            });

            textarea.addEventListener('compositionstart', () => { textarea.composing = true; clearInterval(timerInterval); });
            textarea.addEventListener('compositionend', () => { textarea.composing = false; if(!isBurning) startTimer(); });

            // 스크롤 동기화 (오버레이와 텍스트 에어리어가 같이 움직이도록)
            textarea.addEventListener('scroll', () => { overlay.scrollTop = textarea.scrollTop; });

            textarea.addEventListener('keydown', (e) => {
                if (isBurning) { e.preventDefault(); return; }

                if (e.key === 'Backspace') {
                    if (textarea.composing) return;

                    bsWarning.style.opacity = '1';
                    setTimeout(() => bsWarning.style.opacity = '0', 500);

                    bsCount++;
                    if (bsCount < bsRequired) {
                        e.preventDefault();
                    } else {
                        bsCount = 0;
                        bsRequired = Math.floor(Math.random() * 3) + 3;
                    }
                } else {
                    bsWarning.style.opacity = '0';
                    if(!isBurning) startTimer();
                }
            });
        </script>
    </body>
    </html>
    """
    components.html(automaton_html_updated, height=600)
    
# --- 하단 🏺 따로 움직이는 파편들 (공통) ---
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
