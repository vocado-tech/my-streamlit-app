import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import json
import pandas as pd
import requests
import re
from datetime import datetime
from duckduckgo_search import DDGS


ENTRY_REQUIREMENTS_BY_COUNTRY = {
    "일본": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일 체류 가능",
        "eta": "별도 ESTA/ETA 불필요",
        "passport": "입국 시 유효한 전자여권 필요 (통상 6개월 이상 권장)",
    },
    "중국": {
        "visa": "일반적으로 비자 필요 (경유/특정 정책 예외 가능)",
        "stay": "비자 종류에 따라 상이",
        "eta": "ESTA/ETA 불필요",
        "passport": "일반적으로 6개월 이상 유효기간 필요",
    },
    "대만": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국 시 6개월 이상 권장",
    },
    "홍콩": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국 시 1개월+ 체류기간을 초과하는 유효기간 권장",
    },
    "베트남": {
        "visa": "45일 이하 무비자",
        "stay": "최대 45일",
        "eta": "ESTA/ETA 불필요",
        "passport": "일반적으로 6개월 이상 유효기간 필요",
    },
    "태국": {
        "visa": "무비자 입국 가능",
        "stay": "정책에 따라 60일 내외 (변동 가능)",
        "eta": "ESTA/ETA 불필요",
        "passport": "일반적으로 6개월 이상 유효기간 필요",
    },
    "싱가포르": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "전자입국신고(SG Arrival Card) 필요",
        "passport": "입국 시 6개월 이상 유효기간 필요",
    },
    "말레이시아": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "전자입국신고(MDAC) 필요",
        "passport": "입국 시 6개월 이상 유효기간 필요",
    },
    "미국": {
        "visa": "관광 목적 90일 이하는 ESTA 승인 시 무비자",
        "stay": "최대 90일 (ESTA 기준)",
        "eta": "ESTA 필수",
        "passport": "전자여권 필요 (체류기간 동안 유효)",
    },
    "캐나다": {
        "visa": "단기 체류 시 비자 면제",
        "stay": "통상 최대 6개월",
        "eta": "eTA 필수 (항공 입국 시)",
        "passport": "입국 시 유효한 여권 필요",
    },
    "영국": {
        "visa": "단기 방문 무비자",
        "stay": "최대 6개월",
        "eta": "ETA 필요",
        "passport": "체류기간 동안 유효한 여권 필요",
    },
    "프랑스": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "독일": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "이탈리아": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "스페인": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "포르투갈": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "네덜란드": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "크로아티아": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "아이슬란드": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "튀르키예": {
        "visa": "90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국일 기준 150일 이상 권장",
    },
    "아랍에미리트": {
        "visa": "90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "일반적으로 6개월 이상 유효기간 필요",
    },
    "호주": {
        "visa": "비자 필요",
        "stay": "승인 비자 조건에 따름",
        "eta": "ETA 또는 eVisitor 사전 신청 필요",
        "passport": "체류기간 동안 유효한 전자여권 필요",
    },
    "뉴질랜드": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "NZeTA 필수",
        "passport": "출국일 기준 3개월 이상 유효기간 필요",
    },
    "몽골": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "일반적으로 6개월 이상 유효기간 필요",
    },
    "라오스": {
        "visa": "무비자 입국 가능",
        "stay": "통상 30일 내외 (변동 가능)",
        "eta": "전자비자(eVisa) 선택 가능",
        "passport": "일반적으로 6개월 이상 유효기간 필요",
    },
    "이집트": {
        "visa": "비자 필요",
        "stay": "비자 조건에 따름",
        "eta": "e-Visa 사전 신청 또는 도착비자 가능",
        "passport": "일반적으로 6개월 이상 유효기간 필요",
    },
}


# 1. 페이지 설정 (유지)
st.set_page_config(page_title="NoRegret Trip", page_icon="✈️", layout="wide")

st.title("✈️ NoRegret Trip")
st.subheader("여행 가자 ^~^")


def _extract_destination_keywords(query: str):
    """도시명(국가명) 형태 문자열에서 검색용 키워드를 추출합니다."""
    base = query.strip()
    if "(" in base:
        base = base.split("(")[0].strip()
    return [query, base]


def _get_wikipedia_image(query: str):
    """Wikipedia 요약 API를 이용해 대표 이미지를 보조 조회합니다."""
    for keyword in _extract_destination_keywords(query):
        try:
            endpoint = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{keyword}"
            res = requests.get(endpoint, timeout=8)
            if res.status_code != 200:
                continue
            data = res.json()
            thumb = data.get("thumbnail", {}).get("source")
            original = data.get("originalimage", {}).get("source")
            if original or thumb:
                return original or thumb
        except requests.RequestException:
            continue
    return None


