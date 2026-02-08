import streamlit as st
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(page_title="NoRegret Trip", page_icon="✈️")

st.title("✈️ NoRegret Trip")
st.subheader("당신의 선택 장애를 해결해 줄 AI 여행 가이드")

# 1. 사이드바: API 키 입력 및 사용법
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    st.markdown("---")
    st.write("💡 **사용 방법**")
    st.write("1. API Key를 입력합니다.")
    st.write("2. 여행 스타일과 조건을 선택합니다.")
    st.write("3. '여행지 추천받기' 버튼을 누르세요.")

# 2. 메인 화면: 사용자 입력 받기 (기획서 기능 1 반영)
# 여행 목적, 기간, 동행 여부, 선호 활동 등을 입력받습니다.
st.markdown("### 📋 여행 조건을 알려주세요")

col1, col2 = st.columns(2)
with col1:
    duration = st.selectbox("여행 기간", ["당일치기", "1박 2일", "2박 3일", "3박 4일", "일주일 이상"])
    companion = st.selectbox("동행 여부", ["혼자 떠나는 여행", "친구/연인과 함께", "가족과 함께", "반려동물과 함께"])

with col2:
    style = st.selectbox("여행 스타일", ["힐링/휴양 (편안함)", "액티비티/관광 (활동적)", "먹방/미식 (맛집탐방)", "쇼핑/문화생활"])
    budget_level = st.selectbox("예산 수준", ["최소 비용 (가성비)", "적당함 (일반)", "여유로움 (럭셔리)"])

# 추가 요청사항 입력
etc_req = st.text_input("추가로 고려할 사항이 있나요? (예: 국내 여행만, 바다가 보이는 곳 등)")

# 3. AI 추천 버튼
if st.button("🚀 후회 없는 여행지 추천받기"):
    if not api_key:
        st.error("⚠️ 사이드바에 OpenAI API Key를 먼저 입력해주세요!")
    else:
        with st.spinner("AI가 당신을 위한 최고의 여행지를 분석 중입니다..."):
            try:
                # OpenAI 클라이언트 생성
                client = OpenAI(api_key=api_key)
                
                # AI에게 보낼 질문 만들기 (기획서 기능 2, AI 활용 계획 반영)
                prompt = f"""
                당신은 결정 장애가 있는 여행자를 위한 전문 가이드 'NoRegret Trip'입니다.
                아래 사용자의 조건에 맞춰서 가장 후회 없을 만한 여행지 1곳을 추천하고, 구체적인 계획을 제안해주세요.
                
                [사용자 조건]
                - 여행 기간: {duration}
                - 동행: {companion}
                - 스타일: {style}
                - 예산 수준: {budget_level}
                - 추가 요청: {etc_req}

                [답변 양식]
                1. 🏆 추천 여행지 이름 (국가/도시)
                2. 💡 추천 이유 (이 사용자가 만족할 포인트 설명)
                3. 🗓️ 간단 추천 일정 (주요 명소 포함)
                4. 💰 예상 예산 상세 (기획서의 '예산 상세 보기' 기능 반영)
                   - 교통비: (예상 금액 및 팁)
                   - 숙박비: ({budget_level} 수준에 맞는 숙소 추천 및 가격대)
                   - 식비/기타: (예상 금액)
                   - 총 예상 비용: (대략적인 합계)
                5. ✈️ 꿀팁 (항공권이나 이동편 예약 팁)

                말투는 친절하고 전문적인 가이드처럼 해주세요.
                """

                # AI에게 질문 전송
                response = client.chat.completions.create(
                    model="gpt-4o-mini", # 또는 gpt-3.5-turbo
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # 결과 출력
                st.success("여행지 추천이 도착했습니다!")
                st.markdown(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
