import streamlit as st
from openai import OpenAI
import json
import pandas as pd
import requests
from datetime import datetime
from duckduckgo_search import DDGS


# 1. 페이지 설정 (유지)
st.set_page_config(page_title="NoRegret Trip", page_icon="✈️", layout="wide")

st.title("✈️ NoRegret Trip")
st.subheader("여행 가자 ^~^")


def get_landmark_image(query: str):
    """DuckDuckGo 이미지 검색으로 여행지 대표 이미지를 가져옵니다."""
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.images(
                    keywords=f"{query} landmark",
                    region="kr-kr",
                    safesearch="moderate",
                    size="Large",
                    max_results=1,
                )
            )

        if not results:
            return None, "대표 이미지를 찾지 못했어요."

        return results[0].get("image"), None
    except Exception as exc:
        return None, f"대표 이미지 조회 실패: {exc}"


def get_weather_summary(latitude: float, longitude: float):
    """Open-Meteo로 향후 7일 날씨 요약을 반환합니다."""
    endpoint = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 7,
    }

    weather_code_map = {
        0: "맑음",
        1: "대체로 맑음",
        2: "부분적으로 흐림",
        3: "흐림",
        45: "안개",
        48: "서리 안개",
        51: "약한 이슬비",
        61: "약한 비",
        63: "비",
        65: "강한 비",
        71: "약한 눈",
        73: "눈",
        80: "소나기",
        95: "뇌우",
    }

    try:
        response = requests.get(endpoint, params=params, timeout=12)
        response.raise_for_status()
        data = response.json().get("daily", {})
        if not data:
            return "날씨 데이터를 불러오지 못했어요."

        today_idx = 0
        max_temp = data["temperature_2m_max"][today_idx]
        min_temp = data["temperature_2m_min"][today_idx]
        rain_prob = data["precipitation_probability_max"][today_idx]
        weather_code = data["weathercode"][today_idx]

        weather_text = weather_code_map.get(weather_code, "변동성 있는 날씨")
        rainy_days = sum(1 for p in data["precipitation_probability_max"] if p and p >= 60)

        return (
            f"오늘 기준 {weather_text}, {min_temp:.0f}~{max_temp:.0f}°C 예상. "
            f"향후 7일 중 비 가능성 높은 날은 {rainy_days}일입니다."
        )
    except requests.RequestException as exc:
        return f"날씨 정보를 가져오지 못했어요: {exc}"


def get_festival_summary(query: str):
    """DuckDuckGo 텍스트 검색으로 축제/이벤트 정보 요약을 반환합니다."""
    current_year = datetime.now().year

    try:
        with DDGS() as ddgs:
            items = list(
                ddgs.text(
                    keywords=f"{query} festival event {current_year}",
                    region="kr-kr",
                    safesearch="moderate",
                    max_results=3,
                )
            )

        if not items:
            return "검색 결과 기준, 근시일 내 확인 가능한 대표 축제 정보를 찾지 못했어요."

        summaries = []
        for item in items[:2]:
            title = item.get("title", "이벤트")
            snippet = item.get("body", "일정 정보는 링크에서 확인해 주세요.")
            summaries.append(f"- **{title}**: {snippet}")

        return "\n".join(summaries)
    except Exception as exc:
        return f"축제 정보를 가져오지 못했어요: {exc}"


# 2. 사이드바 (유지)
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    st.markdown("---")
    st.markdown("### 🌐 외부 정보 연동")
    st.caption("대표 이미지 + 축제 정보를 DuckDuckGo Search 기반으로 가져옵니다.")

    st.markdown("---")
    st.write("💡 **팁**")
    st.write("- **'일주일 이상'**을 선택해야 유럽/미주 등 장거리 추천이 나옵니다.")
    st.write("- **'모험가'**를 선택하면 더 이색적인 곳이 나옵니다.")

# 3. 메인 화면 입력 (유지)
st.markdown("### 📋 여행 스타일을 골라주세요")

col1, col2 = st.columns(2)
with col1:
    # 기간 선택
    duration = st.selectbox("여행 기간", [
        "1박 2일", "2박 3일", "3박 4일",
        "4박 5일", "일주일 (6박 7일)", "일주일 이상 (장기/유럽/미주 가능)"
    ])
    companion = st.selectbox("동행 여부", ["혼자", "친구/연인", "가족", "반려동물"])

    # 난이도
    difficulty = st.selectbox("여행 난이도", [
        "쉬움 (힐링: 직항, 한국인 많음, 편한 인프라)",
        "모험가 (탐험: 남들 안 가는 곳, 로컬 감성, 경유 OK)"
    ])

with col2:
    style = st.selectbox("여행 스타일", ["휴양/바다 (물놀이)", "관광/유적 (많이 걷기)", "미식/로컬푸드", "쇼핑/도시", "대자연/트레킹"])
    budget_level = st.selectbox("예산 수준", ["가성비 (아끼기)", "적당함 (평균)", "럭셔리 (플렉스)"])

