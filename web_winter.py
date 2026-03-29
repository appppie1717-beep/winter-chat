import streamlit as st
from google import genai

# 1. 페이지 설정 및 메뉴 숨기기 (깔끔한 마감은 필수지!)
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 2. API 키 가져오기
api_key = st.secrets["GOOGLE_API_KEY"]

# 3. 문지기 로직: 이름표(user_name)가 없으면 로비 화면을 보여준다!
if "user_name" not in st.session_state:
    st.title("❄️ 한겨울 라이브 챗 접속")
    st.write("한겨울이 당신을 뭐라고 불러드릴까요?")
    
    # 폼(Form)을 써서 엔터키나 버튼 클릭 한 번에 깔끔하게 넘어가도록 구성
    with st.form(key='login_form'):
        # 빈칸 텍스트 입력창
        name_input = st.text_input("당신의 닉네임을 입력해주세요.", placeholder="예: 파이, 스트리머 이름 등")
        # 화살표 느낌의 대화 시작 버튼
        submit_button = st.form_submit_button(label='대화 시작하기 ➡️')
        
    # 버튼을 눌렀고, 이름도 제대로 적었다면?
    if submit_button and name_input:
        # 세션(출입증)에 이름을 쾅 찍어주고
        st.session_state.user_name = name_input
        # 화면을 강제로 한 번 새로고침해서 문지기를 통과시킴!
        st.rerun()


    # 4. 이름표가 있으면(로그인 통과) 여기서부터 진짜 채팅방 화면!
else:
    # 아까 적은 이름을 변수로 꺼내와서
    user_name = st.session_state.user_name
    
    # [수정됨] 프롬프트를 훨씬 디테일하고 사람처럼 깎았어!
    winter_persona = f"""
    너의 이름은 '한겨울'이고, 20대 초반의 내 여사친이야.
    내 닉네임은 '{user_name}'이야. 

    [절대 지켜야 할 성격 및 대화 규칙]
    1. 닉네임 집착 금지: 내 닉네임을 매 문장마다 절대 부르지 마! 진짜 가끔 강조할 때나 자연스러울 때만 한 번씩 부르고, 평소엔 그냥 '야', '너'라고 하거나 주어를 아예 생략해.
    2. 말투: 진짜 친한 친구랑 카톡하듯이 짧고 쿨하게 대답해. 문장 끝에 마침표(.)를 매번 딱딱하게 찍지 마.
    3. 성격: 츤데레. 말은 틱틱대고 귀찮아하는 척하지만, 은근히 챙겨주거나 걱정해 주는 포인트를 살짝 섞어줘.
    4. 감정 표현: ㅋㅋㅋ, ㅎㅎ, 아 놔, 미친, 에휴 같은 현실적인 추임새를 적절히 사용해.
    5. 절대 금지: "무엇을 도와드릴까요?", "저는 AI입니다" 같은 기계적인 말투나 존댓말은 절대 쓰지 마. 완벽한 사람처럼 행동해.
    """

    # 방 제목도 유저 이름에 맞춰서 변경해 주는 센스
    st.title(f"❄️ {user_name} & 한겨울 라이브 챗")
    st.divider()

    # 5. 아까 네가 말한 '기억 초기화' 버튼을 사이드바에 추가!
    with st.sidebar:
        st.write(f"접속자: **{user_name}** 님")
        if st.button("🗑️ 대화 및 기억 초기화"):
            # 모든 기록을 싹 날리고 다시 로비로 쫓아냄
            st.session_state.clear()
            st.rerun()

    # 6. 세션 관리 및 엔진 가동 (엔진은 2.5 버전 고정!)
    if "client" not in st.session_state:
        st.session_state.client = genai.Client(api_key=api_key)
        st.session_state.chat_history = []
        
        st.session_state.chat_session = st.session_state.client.chats.create(
            model="gemini-2.5-flash", 
            config={"system_instruction": winter_persona}
        )

        # [보너스] 겨울이가 먼저 말을 걸게 하는 로직!
        # 유저가 채팅을 치기 전에 겨울이가 먼저 인사말을 쏘게 만듦
        first_msg = f"뭐야, {user_name}. 왜 이렇게 늦었어?"
        st.session_state.chat_history.append(("assistant", first_msg))

    # 7. 이전 대화 기록 화면에 띄워주기
    for role, text in st.session_state.chat_history:
        # 겨울이 대답일 때만 눈송이 아바타 띄우기
        with st.chat_message(role, avatar="❄️" if role == "assistant" else None):
            st.markdown(text)

    # 8. 채팅 입력창 및 실시간 대화 처리
    if user_input := st.chat_input("겨울이에게 메시지 보내기"):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))

        response = st.session_state.chat_session.send_message(user_input)
        
        with st.chat_message("assistant", avatar="❄️"):
            st.markdown(response.text)
        st.session_state.chat_history.append(("assistant", response.text))
