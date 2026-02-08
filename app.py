import streamlit as st
from openai import OpenAI
import json
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="NoRegret Trip", page_icon="✈️", layout="wide")

st.title("✈️ NoRegret Trip")
st.subheader("실패 없는 여행을 위한 AI 가이드 (업그레이드 버전)")

# 1. 사이드바: API 키 입력 및 사용법
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    st.markdown("---")
    st.write("💡 **사용 방법**")
    st.write("1. API Key를 입력하세요.")
    st.write("2. 여행 스타일을 선택하세요.")
    st.write("3. 지도로 위치를 확인하고 바로 예매하세요!")

# 2. 메인 화면: 사용자 입력 받기
st.markdown("### 📋 어떤 여행을 떠나고 싶으신가요?")

col1, col2 = st.columns(2)
with col1:
    # 기간 선택
    duration = st.selectbox("여행 기간", ["1박 2일", "2박 3일", "3박 4일", "4박 5일", "일주일", "일주일 이상"])
    companion = st.selectbox("동행 여부", ["혼자", "친구/연인", "가족(아이 동반)", "가족(부모님 동반)", "반려동물"])
    
    # 난이도 단순화 (쉬움 vs 모험가)
    difficulty = st.selectbox("여행 난이도", [
        "쉬움 (초보자: 직항 있고, 치안 좋고, 한국인 많은 곳)",
        "모험가 (탐험가: 경유 감수, 이색적이고 낯선 곳)"
    ])

with col2:
    style = st.selectbox("여행 스타일", ["힐링/휴양 (아무것도 안 하기)", "액티비티/관광 (꽉 찬 일정)", "먹방/미식 (하루 5끼)", "쇼핑/도시 (트렌디)"])
    budget_level = st.selectbox("예산 수준", ["가성비 (최소한의 비용)", "적당함 (평균)", "럭셔리 (비용 상관없음)"])

etc_req = st.text_input("특별히 원하는 조건이 있나요? (예: 더운 나라는 싫어요, 수영장 필수)")

# 3. AI 추천 버튼
if st.button("🚀 맞춤 여행지 3곳 추천받기"):
    if not api_key:
        st.error("⚠️ 사이드바에 OpenAI API Key를 먼저 입력해주세요!")
    else:
        with st.spinner("AI가 현실적인 일정과 외교부 안전 정보를 검토 중입니다..."):
            try:
                client = OpenAI(api_key=api_key)
                
                # 프롬프트 강화: 안전, 거리, 상세 설명, 공항 코드 요청
                prompt = f"""
                당신은 한국인 여행자를 위한 10년 차 베테랑 여행 가이드입니다.
                아래 조건에 맞춰서 **실제로 갈 수 있는** 여행지 3곳을 추천해주세요.

                [필수 제약 조건]
                1. **대한민국 외교부 지정 여행 금지 국가(예: 우크라이나, 소말리아 등)나 위험 국가는 절대 추천하지 마세요.**
                2. **현실적인 거리 고려:** 여행 기간이 {duration}으로 짧다면, 이동 시간이 너무 긴 곳(유럽, 미주, 남극 등)은 추천하지 마세요. 한국(인천)에서 현실적으로 다녀올 수 있는 거리여야 합니다.
                3. **설명 강화:** 예산과 일정 설명은 대충 하지 말고, 구체적인 금액과 동선, 팁을 포함해서 풍부하게(3~4문장 이상) 작성하세요.
                
                [사용자 정보]
                - 난이도: {difficulty}
                - 기간: {duration}
                - 동행: {companion}
                - 스타일: {style}
                - 예산: {budget_level}
                - 추가 요청: {etc_req}

                반드시 아래 JSON 형식으로만 답변하세요. (주석이나 추가 말 금지)
                {{
                    "destinations": [
                        {{
                            "name_kr": "도시명 (국가명)",
                            "airport_code": "IATA 공항 코드 3자리 (예: NRT, DAD, CDG)",
                            "latitude": 위도(숫자),
                            "longitude": 경도(숫자),
                            "reason": "왜 이곳이 딱인지 설득력 있는 추천 이유",
                            "itinerary": "1일차: ... / 2일차: ... (구체적인 동선과 명소 포함한 줄글 설명)",
                            "total_budget": "총 예상 비용 (1인 기준, 원화)",
                            "budget_detail": "항공권 약 00만, 숙박(3박) 약 00만, 식비/교통 약 00만 등 상세 내역 설명"
                        }},
                        ... (3개)
                    ]
                }}
                """

                # JSON 모드로 응답 받기
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" }
                )
                
                result = json.loads(response.choices[0].message.content)
                destinations = result['destinations']

                st.success(f"여행 기간({duration})에 맞춰 다녀올 수 있는 곳으로 엄선했습니다! 🎒")
                
                # 탭으로 보기 좋게 구분 (선택 사항)
                tab1, tab2, tab3 = st.tabs([d['name_kr'] for d in destinations])
                
                for i, tab in enumerate([tab1, tab2, tab3]):
                    with tab:
                        dest = destinations[i]
                        
                        # 1. 지도 표시
                        st.subheader(f"📍 {dest['name_kr']}")
                        map_data = pd.DataFrame({'lat': [dest['latitude']], 'lon': [dest['longitude']]})
                        st.map(map_data, zoom=4)
                        
                        # 2. 상세 설명 (이전 버전처럼 풍부하게)
                        st.markdown(f"#### 💡 왜 추천하나요?")
                        st.write(dest['reason'])
                        
                        st.divider()
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("#### 🗓️ 추천 일정")
                            st.info(dest['itinerary'])
                        
                        with col_b:
                            st.markdown("#### 💰 예상 예산")
                            st.success(f"**총 {dest['total_budget']}**")
                            st.caption(dest['budget_detail'])
                        
                        # 3. 스카이스캐너 버튼 (공항 코드로 정확도 UP)
                        # 출발지는 서울(ICN/GMP 통합코드: SEL)로 고정
                        skyscanner_url = f"https://www.skyscanner.co.kr/transport/flights/sela/{dest['airport_code']}"
                        st.link_button(f"✈️ {dest['name_kr']} 최저가 항공권 검색", skyscanner_url)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
