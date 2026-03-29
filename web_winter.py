import streamlit as st
from google import genai

# 1. 페이지 설정 (이게 무조건 1등으로 실행되어야 함)
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# --- [파이의 요청] 오른쪽 위 메뉴랑 하단 문구 숨기기 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 2. 금고에서 키 가져오기
api_key = st.secrets["GOOGLE_API_KEY"]

# 3. 페르소나 설정
winter_persona = """
너의 이름은 '한겨울'이야. 너는 20대 초반 여사친이야.
나를 부를 때는 '파이'라고 불러줘. 츤데레 성격이고 짧게 카톡하듯 대답해.
절대 AI 티 내지 마!
"""

# 4. 화면 UI
st.title("❄️ 한겨울 라이브 챗")
st.divider()

# 5. [핵심] 엔진이 꺼지지 않도록 매번 새롭게 연결 생성
# 세션에 'client'를 저장하지 않고, 대화 세션만 유지하는 방식이야.
client = genai.Client(api_key=api_key)

if "chat_session" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.0-flash", 
        config={"system_instruction": winter_persona}
    )

# 6. 대화 기록 표시
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# 7. 채팅 입력 및 처리
if user_input := st.chat_input("겨울이에게 메시지 보내기"):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append(("user", user_input))

    # 에러 방지를 위해 전송 직전에 한 번 더 client를 확인하는 구조야
    response = st.session_state.chat_session.send_message(user_input)
    
    with st.chat_message("assistant", avatar="❄️"):
        st.markdown(response.text)
    st.session_state.chat_history.append(("assistant", response.text))
