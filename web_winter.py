import streamlit as st
from google import genai

# 1. 페이지 설정
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# 2. 스트림릿 금고(Secrets)에서 키 가져오기
# (에러 방지를 위해 직접 적지 않고 금고에서만 가져옴)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("스트림릿 'Secrets' 설정에서 GOOGLE_API_KEY를 확인해주세요!")
    st.stop()

# 3. 페르소나 설정
winter_persona = """
너의 이름은 '한겨울'이야. 너는 20대 초반 여사친이야.
나를 부를 때는 '파이'라고 불러줘. 츤데레 성격이고 짧게 카톡하듯 대답해.
절대 AI 티 내지 마!
"""

# 4. 화면 UI
st.title("❄️ 한겨울 라이브 챗")
st.divider()

# 5. 세션 관리
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)
    st.session_state.chat_history = []
    st.session_state.chat_session = st.session_state.client.chats.create(
        model="gemini-2.5-flash",
        config={"system_instruction": winter_persona}
    )

# 6. 대화 기록 표시
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# 7. 채팅 입력
if user_input := st.chat_input("겨울이에게 메시지 보내기"):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append(("user", user_input))

    response = st.session_state.chat_session.send_message(user_input)
    
    with st.chat_message("assistant", avatar="❄️"):
        st.markdown(response.text)
    st.session_state.chat_history.append(("assistant", response.text))
