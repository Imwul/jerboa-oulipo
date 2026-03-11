import streamlit as st
import streamlit.components.v1 as components
from kiwipiepy import Kiwi
import random
import os
import re
import json

# --- 1. 페이지 설정 (최상단 고정) ---
st.set_page_config(page_title="Jerboa Circle", layout="wide")

# --- 2. 🎨 디자인 및 폰트 로드 (CSS) ---
st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }

    /* 폰트 4종 로드 */
    @font-face { font-family: 'Eulyoo1945'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff'); }
    @font-face { font-family: 'GmarketSans'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff'); }
    @font-face { font-family: 'KyoboHandwriting'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_20-04@1.0/KyoboHandwriting2019.woff') format('woff'); }
    @font-face { font-family: 'DungGeunMo'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/DungGeunMo.woff') format('woff'); }

    /* 기본 텍스트 설정 */
    html, body, [data-testid="stHeader"], .stMarkdown, p, span, div { 
        font-family: 'Eulyoo1945', serif; 
        color: #000000;
    }

    h1 {
        font-family: 'Trattatello', 'Apple Chancery', cursive !important;
        font-size: 3.8rem !important; color: #000000 !important;
        text-align: center; margin-bottom: 1.5rem !important; padding-top: 1rem !important;
    }

    /* ❗ 입력창(해부대) 설정: 검은 배경에 하얀 글씨 */
    .stTextArea textarea, .stTextInput input {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        font-family: 'Eulyoo1945', serif !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }
    
    /* 지침서 박스 */
    .instruction-box {
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem; color: #000000 !important;
    }

    /* 하단 사전 파편 애니메이션 */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(1.5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    .fragment-tag {
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 5s ease-in-out infinite;
        font-weight: bold; cursor: default; color: #000000 !important;
    }

    /* 버튼 설정 */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border-radius: 0px !important; width: 100% !important;
        height: 3.5rem; font-size: 1.2rem !important;
    }
    div.stButton > button p, div[data-testid="stFormSubmitButton"] > button p { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. 형태소 분석기 및 사전 로드 ---
@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각", "미학", "구토", "이방인", "페스트", "시시포스", "환영", "균열", "기하학", "태엽", "미궁", "내장", "잿더미", "권태", "맹목"]

NOUN_DICT = load_oulipo_dict()
WASHED_COLORS = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]

# --- 4. 메인 화면 ---
st.title("Jerboa Circle: Surrealist Workshop")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏺 Oulipo (S+N)", "🔪 Dissector (마그넷)", "🔥 Automaton (자동기술)", "⬛ Erasure (소거)", "📜 Cadavre (시체)", "🗼 Babel (오독)"
])

# ==========================================
# TAB 1: Oulipo Engine (S+N)
# ==========================================
with tab1:
    st.markdown("""
    <div class="instruction-box">
        <b>[울리포 엔진 가동 지침]</b><br>
        - <b>해부대:</b> 문장을 입력하세요. <b>줄 바꿈</b>과 <b>단어 사이의 여백</b>은 엄격히 보존됩니다.<br>
        - <b>S+N 거리:</b> 명사를 사전에서 찾아 N단계 뒤의 단어로 치환합니다.<br>
        - <b>성역 보호:</b> <b>&lt;단어&gt;</b> 와 같이 꺽쇠로 감싼 부분은 변하지 않는 '성역'이 됩니다.<br>
        - <b>변환 확률:</b> 문장 속 모든 명사를 바꿀지, 일부만 무작위로 치환할지 결정합니다.
    </div>
    """, unsafe_allow_html=True)
    user_input = st.text_area("해부대", placeholder="나는 <심연을> 보았다.", height=150, key="engine_input")
    c1, c2 = st.columns(2); shift_val = c1.slider("S+N 거리", 1, 100, 7); prob_val = c2.slider("변환 확률 (%)", 0, 100, 100)
    c3, c4 = st.columns(2); b_val = c3.slider("진동", 0.0, 0.6, 0.15); t_val = c4.slider("비틀림", 0, 30, 10)

    def transform_logic(line, shift, prob):
        parts = re.split(r'(<.*?>)', line)
        d_len = len(NOUN_DICT)
        res = []
        for p in parts:
            if p.startswith('<') and p.endswith('>'): res.append(p[1:-1])
            elif not p.strip(): res.append(p)
            else:
                l_ws = re.match(r'^\s*', p).group() if re.match(r'^\s*', p) else ""
                r_ws = re.search(r'\s*$', p).group() if re.search(r'\s*$', p) else ""
                tokens = kiwi.tokenize(p.strip())
                sub = []
                for t in tokens:
                    if t.tag.startswith('N') and (hash(t.form) % 100) < prob:
                        if t.form in NOUN_DICT: idx = (NOUN_DICT.index(t.form) + shift) % d_len; new_w = NOUN_DICT[idx]
                        else: random.seed(hash(t.form)); new_w = NOUN_DICT[random.randint(0, d_len-1)]
                        sub.append((new_w, 'NNG'))
                    else: sub.append((t.form, t.tag))
                res.append(l_ws + kiwi.join(sub) + r_ws)
        return "".join(res)

    if st.button("✨ 문장 재단하기", key="btn1"):
        if user_input:
            lines = user_input.split('\n')
            html = '<div style="line-height:2.3; padding:25px; border:3px solid #000; background:#FFF; white-space:pre-wrap;">'
            for line in lines:
                if not line.strip(): html += '\n'; continue
                tr = transform_logic(line, shift_val, prob_val)
                for char in tr:
                    if char == ' ': html += '&nbsp;'
                    else:
                        fs = 1.4 + random.uniform(-b_val, b_val); rt = random.uniform(-t_val, t_val)
                        html += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rt}deg); font-weight:bold;">{char}</span>'
                html += '\n'
            st.markdown(html + '</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: The Dissector (마그넷 해부학)
# ==========================================
with tab2:
    st.markdown("<div class='instruction-box'><b>[마그넷 지침]</b> 텍스트를 마그넷으로 만들어 캔버스에 배치하세요. 칼로 자르고 풀로 붙일 수 있습니다.</div>", unsafe_allow_html=True)
    user_input_2 = st.text_area("해부대 (마그넷 생성)", placeholder="내용을 입력하세요.", height=150, key="magnet_input")
    if st.button("🧲 캔버스 생성"):
        if user_input_2:
            words_json = json.dumps([w for w in re.split(r'\s+', user_input_2) if w])
            colors_json = json.dumps(WASHED_COLORS)
            custom_html = f"""
            <div id="toolbar" style="background:#000; padding:10px; display:flex; gap:10px; justify-content:center;">
                <button onclick="m=0" style="padding:5px 15px; cursor:pointer;">🖐️ 이동</button>
                <button onclick="m=1" style="padding:5px 15px; cursor:pointer; background:#ff4d4d; color:#fff;">🔪 칼</button>
                <button onclick="m=2" style="padding:5px 15px; cursor:pointer; background:#4d79ff; color:#fff;">🧴 풀</button>
                <button onclick="shuffle()" style="padding:5px 15px; cursor:pointer; background:#ffe3b3;">✨ 셔플</button>
            </div>
            <div id="can" style="width:100%; height:500px; background:#fafafa; border:3px solid #000; position:relative; overflow:hidden;"></div>
            <script>
                const words = {words_json}; const colors = {colors_json}; const can = document.getElementById('can');
                let m = 0; let glueTarget = null; let z = 10;
                function create(txt, x, y, bg) {{
                    const d = document.createElement('div'); d.className='mag'; d.style.cssText=`position:absolute; left:${{x}}px; top:${{y}}px; padding:10px; border:2px solid #000; background:${{bg}}; cursor:grab; font-weight:bold; box-shadow:3px 3px 0 #000; z-index:${{z++}}; white-space:nowrap;`;
                    d.innerText = txt;
                    d.onmousedown = (e) => {{
                        if(m===1) {{ const ws=d.innerText; if(ws.length>1) {{ d.remove(); create(ws.slice(0,Math.floor(ws.length/2)), e.clientX, e.clientY, bg); create(ws.slice(Math.floor(ws.length/2)), e.clientX+20, e.clientY+20, bg); }} }}
                        else if(m===2) {{ if(!glueTarget) {{ glueTarget=d; d.style.outline='3px solid #4d79ff'; }} else {{ glueTarget.innerText += d.innerText; d.remove(); glueTarget.style.outline='none'; glueTarget=null; }} }}
                        else {{ 
                            let ox=e.clientX-d.offsetLeft, oy=e.clientY-d.offsetTop;
                            document.onmousemove=(ev)=>{{ d.style.left=(ev.clientX-ox)+'px'; d.style.top=(ev.clientY-oy)+'px'; }};
                            document.onmouseup=()=>{{ document.onmousemove=null; }};
                        }}
                    }};
                    can.appendChild(d);
                }}
                words.forEach((w,i)=>create(w, 50+(i%5)*120, 50+Math.floor(i/5)*70, colors[i%colors.length]));
                function shuffle() {{ const ms=document.querySelectorAll('.mag'); ms.forEach(mag=>{{ mag.style.left=Math.random()*800+'px'; mag.style.top=Math.random()*400+'px'; }}); }}
            </script>
            """
            components.html(custom_html, height=600)

# ==========================================
# TAB 3: The Automaton (불타는 캔버스)
# ==========================================
with tab3:
    st.markdown("<div class='instruction-box'><b>[자동 기술 지침]</b> 5초간 멈추면 최근 쏟아낸 3~5어절이 붉게 타오르며 사라집니다. 백스페이스는 연타해야 작동합니다.</div>", unsafe_allow_html=True)
    auto_html = """
    <div id="p-c" style="width:100%; height:8px; background:#ddd;"><div id="p-b" style="width:100%; height:100%; background:#000; transition:width 0.1s linear;"></div></div>
    <div id="e-w" style="position:relative; width:100%; height:400px; border:3px solid #000; margin-top:10px; background:#fff;">
        <div id="ov" style="position:absolute; top:0; left:0; width:100%; height:100%; padding:20px; font-size:1.5rem; line-height:1.8; color:transparent; white-space:pre-wrap; pointer-events:none; z-index:1; font-family:serif;"></div>
        <textarea id="at" style="position:absolute; top:0; left:0; width:100%; height:100%; padding:20px; font-size:1.5rem; line-height:1.8; border:none; outline:none; background:transparent; resize:none; z-index:2; color:#000; font-family:serif;" placeholder="의식을 쏟아내세요..."></textarea>
    </div>
    <style>
        .burn { animation: b-a 1.5s forwards; display:inline-block; }
        @keyframes b-a { 0% { color:#ff4d4d; opacity:1; } 100% { color:transparent; text-shadow:0 -15px 20px #ff0000; opacity:0; transform:translateY(-10px); } }
    </style>
    <script>
        const ta = document.getElementById('at'); const ov = document.getElementById('ov'); const pb = document.getElementById('p-b');
        let timer, left = 5000, bsCount = 0;
        function trBurn() {
            const v = ta.value; const ws = v.split(/\\s+/); const num = Math.floor(Math.random()*3)+3;
            const safe = ws.slice(0, Math.max(0, ws.length - num)).join(' ');
            const burn = ws.slice(Math.max(0, ws.length - num)).join(' ');
            ov.innerHTML = `<span>${safe}</span><span class="burn"> ${{burn}}</span>`;
            ta.style.color = 'transparent';
            setTimeout(() => { ta.value = safe; ta.style.color = '#000'; ov.innerHTML = ''; left = 5000; pb.style.width = '100%'; }, 1500);
        }
        ta.addEventListener('input', () => {
            clearInterval(timer); left = 5000; pb.style.width = '100%';
            timer = setInterval(() => { if(!ta.value.trim()) return; left -= 100; pb.style.width = (left/5000*100) + '%'; if(left <= 0) { clearInterval(timer); trBurn(); } }, 100);
        });
        ta.addEventListener('keydown', (e) => { if(e.key==='Backspace') { bsCount++; if(bsCount < 4) e.preventDefault(); else bsCount=0; } });
    </script>
    """
    components.html(auto_html, height=500)

# ==========================================
# TAB 4: The Erasure (블랙아웃)
# ==========================================
with tab4:
    st.markdown("<div class='instruction-box'><b>[소거의 미학]</b> 텍스트 위를 드래그하여 불필요한 단어를 지워 시를 발견하세요.</div>", unsafe_allow_html=True)
    erasure_in = st.text_area("원본 텍스트", value="이성은 언제나 우리를 배신한다. 논리는 껍데기에 불과하다. 진정한 구원은 무의식의 심연 속에 있다.", height=120)
    if st.button("⬛ 소거 캔버스 생성"):
        words_json = json.dumps(erasure_in.split())
        erasure_html = f"""
        <div id="can" style="padding:30px; border:3px solid #000; background:#fff; line-height:2.5; font-size:1.5rem; cursor:crosshair; min-height:300px;"></div>
        <script>
            const ws = {words_json}; const can = document.getElementById('can');
            let drag = false;
            can.onmousedown = () => drag = true; document.onmouseup = () => drag = false;
            ws.forEach(w => {{
                const s = document.createElement('span'); s.innerText = w + ' '; s.style.padding='2px 5px';
                s.onmousedown = () => s.style.background = s.style.background==='black'?'transparent':'black';
                s.onmouseenter = () => {{ if(drag) s.style.background='black'; }};
                can.appendChild(s);
            }});
        </script>
        """
        components.html(erasure_html, height=500)

# ==========================================
# TAB 5: Cadavre Exquis (우아한 시체)
# ==========================================
with tab5:
    st.markdown("<div class='instruction-box'><b>[우아한 시체]</b> 문장을 쓰고 넘기면 문장은 가려지고 마지막 3어절만 보입니다. 앞의 파편에 기대어 다음 문장을 쓰세요.</div>", unsafe_allow_html=True)
    if 'corpse' not in st.session_state: st.session_state.corpse = []
    if st.session_state.corpse:
        last = st.session_state.corpse[-1].split(); show = " ".join(last[-3:]) if len(last)>=3 else " ".join(last)
        st.markdown(f"<h3 style='text-align: center; color: #ff4d4d;'>... {show}</h3>", unsafe_allow_html=True)
    with st.form(key='corpse_form', clear_on_submit=True):
        new_line = st.text_input("다음 문장 이어쓰기:")
        if st.form_submit_button("✒️ 종이 접어 넘기기") and new_line.strip():
            st.session_state.corpse.append(new_line.strip()); st.rerun()
    c1, c2 = st.columns(2)
    if c1.button("📜 종이 펼치기"): st.write(" ".join(st.session_state.corpse))
    if c2.button("🗑️ 초기화"): st.session_state.corpse = []; st.rerun()

# ==========================================
# TAB 6: The Babel Glitch (오독의 시학)
# ==========================================
with tab6:
    st.markdown("<div class='instruction-box'><b>[바벨의 균열]</b> 4가지 한글 폰트가 실시간으로 뒤섞입니다. 슬라이더를 조작해 활자의 해체를 감상하세요.</div>", unsafe_allow_html=True)
    b_in = st.text_area("해부할 문장", placeholder="나는 오늘 아침 거울을 보며 깊은 절망을 느꼈다.", height=150)
    
    if 'b_raw' not in st.session_state: st.session_state.b_raw = ""
    if st.button("🗼 바벨탑 무너뜨리기"):
        if b_in:
            toks = kiwi.tokenize(b_in)
            res = []
            for t in toks:
                if t.tag.startswith('N') and random.random() > 0.8: res.append((random.choice(NOUN_DICT), t.tag))
                else: res.append((t.form, t.tag))
            st.session_state.b_raw = kiwi.join(res)
    
    if st.session_state.b_raw:
        st.divider()
        c1, c2 = st.columns(2); b_t = c1.slider("비틀림", 0, 45, 15); b_s = c2.slider("진동", 0.0, 1.0, 0.3)
        # 폰트 클래스 믹스
        f_list = ["f-eulyoo", "f-gmarket", "f-kyobo", "f-pixel"]
        res_h = "<div style='padding:30px; border:3px solid #000; background:#fff; line-height:2.5;'>"
        for char in st.session_state.b_raw:
            if char == ' ': res_h += '&nbsp;'
            else:
                f = random.choice(f_list) if random.random() > 0.6 else f_list[0]
                rt = random.uniform(-b_t, b_t); sz = 1.4 + random.uniform(-b_s, b_s)
                # ❗ 폰트 적용을 위해 인라인 스타일과 클래스를 동시에 사용
                res_h += f'<span class="{f}" style="font-size:{sz}rem; display:inline-block; transform:rotate({rt}deg); font-weight:bold; color:#000;">{char}</span>'
        st.markdown(res_h + "</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🏺 하단: 사전의 파편들 (Floating Animation)
# ---------------------------------------------------------
st.divider()
st.subheader("🏺 사전의 파편들")
samples = random.sample(NOUN_DICT, min(30, len(NOUN_DICT)))
tag_html = '<div style="text-align:center; padding-bottom: 50px;">'
for s in samples:
    color = random.choice(WASHED_COLORS)
    delay = random.uniform(0, 4)
    tag_html += f'<span class="fragment-tag" style="background-color:{color}; animation-delay:{delay}s;">{s}</span>'
st.markdown(tag_html + '</div>', unsafe_allow_html=True)