def get_landmark_image(query: str):
    """DuckDuckGo + Wikipedia로 여행지 대표 이미지를 가져옵니다."""
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

        if results:
            image_url = (
                results[0].get("image")
                or results[0].get("thumbnail")
                or results[0].get("url")
            )
            if image_url:
                return image_url, None

        wiki_image = _get_wikipedia_image(query)
        if wiki_image:
            return wiki_image, None

        return None, "대표 이미지를 찾지 못했어요."
    except Exception:
        wiki_image = _get_wikipedia_image(query)
        if wiki_image:
            return wiki_image, None
        return None, "대표 이미지 서비스 접근이 제한되어 이미지를 불러오지 못했어요."


def get_best_travel_season(latitude: float):
    """위도 기반으로 여행하기 좋은 시기를 추천합니다."""
    abs_lat = abs(latitude)

    if abs_lat < 15:
        return "연중 여행 가능 (우기/건기 확인 권장)"

    if latitude >= 0:
        return "4~6월, 9~10월 (기온이 온화하고 이동이 편한 시기)"

    return "10~12월, 3~4월 (남반구 기준 쾌적한 계절)"


def get_weather_summary(latitude: float, longitude: float, weather_api_key: str):
    """OpenWeather API로 현재 날씨 + 단기 예보를 요약합니다."""
    if not weather_api_key:
        return "OpenWeather API Key를 입력하면 현재 날씨를 볼 수 있어요."

    current_endpoint = "https://api.openweathermap.org/data/2.5/weather"
    forecast_endpoint = "https://api.openweathermap.org/data/2.5/forecast"
    base_params = {
        "lat": latitude,
        "lon": longitude,
        "appid": weather_api_key,
        "units": "metric",
        "lang": "kr",
    }

    try:
        current_res = requests.get(current_endpoint, params=base_params, timeout=12)
        current_res.raise_for_status()
        current_data = current_res.json()

        forecast_res = requests.get(forecast_endpoint, params=base_params, timeout=12)
        forecast_res.raise_for_status()
        forecast_data = forecast_res.json().get("list", [])

        current_weather = current_data.get("weather", [{}])[0].get("description", "날씨 정보 없음")
        current_temp = current_data.get("main", {}).get("temp")
        feels_like = current_data.get("main", {}).get("feels_like")

        rainy_slots = 0
        for slot in forecast_data[:16]:  # 약 2일치(3시간 간격)
            rain_probability = slot.get("pop", 0)
            if rain_probability >= 0.6:
                rainy_slots += 1

        season_tip = get_best_travel_season(latitude)

        return (
            f"현재 날씨는 **{current_weather}**, 기온은 **{current_temp:.1f}°C** "
            f"(체감 **{feels_like:.1f}°C**) 입니다. "
            f"향후 48시간 기준 비 가능성이 높은 시간대는 약 {rainy_slots}회예요.\n\n"
            f"✈️ **여행 추천 시기**: {season_tip}"
        )
    except requests.HTTPError as exc:
        return f"OpenWeather 요청이 실패했어요. API Key를 확인해 주세요: {exc}"
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


def get_destination_bgm(name_kr: str):
    """도시 분위기에 맞는 유튜브 BGM 플레이리스트를 반환합니다."""
    bgm_map = {
        "파리": ("Emily in Paris OST 분위기 플레이리스트", "https://www.youtube.com/watch?v=cTLTG4FTNBQ"),
        "몽골": ("광활한 초원 드라이브 BGM", "https://www.youtube.com/watch?v=9e9v4M9RjvY"),
        "치앙마이": ("치앙마이 카페 감성 로파이", "https://www.youtube.com/watch?v=5qap5aO4i9A"),
        "다낭": ("다낭 해변 선셋 칠 음악", "https://www.youtube.com/watch?v=DWcJFNfaw9c"),
    }

    for keyword, bgm_info in bgm_map.items():
        if keyword in name_kr:
            return bgm_info

    return (
        "여행 설렘을 높여주는 월드 트래블 무드",
        "https://www.youtube.com/watch?v=2OEL4P1Rz04",
    )


def extract_country_from_destination(name_kr: str):
    """도시명 (국가명) 문자열에서 국가명만 추출합니다."""
    if "(" in name_kr and ")" in name_kr:
        return name_kr.split("(")[-1].replace(")", "").strip()
    return name_kr.strip()