etc_req = st.text_input("특별 요청 (예: 사막이 보고 싶어요, 미술관 투어 원함)")

# 4. 추천 버튼
if st.button("🚀 여행지 3곳 추천받기"):
    if not api_key:
        st.error("⚠️ 사이드바에 OpenAI API Key를 먼저 입력해주세요!")
    else:
        with st.spinner("AI가 전 세계 지도를 펼쳐 놓고 고민 중입니다..."):
            try:
                client = OpenAI(api_key=api_key)

                # 프롬프트 수정: 장거리 여행 시 대륙 제한 해제
                prompt = f"""
                당신은 전 세계를 여행한 베테랑 가이드입니다. 사용자 조건에 맞는 여행지 3곳을 추천하세요.

                [사용자 정보]
                - 난이도: {difficulty}
                - 기간: {duration}
                - 스타일: {style}
                - 예산: {budget_level}
                - 동행: {companion}
                - 추가요청: {etc_req if etc_req else '없음'}

                [🚨 거리 및 지역 추천 로직 (수정됨)]
                1. **단거리 ('1박 2일' ~ '4박 5일'):**
                   - 물리적으로 먼 곳은 불가능합니다. **한국 국내, 일본, 중국, 대만, 홍콩, 마카오, 블라디보스톡** 등 비행시간 5시간 이내 지역만 추천하세요.

                2. **장거리 ('일주일' ~ '일주일 이상'):**
                   - **아시아에 국한되지 마세요! 전 세계로 눈을 돌리세요.**
                   - 예산이 '적당함' 이상이고 기간이 길다면 **유럽(서유럽/동유럽), 미주(미국/캐나다), 대양주(호주/뉴질랜드), 중동(튀르키예/두바이)** 등을 적극 추천하세요.
                   - 물론 사용자가 휴양을 원하면 동남아도 가능하지만, **'유럽이나 다른 대륙'을 우선적으로 고려**해보세요.

                3. **난이도별 차별화:**
                   - **'쉬움'**: 파리, 런던, 로마, 시드니, 뉴욕, 싱가포르 등 유명하고 인프라 좋은 곳.
                   - **'모험가'**:
                     - 아시아: 몽골, 라오스, 치앙마이, 사파 등.
                     - 유럽/기타: 포르투갈, 크로아티아, 아이슬란드, 튀르키예 카파도키아, 이집트 등 이색적인 곳.
                     - **(금지어 적용 유지)**: 다낭, 방콕, 오사카, 세부 등 너무 뻔한 곳은 '모험가'에게 추천 금지.

                4. **공통 제약:**
                   - 대한민국 외교부 여행 금지 국가 절대 제외.

                반드시 아래 JSON 포맷으로 답변하세요.
                {{
                    "destinations": [
                        {{
                            "name_kr": "도시명 (국가명)",
                            "airport_code": "IATA공항코드(3자리)",
                            "latitude": 위도(숫자),
                            "longitude": 경도(숫자),
                            "reason": "기간과 대륙을 고려한 추천 이유",
                            "itinerary": "상세 일정 요약",
                            "total_budget": "총 예상 비용 (1인, 항공포함)",
                            "budget_detail": "상세 내역"
                        }}
                    ]
                }}
                """

                # temperature 1.1 유지 (다양성)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=1.1,
                )

                result = json.loads(response.choices[0].message.content)
                destinations = result['destinations']

                st.success(f"'{duration}' 동안 다녀오기 좋은, 전 세계 여행지를 엄선했습니다! 🌍")

                tabs = st.tabs([d['name_kr'] for d in destinations])

                for i, tab in enumerate(tabs):
                    with tab:
                        dest = destinations[i]
                        st.header(f"📍 {dest['name_kr']}")

                        map_data = pd.DataFrame({'lat': [dest['latitude']], 'lon': [dest['longitude']]})
                        st.map(map_data, zoom=4)

                        image_url, image_error = get_landmark_image(dest['name_kr'])
                        if image_url:
                            st.image(image_url, caption=f"{dest['name_kr']} 대표 랜드마크", use_container_width=True)
                        else:
                            st.warning(image_error)

                        st.info(f"💡 **추천 이유**: {dest['reason']}")

                        weather_summary = get_weather_summary(dest['latitude'], dest['longitude'])
                        festival_summary = get_festival_summary(dest['name_kr'])

                        st.markdown("#### 🌤️ 현지 날씨 (실시간 예보)")
                        st.write(weather_summary)

                        st.markdown("#### 🎉 현지 축제/이벤트 (검색 기반)")
                        st.markdown(festival_summary)

                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("#### 🗓️ 추천 일정")
                            st.write(dest['itinerary'])

                        with col_b:
                            st.markdown("#### 💰 예상 예산")
                            st.success(f"**{dest['total_budget']}**")
                            st.caption(dest['budget_detail'])

                        st.markdown("---")
                        url = f"https://www.skyscanner.co.kr/transport/flights/sela/{dest['airport_code']}"
                        st.link_button(f"✈️ {dest['name_kr']} 항공권 검색", url)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
