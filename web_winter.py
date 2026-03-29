import streamlit as st
from google import genai
from supabase import create_client, Client

# 1. 페이지 설정 및 메뉴 숨기기 (깔끔한 출고용 마감!)
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 2. 스트림릿 금고에서 열쇠 3개 꺼내오기!
api_key = st.secrets["GOOGLE_API_KEY"]
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

# 3. DB 접속 도구(Client) 만들기
# (에러의 원인이었던 @st.cache_resource 캐시 기능 과감하게 삭제!)
supabase: Client = create_client(supabase_url, supabase_key)
client = genai.Client(api_key=api_key)

supabase: Client = init_supabase()
client = genai.Client(api_key=api_key)

# 4. 문지기 로직 (온보딩: 이름 물어보기)
if "user_name" not in st.session_state:
    st.title("❄️ 한겨울 라이브 챗 접속")
    st.write("한겨울이 당신을 뭐라고 불러드릴까요?")
    
    with st.form(key='login_form'):
        name_input = st.text_input("당신의 닉네임을 입력해주세요.", placeholder="예: 파이, 스트리머 이름 등")
        submit_button = st.form_submit_button(label='대화 시작하기 ➡️')
        
    if submit_button and name_input:
        st.session_state.user_name = name_input
        st.rerun()

# 5. 이름표가 있으면 진짜 채팅방 입장!
else:
    user_name = st.session_state.user_name
    
    # 똑똑해진 츤데레 프롬프트 (이름 강박증 치료 완료)
    winter_persona = f"""
    너의 이름은 '한겨울'이고, 20대 초반의 내 여사친이야.
    내 닉네임은 '{user_name}'이야. 

    [절대 지켜야 할 규칙]
    1. 닉네임 집착 금지: 매 문장마다 부르지 마. 가끔만 부르고 평소엔 '야', '너' 사용.
    2. 말투: 진짜 친한 친구처럼 짧고 쿨하게. 마침표(.) 남발 금지.
    3. 성격: 츤데레. 틱틱대면서도 은근히 챙겨주는 스타일.
    4. 감정 표현: ㅋㅋㅋ, ㅎㅎ, 아 놔, 미친, 에휴 같은 현실적인 추임새 사용.
    5. 기계 말투 절대 금지: "무엇을 도와드릴까요?", "AI입니다" 등 금지.
    """

    st.title(f"❄️ {user_name} & 한겨울 라이브 챗")
    st.divider()

    # 사이드바 (기억 초기화 버튼)
    with st.sidebar:
        st.write(f"접속자: **{user_name}** 님")
        if st.button("🗑️ 대화 및 기억 초기화"):
            # 버튼 누르면 DB에서 이 유저(파이)의 데이터만 싹 삭제!
            supabase.table("chat_memory").delete().eq("user_name", user_name).execute()
            st.session_state.clear()
            st.rerun()

    # 6. 대망의 [기억력 복원 및 엔진 가동] 로직
    if "chat_session" not in st.session_state:
        # DB 창고에서 '내 이름(user_name)'으로 된 예전 대화 기록 싹 다 가져오기
        response = supabase.table("chat_memory").select("*").eq("user_name", user_name).order("id").execute()
        db_history = response.data

        st.session_state.chat_history = []
        gemini_history = [] # 제미나이 뇌에 집어넣을 기억 세트
        
        # 가져온 DB 기록을 화면과 제미나이 뇌에 맞게 분류해서 넣어줌
        for row in db_history:
            role = row["role"]
            text = row["message"]
            st.session_state.chat_history.append((role, text))
            
            # 제미나이 엔진은 'assistant' 대신 'model'이라는 단어를 써서 변환해줌
            gemini_role = "model" if role == "assistant" else "user"
            gemini_history.append({"role": gemini_role, "parts": [{"text": text}]})

        # 만약 DB가 텅 비어있다? (= 처음 왔거나 방금 초기화했다면) 선톡 날리기!
        if not db_history:
            first_msg = f"뭐야, {user_name}. 왜 이렇게 늦었어?"
            st.session_state.chat_history.append(("assistant", first_msg))
            
            # 이 첫 인사도 DB에 저장!
            supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": first_msg}).execute()
            gemini_history.append({"role": "model", "parts": [{"text": first_msg}]})

        # 제미나이 엔진 가동! (이때 과거 기억인 gemini_history를 뇌에 주입함)
        st.session_state.chat_session = client.chats.create(
            model="gemini-2.5-flash", 
            config={"system_instruction": winter_persona},
            history=gemini_history
        )

    # 7. 이전 대화 기록 화면에 띄워주기
    for role, text in st.session_state.chat_history:
        with st.chat_message(role, avatar="❄️" if role == "assistant" else None):
            st.markdown(text)

    # 8. 실시간 채팅 및 DB 저장 로직
    if user_input := st.chat_input("겨울이에게 메시지 보내기"):
        # 내 채팅 화면에 띄우기
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))
        
        # [DB 저장] 내가 친 채팅 수파베이스 장부에 기록!
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "user", "message": user_input}).execute()

        # 겨울이 대답 받아오기
        response = st.session_state.chat_session.send_message(user_input)
        
        # 겨울이 대답 화면에 띄우기
        with st.chat_message("assistant", avatar="❄️"):
            st.markdown(response.text)
        st.session_state.chat_history.append(("assistant", response.text))
        
        # [DB 저장] 겨울이가 친 대답도 수파베이스 장부에 기록!
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": response.text}).execute()