def _summarize_entry_requirement_from_search(country: str):
    """검색 결과 스니펫을 바탕으로 비자/입국 요건을 요약합니다."""
    fallback = {
        "visa": "검색 결과 기준 최신 정책 확인 필요",
        "stay": "검색 결과에서 체류기간 확인 필요",
        "eta": "검색 결과에서 ETA/ESTA 여부 확인 필요",
        "passport": "대부분 국가에서 6개월 이상 유효기간 권장",
        "source": "",
    }

    try:
        with DDGS() as ddgs:
            items = list(
                ddgs.text(
                    keywords=f"{country} 대한민국 여권 비자 체류 기간 ETA ESTA 여권 유효기간",
                    region="kr-kr",
                    safesearch="moderate",
                    max_results=5,
                )
            )

        if not items:
            return fallback

        text_blob = " ".join(
            [item.get("title", "") + " " + item.get("body", "") for item in items]
        )

        visa = fallback["visa"]
        if "무비자" in text_blob:
            visa = "무비자 가능 (검색 결과 기반)"
        elif "비자 필요" in text_blob or "사증" in text_blob:
            visa = "비자 필요 가능성 높음 (검색 결과 기반)"

        stay = fallback["stay"]
        stay_match = re.search(r"(\d{1,3})\s*일", text_blob)
        if stay_match:
            stay = f"약 {stay_match.group(1)}일 내외 (검색 결과 기반)"

        eta = fallback["eta"]
        if "ESTA" in text_blob:
            eta = "ESTA 필요 가능성 있음 (검색 결과 기반)"
        elif "eTA" in text_blob or "ETA" in text_blob or "NZeTA" in text_blob:
            eta = "ETA/eTA 필요 가능성 있음 (검색 결과 기반)"
        elif "불필요" in text_blob and ("ETA" in text_blob or "ESTA" in text_blob):
            eta = "ETA/ESTA 불필요 가능성 있음 (검색 결과 기반)"

        passport = fallback["passport"]
        if "6개월" in text_blob:
            passport = "입국 시 여권 유효기간 6개월 이상 필요 가능성 높음"
        elif "3개월" in text_blob:
            passport = "출국 예정일 기준 3개월 이상 필요 가능성 있음"
        elif "150일" in text_blob:
            passport = "입국일 기준 150일 이상 필요 가능성 있음"

        first = items[0]
        source = first.get("href") or first.get("url") or ""

        return {
            "visa": visa,
            "stay": stay,
            "eta": eta,
            "passport": passport,
            "source": source,
        }
    except Exception:
        return fallback


def get_entry_requirement_for_korean_passport(destination_name: str):
    """대한민국 여권 기준 비자/입국 요건을 반환합니다."""
    country = extract_country_from_destination(destination_name)
    requirement = ENTRY_REQUIREMENTS_BY_COUNTRY.get(country)

    if requirement:
        return country, requirement, False

    searched_requirement = _summarize_entry_requirement_from_search(country)
    return country, searched_requirement, True


def render_kakao_share_copy_button(share_text: str):
    """카카오톡 공유용 텍스트를 클립보드에 복사하는 버튼을 렌더링합니다."""
    safe_text = json.dumps(share_text)

    components.html(
        f"""
        <div style="margin-top:8px; margin-bottom:8px;">
            <button id="kakao-copy-btn"
                style="
                    background:#FEE500;
                    color:#191919;
                    border:none;
                    border-radius:10px;
                    padding:10px 14px;
                    font-weight:700;
                    cursor:pointer;
                ">
                📋 카카오톡 공유 텍스트 복사
            </button>
            <p id="kakao-copy-status" style="margin-top:8px; font-size:14px;"></p>
        </div>
        <script>
            const button = document.getElementById("kakao-copy-btn");
            const status = document.getElementById("kakao-copy-status");
            const textToCopy = {safe_text};

            button.addEventListener("click", async () => {{
                try {{
                    await navigator.clipboard.writeText(textToCopy);
                    status.textContent = "복사 완료! 친구 단톡방에 바로 붙여넣어 투표를 받아보세요 🙌";
                }} catch (error) {{
                    status.textContent = "브라우저 권한 문제로 자동 복사에 실패했어요. 아래 텍스트를 수동 복사해 주세요.";
                }}
            }});
        </script>
        """,
        height=120,
    )


