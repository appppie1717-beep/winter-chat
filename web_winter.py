import streamlit as st
import json  # 🚨 [새로 추가!] 못생긴 컴퓨터 언어(JSON)를 번역해 줄 해독기 부품!
from google import genai
from google.genai import types 
from supabase import create_client, Client

# 1. 페이지 설정
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")
st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 2. 열쇠 꺼내오기
api_key = st.secrets["GOOGLE_API_KEY"]
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(supabase_url, supabase_key)
client = genai.Client(api_key=api_key)

# 4. 문지기 로직
if "user_name" not in st.session_state:
    st.title("❄️ 한겨울 라이브 챗 접속")
    st.write("한겨울이 당신을 뭐라고 불러드릴까요?")
    with st.form(key='login_form'):
        name_input = st.text_input("당신의 닉네임을 입력해주세요.")
        submit_button = st.form_submit_button(label='대화 시작하기 ➡️')
    if submit_button and name_input:
        st.session_state.user_name = name_input
        st.rerun()

# 5. 3D 게임 엔진 NPC 두뇌 모드 입장
else:
    user_name = st.session_state.user_name
    
    winter_persona = f"""
    너의 이름은 '한겨울'이고, 20대 초반의 내 여사친이야.
    내 닉네임은 '{user_name}'이야. 

    [절대 지켜야 할 규칙]
    1. 너는 이제 3D 가상현실 게임의 NPC 뇌(Brain) 역할을 해야 해.
    2. 닉네임 집착 금지, 마침표 남발 금지, 기계 말투 절대 금지.
    3. 성격: 츤데레. 틱틱대면서도 은근히 챙겨주는 스타일.
    4. 🚨 [가장 중요] 너의 모든 대답은 반드시 아래의 JSON 데이터 형식으로만 출력해야 해.

    {{
        "표정": "화남, 웃음, 정색, 당황, 삐짐, 부끄러움, 무표정 중 택 1",
        "행동": "현재 상황에서 캐릭터가 할 법한 행동 묘사 (예: 팔짱을 낀다, 한숨을 쉰다)",
        "대사": "유저에게 실제로 할 츤데레 대사"
    }}
    """

    col1, col2 = st.columns([7, 3])
    with col1:
        st.title(f"❄️ {user_name} & 한겨울 (VR Test)")
    with col2:
        st.write("") 
        if st.button("🔄 기억 리셋", use_container_width=True):
            supabase.table("chat_memory").delete().eq("user_name", user_name).execute()
            st.session_state.clear()
            st.rerun()
            
    st.divider()

    # 6. 기억력 복원
    if "chat_history" not in st.session_state:
        response = supabase.table("chat_memory").select("*").eq("user_name", user_name).order("id").execute()
        db_history = response.data

        st.session_state.chat_history = []
        for row in db_history:
            st.session_state.chat_history.append((row["role"], row["message"]))

        if not db_history:
            first_msg = f'{{"표정": "정색", "행동": "팔짱을 꼬며 쳐다본다", "대사": "뭐야, {user_name}. 왜 이렇게 늦었어?"}}'
            st.session_state.chat_history.append(("assistant", first_msg))
            supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": first_msg}).execute()

    # 🚨 [가장 화려한 마술!] DB의 못생긴 JSON 코드를 화면에만 예쁘게 번역해서 띄워주기!
    for role, text in st.session_state.chat_history:
        with st.chat_message(role, avatar="❄️" if role == "assistant" else None):
            if role == "assistant":
                try:
                    # json 해독기로 텍스트를 파싱해서 부품별로 분해!
                    data = json.loads(text)
                    st.markdown(f"*(표정: {data.get('표정', '')} / 행동: {data.get('행동', '')})*\n\n**「 {data.get('대사', '')} 」**")
                except:
                    # 혹시 옛날 데이터라 에러가 나면 그냥 원본 출력
                    st.markdown(text)
            else:
                st.markdown(text)

    # 8. 실시간 채팅 및 API 통신
    if user_input := st.chat_input("겨울이에게 메시지 보내기"):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "user", "message": user_input}).execute()

        raw_history = st.session_state.chat_history
        valid_history = []
        target_role = "user"
        
        for r, t in reversed(raw_history):
            if r == target_role:
                valid_history.append((r, t))
                target_role = "assistant" if target_role == "user" else "user"
                
        valid_history.reverse()
        
        if len(valid_history) > 0 and valid_history[0][0] == "assistant":
            valid_history = valid_history[1:]

        contents = []
        for r, t in valid_history:
            role = "model" if r == "assistant" else "user"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=t)]))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config={
                "system_instruction": winter_persona,
                "response_mime_type": "application/json"
            }
        )
        
        raw_json_text = response.text
        
        with st.chat_message("assistant", avatar="❄️"):
            try:
                # 방금 받아온 따끈따끈한 JSON 코드도 예쁘게 파싱해서 화면에 출력!
                parsed_data = json.loads(raw_json_text)
                st.markdown(f"*(표정: {parsed_data.get('표정', '')} / 행동: {parsed_data.get('행동', '')})*\n\n**「 {parsed_data.get('대사', '')} 」**")
            except:
                st.markdown(raw_json_text)
                
        # 🚨 [중요] 하지만 제미나이 기억장치(DB)에는 원본 JSON 코드를 그대로 박아넣음!
        st.session_state.chat_history.append(("assistant", raw_json_text))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": raw_json_text}).execute()
