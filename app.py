import streamlit as st
from openai import OpenAI
import json
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="NoRegret Trip", page_icon="✈️", layout="wide")

st.title("✈️ NoRegret Trip")
st.subheader("기간과 취향에 딱 맞는 여행지 추천기")

# 1. 사이드바
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    st.markdown("---")
    st.write("💡 **사용 방법**")
    st.write("1. API Key를 입력하세요.")
    st.write("2. 여행 기간과 스타일을 선택하세요.")
    st.write("3. 기간에 따라 추천 여행지가 달라집니다!")

# 2. 메인 화면 입력
st.markdown("### 📋 여행 조건을 알려주세요")

col1, col2 = st.columns(2)
with col1:
    # 기간을 더 명확하게 구분
    duration = st.selectbox("여행 기간", [
        "1박 2일 (아주 짧음)", 
        "2박 3일 (짧음)", 
        "3박 4일 (보통)", 
        "4박 5일 (여유)", 
        "일주일 (장기)", 
        "일주일 이상 (아주 김)"
    ])
    companion = st.selectbox("동행 여부", ["혼자", "친구/연인", "가족(아이 동반)", "가족(부모님 동반)", "반려동물"])
    
    # 난이도
    difficulty = st.selectbox("여행 난이도", [
        "쉬움 (직항, 치안 좋음, 관광지 위주)",
        "모험가 (경유 가능, 로컬 체험, 남들이 안 가는 곳)"
    ])

with col2:
    style = st.selectbox("여행 스타일", ["휴양/힐링 (바다, 리조트)", "관광/유적지 (많이 걷기)", "식도락 (맛집 투어)", "쇼핑/도시 (핫플레이스)"])
    budget_level = st.selectbox("예산 수준", ["가성비 (저렴하게)", "적당함 (평균)", "럭셔리 (플렉스)"])

etc_req = st.text_input("특별 요청 (예: 더운 곳 싫음, 수영장 필수)")

# 3. 추천 버튼
if st.button("🚀 여행지 3곳 추천받기"):
    if not api_key:
        st.error("⚠️ 사이드바에 OpenAI API Key를 먼저 입력해주세요!")
    else:
        with st.spinner("AI가 기간에 맞는 최적의 거리를 계산 중입니다..."):
            try:
                client = OpenAI(api_key=api_key)
                
                # 프롬프트: 기간에 따른 지역 제한을 강력하게 검
                prompt = f"""
                당신은 여행 전문가입니다. 사용자 조건에 맞춰 여행지 3곳을 추천하세요.
                
                [매우 중요: 기간에 따른 추천 지역 제한]
                사용자의 여행 기간은 '{duration}'입니다. 이 기간을 엄격히 고려하여 추천하세요.
                1. '1박 2일' ~ '2박 3일': **무조건 한국 국내 혹은 비행시간 2시간 이내(후쿠오카, 대마도, 칭다오 등)**만 추천하세요. 먼 곳은 절대 금지.
                2. '3박 4일' ~ '4박 5일': 일본 전역, 대만, 홍콩, 마카오, 중국 상해/베이징 등 **비행시간 4시간 이내** 지역을 추천하세요.
                3. '일주일' ~ '일주일 이상': 동남아(방콕, 다낭, 발리, 싱가포르) 혹은 괌/사이판, 몽골 등을 추천하세요. **가까운 일본은 추천하지 마세요.**
                4. 난이도가 '모험가'라면 뻔한 관광지(오사카, 다낭)는 제외하고 숨은 명소를 추천하세요.

                [사용자 정보]
                - 난이도: {difficulty}
                - 동행: {companion}
                - 스타일: {style}
                - 예산: {budget_level}
                - 추가: {etc_req}

                반드시 아래 JSON 포맷으로 답변하세요.
                {{
                    "destinations": [
                        {{
                            "name_kr": "도시명 (국가명)",
                            "airport_code": "IATA공항코드(3자리)",
                            "latitude": 위도(숫자),
                            "longitude": 경도(숫자),
                            "reason": "기간과 거리를 고려한 추천 이유",
                            "itinerary": "간략한 일정 요약",
                            "total_budget": "총 예상 비용",
                            "budget_detail": "상세 예산 내용"
                        }}
                    ]
                }}
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" },
                    temperature=1.2, # 창의성 수치를 높여서 매번 다른 답이 나오게 유도
                )
                
                result = json.loads(response.choices[0].message.content)
                destinations = result['destinations']

                st.success(f"선택하신 기간({duration})에 딱 맞는 여행지를 찾아왔어요! 🎒")
                
                # 탭 생성
                tabs = st.tabs([d['name_kr'] for d in destinations])
                
                for i, tab in enumerate(tabs):
                    with tab:
                        dest = destinations[i]
                        st.subheader(f"📍 {dest['name_kr']}")
                        
                        # 지도
                        map_data = pd.DataFrame({'lat': [dest['latitude']], 'lon': [dest['longitude']]})
                        st.map(map_data, zoom=4)
                        
                        # 내용
                        st.info(f"💡 **추천 이유**: {dest['reason']}")
                        st.write(f"**🗓️ 일정**: {dest['itinerary']}")
                        st.write(f"**💰 비용**: {dest['total_budget']} ({dest['budget_detail']})")
                        
                        # 스카이스캐너 버튼
                        url = f"https://www.skyscanner.co.kr/transport/flights/sela/{dest['airport_code']}"
                        st.link_button(f"✈️ {dest['name_kr']} 항공권 보기", url)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
