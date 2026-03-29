import streamlit as st
import json  # 🚨 못생긴 컴퓨터 언어(JSON)를 번역해 줄 해독기 부품!
from google import genai
from google.genai import types 
from supabase import create_client, Client

# 1. 페이지 설정 및 깔끔한 출고용 마감
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# 지붕 숨기기를 빼서 점 세 개(다크모드 메뉴)를 부활시키고, 짜치는 Deploy 버튼만 암살!
st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 🚨 [새로 추가된 핵심 부품! - 3번 구역] 이미지 지도(Mapping) 세팅
# 파아야! 네가 깃허브 'images' 폴더에 올린 실제 파일 이름으로 여기를 꼭 수정해줘!
# (대소문자, 확장자 .png까지 완벽하게 똑같아야 해!)
emotion_images = {
    "화남": "images/angry.png",          # 예: 네가 올린 게 Angry.png면 여기도 Angry.png로!
    "웃음": "images/smile.png",
    "정색": "images/serious.png",
    "당황": "images/flustered.png",
    "삐짐": "images/sulking.png",
    "부끄러움": "images/shy.png",
    "무표정": "images/neutral.png",
    "기본": "images/neutral.png"           # 에러 방지용 기본 이미지
}

# 2. 스트림릿 금고에서 열쇠 꺼내오기
api_key = st.secrets["GOOGLE_API_KEY"]
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

# 3. DB 접속 도구
supabase: Client = create_client(supabase_url, supabase_key)
client = genai.Client(api_key=api_key)

# 4. 문지기 로직
if "user_name" not in st.session_state:
    st.title("❄️ 한겨울 라이브 챗 접속")
    st.write("한겨울이 당신을 뭐라고 불러드릴까요?")
    
    with st.form(key='login_form'):
        name_input = st.text_input("당신의 닉네임을 입력해주세요.", placeholder="예: 파이, 스트리머 이름 등")
        submit_button = st.form_submit_button(label='대화 시작하기 ➡️')
        
    if submit_button and name_input:
        st.session_state.user_name = name_input
        st.rerun()

# 5. 진짜 채팅방 입장 (3D 게임 엔진 NPC 두뇌 모드)
else:
    user_name = st.session_state.user_name
    
    # [프롬프트 대수술] 호감도 변화 수치를 계산해서 같이 뱉어내도록 지시!
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
        "호감도변화": "유저의 방금 대화에 대한 호감도 변화 수치 (-5부터 +5 사이의 정수만 입력)",
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

    # [10시 패치 공지!] 업데이트 완료 배너 띄우기!
    st.info("📢 **[시스템 공지]** 3D VR 엔진 및 [호감도 시스템], [비주얼 업그레이드]가 완료되었습니다! 이제 겨울이가 대화에 따라 표정을 바꿉니다.", icon="✨")

    # 6. 기억력 복원
    if "chat_history" not in st.session_state:
        response = supabase.table("chat_memory").select("*").eq("user_name", user_name).order("id").execute()
        db_history = response.data

        st.session_state.chat_history = []
        for row in db_history:
            st.session_state.chat_history.append((row["role"], row["message"]))

        if not db_history:
            # 첫 인사에도 호감도(0)와 표정(정색)을 세팅해줌!
            first_msg = f'{{"표정": "정색", "행동": "팔짱을 꼬며 쳐다본다", "호감도변화": 0, "대사": "뭐야, {user_name}. 왜 이렇게 늦었어?"}}'
            st.session_state.chat_history.append(("assistant", first_msg))
            supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": first_msg}).execute()

    # 🚨 [가장 화려한 마술! - 비주얼 노벨 모드] DB의 못생긴 JSON 코드를 화면에만 예쁘게 번역 및 이미지 출력
    for role, text in st.session_state.chat_history:
        # 유저 채팅창은 그대로 냅둠
        if role == "user":
            with st.chat_message("user"):
                st.markdown(text)
        # 겨울이 채팅창은 프로필 사진 로직 가동!
        else:
            try:
                # 1. JSON 해독기로 데이터 부품별로 분해
                data = json.loads(text)
                emotion = data.get('표정', '기본')  # 표정 데이터 추출
                
                # 2. 이미지 지도에서 표정에 맞는 사진 주소 가져오기
                img_path = emotion_images.get(emotion, emotion_images["기본"])
                
                # 3. 🚨 [핵심 업데이트] 채팅창 옆에 눈송이 이모티콘 대신, 진짜 겨울이 일러스트 띄우기!
                with st.chat_message("assistant", avatar=img_path):
                    score = int(data.get('호감도변화', 0))
                    # 수치에 따라 하트 모양 다르게 출력!
                    heart_icon = "💔" if score < 0 else "💖" if score > 0 else "🤍"
                    st.markdown(f"*(표정: {emotion} / 행동: {data.get('행동', '')})*\n\n**[호감도 변화: {score} {heart_icon}]**\n\n**「 {data.get('대사', '')} 」**")
            except:
                # 혹시 옛날 데이터나 에러가 나면 그냥 원본 출력
                with st.chat_message("assistant", avatar="❄️"):
                    st.markdown(text)

    # 8. 실시간 채팅 및 API 통신 (JSON 규격 강제 적용)
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
        
        # 실시간 응답 화면 출력 로직 (위의 루프와 똑같아!)
        try:
            parsed_data = json.loads(raw_json_text)
            emotion = parsed_data.get('표정', '기본')
            img_path = emotion_images.get(emotion, emotion_images["기본"])
            
            with st.chat_message("assistant", avatar=img_path):
                score = int(parsed_data.get('호감도변화', 0))
                heart_icon = "💔" if score < 0 else "💖" if score > 0 else "🤍"
                st.markdown(f"*(표정: {emotion} / 행동: {parsed_data.get('행동', '')})*\n\n**[호감도 변화: {score} {heart_icon}]**\n\n**「 {parsed_data.get('대사', '')} 」**")
        except:
            with st.chat_message("assistant", avatar="❄️"):
                st.markdown(raw_json_text)
                
        # 🚨 [중요] DB에는 여전히 원본 JSON을 저장함!
        st.session_state.chat_history.append(("assistant", raw_json_text))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": raw_json_text}).execute()
