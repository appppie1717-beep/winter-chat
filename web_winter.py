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

# 2. 스트림릿 금고에서 열쇠 꺼내오기! (보안 완벽 유지)
api_key = st.secrets["GOOGLE_API_KEY"]
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

# 3. DB 접속 도구(Client) 만들기
# (에러의 원인이었던 init_supabase 함수 호출과 캐시를 아예 영구 삭제함!)
# 수파베이스와 제미나이 엔진을 헷갈리는 이름 없이 다이렉트로 바로 꽂아버립니다.
supabase: Client = create_client(supabase_url, supabase_key)
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

    # 6. 대망의 [기억력 복원 및 엔진 가동] 로직 (세션 꼬임 완벽 해결)
    if "chat_history" not in st.session_state:
        # DB 창고에서 '내 이름(user_name)'으로 된 예전 대화 기록 싹 다 가져오기
        response = supabase.table("chat_memory").select("*").eq("user_name", user_name).order("id").execute()
        db_history = response.data

        st.session_state.chat_history = []
        
        # 가져온 DB 기록을 화면용으로 복원
        for row in db_history:
            st.session_state.chat_history.append((row["role"], row["message"]))

        # 만약 DB가 텅 비어있다? (= 처음 왔거나 방금 초기화했다면) 선톡 날리기!
        if not db_history:
            first_msg = f"뭐야, {user_name}. 왜 이렇게 늦었어?"
            st.session_state.chat_history.append(("assistant", first_msg))
            
            # 이 첫 인사도 DB에 저장!
            supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": first_msg}).execute()

    # 7. 이전 대화 기록 화면에 띄워주기
    for role, text in st.session_state.chat_history:
        with st.chat_message(role, avatar="❄️" if role == "assistant" else None):
            st.markdown(text)

    # 8. 실시간 채팅 및 DB 저장 로직 (엔진을 매번 새로 만들어서 Closed 에러 원천 차단!)
    if user_input := st.chat_input("겨울이에게 메시지 보내기"):
        # 내 채팅 화면 띄우고 DB 저장
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "user", "message": user_input}).execute()

        # [핵심] 제미나이 뇌에 꽂아줄 과거 기억 세팅 (방금 친 채팅 제외)
        gemini_history = []
        for r, t in st.session_state.chat_history[:-1]: 
            gemini_role = "model" if r == "assistant" else "user"
            gemini_history.append({"role": gemini_role, "parts": [{"text": t}]})

        # 방금 막 생성된 쌩쌩한 엔진으로 대화방 임시 생성 (오류 해결의 마스터키)
        temp_chat = client.chats.create(
            model="gemini-2.5-flash", 
            config={"system_instruction": winter_persona},
            history=gemini_history
        )
        
        # 겨울이 대답 받아오기
        response = temp_chat.send_message(user_input)
        
        # 겨울이 대답 화면 띄우고 DB 저장
        with st.chat_message("assistant", avatar="❄️"):
            st.markdown(response.text)
        st.session_state.chat_history.append(("assistant", response.text))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": response.text}).execute()
