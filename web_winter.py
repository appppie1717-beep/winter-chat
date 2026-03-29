import streamlit as st
from google import genai

# 1. 페이지 설정 및 메뉴 숨기기 (이게 제일 위에 있어야 함)
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# --- 오른쪽 위 메뉴랑 하단 문구 숨기기 (파이가 원했던 깔끔 마감!) ---
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

# 5. 세션 관리 및 엔진 초기화 (엔진이 꺼지지 않도록 세션에 저장)
if "chat_session" not in st.session_state:
    # 클라이언트를 세션에 저장하지 않고 직접 호출해서 세션을 만들어
    client = genai.Client(api_key=api_key)
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
    # 유저 메시지 표시
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append(("user", user_input))

    # 겨울이 대답 받기
    response = st.session_state.chat_session.send_message(user_input)
    
    # 겨울이 메시지 표시
    with st.chat_message("assistant", avatar="❄️"):
        st.markdown(response.text)
    st.session_state.chat_history.append(("assistant", response.text))
