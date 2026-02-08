import streamlit as st
from openai import OpenAI
import json
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="NoRegret Trip", page_icon="✈️")

st.title("✈️ NoRegret Trip")
st.subheader("실패 없는 여행을 위한 AI 가이드")

# 1. 사이드바: API 키 입력 및 사용법
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    st.markdown("---")
    st.write("💡 **사용 방법**")
    st.write("1. API Key를 입력하세요.")
    st.write("2. 난이도와 여행 조건을 선택하세요.")
    st.write("3. 지도로 위치를 확인하고 바로 예매하세요!")

# 2. 메인 화면: 사용자 입력 받기
st.markdown("### 📋 여행 조건을 알려주세요")

col1, col2 = st.columns(2)
with col1:
    duration = st.selectbox("여행 기간", ["2박 3일", "3박 4일", "4박 5일", "일주일", "일주일 이상"])
    companion = st.selectbox("동행 여부", ["혼자", "친구/연인", "가족", "반려동물"])
    # 여행 난이도 추가 (요청사항 반영)
    difficulty = st.selectbox("여행 난이도", [
        "하 (초보자: 일본, 대만 등 가깝고 편한 곳)",
        "중 (경험자: 적당한 비행시간과 관광)",
        "상 (모험가: 남들이 잘 안 가는 이색 여행지)"
    ])

with col2:
    style = st.selectbox("여행 스타일", ["힐링/휴양", "액티비티/관광", "먹방/미식", "쇼핑/예술"])
    budget_level = st.selectbox("예산 수준", ["최소 비용 (가성비)", "적당함 (일반)", "여유로움 (럭셔리)"])

etc_req = st.text_input("추가 요청사항 (예: 추운 건 싫어요, 직항만 원해요)")

# 3. AI 추천 버튼
if st.button("🚀 여행지 3곳 추천받기"):
    if not api_key:
        st.error("⚠️ 사이드바에 OpenAI API Key를 먼저 입력해주세요!")
    else:
        with st.spinner("AI가 최적의 여행지 3곳을 분석하고 지도를 준비 중입니다..."):
            try:
                client = OpenAI(api_key=api_key)
                
                # AI에게 JSON 형식으로 데이터를 요청 (좌표와 영어 이름 포함)
                prompt = f"""
                당신은 전문 여행 가이드입니다. 아래 조건에 맞는 여행지 3곳을 추천해주세요.
                
                [사용자 조건]
                - 난이도: {difficulty} (난이도 '하'는 일본/대만/동남아 등 한국에서 가깝고 편한 곳 위주, '상'은 남미/아프리카/소도시 등 이색적인 곳 위주)
                - 기간: {duration}
                - 동행: {companion}
                - 스타일: {style}
                - 예산: {budget_level}
                - 추가: {etc_req}

                반드시 아래 JSON 형식(List)으로만 답변해주세요. 설명이나 사족을 달지 마세요.
                {{
                    "destinations": [
                        {{
                            "name_kr": "여행지 한글 이름 (국가)",
                            "name_en": "여행지 영어 이름 (스카이스캐너 검색용, 도시명)",
                            "latitude": 위도(실수형),
                            "longitude": 경도(실수형),
                            "reason": "추천 이유 요약",
                            "itinerary": "간단 추천 일정",
                            "total_budget": "총 예상 비용 (항공,숙박,식비 포함)",
                            "budget_detail": "예산 상세 설명"
                        }},
                        ... (총 3개)
                    ]
                }}
                """

                # JSON 모드로 응답 받기
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # gpt-3.5-turbo-1106 이상 사용 권장
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" }
                )
                
                # 데이터 변환 (String -> JSON)
                result = json.loads(response.choices[0].message.content)
                destinations = result['destinations']

                st.success("여행지 분석 완료! 아래에서 지도를 확인하세요. 🗺️")
                
                # 3개 여행지 반복 출력
                for i, dest in enumerate(destinations):
                    st.markdown("---")
                    st.markdown(f"### {i+1}. {dest['name_kr']}")
                    
                    # 1) 구글 맵 대신 Streamlit 내장 지도 활용 (위도/경도 사용)
                    # 좌표 데이터 프레임 생성
                    map_data = pd.DataFrame({
                        'lat': [dest['latitude']],
                        'lon': [dest['longitude']]
                    })
                    st.map(map_data, zoom=4) # 지도 표시
                    
                    # 2) 상세 정보 출력
                    st.info(f"💡 **추천 이유**: {dest['reason']}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**🗓️ 일정**: {dest['itinerary']}")
                    with col_b:
                        st.write(f"**💰 총 비용**: {dest['total_budget']}")
                        st.caption(f"({dest['budget_detail']})")
                    
                    # 3) 스카이스캐너 바로가기 버튼 (영어 이름 활용)
                    # 서울(ICN/GMP) 출발 기준으로 검색 링크 생성
                    skyscanner_url = f"https://www.skyscanner.co.kr/transport/flights/sela/{dest['name_en']}"
                    st.link_button(f"✈️ {dest['name_kr']} 항공권 최저가 검색", skyscanner_url)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