# 2. 사이드바 (유지)
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    weather_api_key = st.text_input("OpenWeather API Key를 입력하세요", type="password")
    st.markdown("---")
    st.markdown("### 🌐 외부 정보 연동")
    st.caption("대표 이미지/축제는 DuckDuckGo, 날씨는 OpenWeather API를 사용합니다.")

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
                            "itinerary": [
                                "DAY 1: 오전/오후/저녁 동선을 포함한 상세 일정",
                                "DAY 2: 이동시간/예약팁/식사 추천 포함",
                                "..."
                            ],
                            "total_budget": "총 예상 비용 (1인, 왕복항공 포함, KRW)",
                            "budget_detail": [
                                "왕복 항공권: 000,000원 (성수기/비수기 범위)",
                                "숙소: 1박 000,000원 x N박 = 000,000원",
                                "식비: 1일 00,000원 x N일 = 000,000원",
                                "교통/입장료/투어/기타 비용"
                            ]
                        }}
                    ]
                }}

                [일정/예산 품질 규칙]
                - itinerary는 문자열 하나가 아니라 '일자별 리스트'로 반환하세요. 최소 3개 이상.
                - 각 일자 항목에는 오전/오후/저녁 활동과 이동 팁을 포함하세요.
                - total_budget과 budget_detail은 한국 원화 기준으로 작성하세요.
                - budget_detail은 실제 여행자가 참고 가능한 현실적인 숫자로 작성하세요.
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

                        weather_summary = get_weather_summary(dest['latitude'], dest['longitude'], weather_api_key)
                        festival_summary = get_festival_summary(dest['name_kr'])

                        st.markdown("#### 🌤️ 현지 날씨 (실시간 예보)")
                        st.write(weather_summary)

                        st.markdown("#### 🎉 현지 축제/이벤트 (검색 기반)")
                        st.markdown(festival_summary)

                        country, entry_info, is_search_based = get_entry_requirement_for_korean_passport(dest['name_kr'])
                        country, entry_info = get_entry_requirement_for_korean_passport(dest['name_kr'])
                        st.markdown("#### 🛂 한국 여권 기준 비자/입국 조건")
                        st.markdown(
                            f"""
                            - **비자 필요 여부**: {entry_info['visa']}
                            - **체류 가능 기간**: {entry_info['stay']}
                            - **ESTA / ETA 필요 여부**: {entry_info['eta']}
                            - **여권 유효기간 조건**: {entry_info['passport']}
                            """
                        )
                        if is_search_based:
                            st.caption("※ 위 정보는 실시간 검색 요약입니다. 예약/출국 전 외교부 해외안전여행 및 해당국 대사관 공지로 최종 확인하세요.")
                            if entry_info.get("source"):
                                st.link_button("🔎 참고 링크(검색 결과)", entry_info["source"])
                        if country not in ENTRY_REQUIREMENTS_BY_COUNTRY:
                            st.caption("※ 자동 요약에 없는 국가입니다. 출국 전 외교부 해외안전여행 및 해당국 대사관 공지를 꼭 확인하세요.")

                        bgm_title, bgm_url = get_destination_bgm(dest['name_kr'])
                        st.markdown("#### 🎵 여행지 무드 BGM")
                        st.caption(bgm_title)
                        st.video(bgm_url)

                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("#### 🗓️ 추천 일정")
                            itinerary_items = dest.get('itinerary', [])
                            if isinstance(itinerary_items, list):
                                for item in itinerary_items:
                                    st.markdown(f"- {item}")
                            else:
                                st.write(itinerary_items)

                        with col_b:
                            st.markdown("#### 💰 예상 예산")
                            st.success(f"**{dest['total_budget']}**")
                            budget_items = dest.get('budget_detail', [])
                            if isinstance(budget_items, list):
                                for item in budget_items:
                                    st.caption(f"• {item}")
                            else:
                                st.caption(budget_items)

                        st.markdown("---")
                        url = f"https://www.skyscanner.co.kr/transport/flights/sela/{dest['airport_code']}"
                        st.link_button(f"✈️ {dest['name_kr']} 항공권 검색", url)

                st.markdown("---")
                st.markdown("### 🗳️ 친구들에게 투표받기")
                share_options = [f"{idx + 1}. {d['name_kr']}" for idx, d in enumerate(destinations[:3])]
                share_text = (
                    "나 이번에 여행 가는데 어디가 좋을까? "
                    + " ".join(share_options)
                    + " 투표 좀!"
                )
                render_kakao_share_copy_button(share_text)
                st.caption("예시: 나 이번에 여행 가는데 어디가 좋을까? 1. 몽골(별 쏟아짐) 2. 치앙마이(힐링) 3. 다낭(가성비) 투표 좀!")
                st.text_area("공유 텍스트 미리보기", value=share_text, height=90)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
