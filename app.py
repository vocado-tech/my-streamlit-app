import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import json
import pandas as pd
import requests
import re
from datetime import datetime
from urllib.parse import quote_plus
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
    "필리핀": {
        "visa": "30일 이하 무비자",
        "stay": "최대 30일",
        "eta": "eTravel 등록 필요",
        "passport": "입국일 기준 6개월 이상 유효기간 필요",
    },
    "인도네시아": {
        "visa": "단기 관광 시 도착비자(VOA) 또는 e-VOA",
        "stay": "통상 최대 30일 (연장 가능)",
        "eta": "전자 세관신고(e-CD) 등 입국 전 절차 확인 권장",
        "passport": "입국일 기준 6개월 이상 유효기간 필요",
    },
    "인도": {
        "visa": "비자 필요",
        "stay": "승인 비자 조건에 따름",
        "eta": "e-Visa 사전 신청 가능",
        "passport": "입국일 기준 6개월 이상 유효기간 필요",
    },
    "스위스": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "오스트리아": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "체코": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "헝가리": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "핀란드": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "노르웨이": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "덴마크": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "벨기에": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "아일랜드": {
        "visa": "단기 방문 무비자",
        "stay": "통상 최대 90일",
        "eta": "향후 ETA 시행 가능, 최신 공지 확인 필요",
        "passport": "체류기간 동안 유효한 여권 필요",
    },
    "멕시코": {
        "visa": "무비자 입국 가능",
        "stay": "통상 최대 180일 (심사관 재량)",
        "eta": "ESTA/ETA 불필요",
        "passport": "체류기간 동안 유효한 여권 필요",
    },
}


REPRESENTATIVE_FOOD_BY_DESTINATION = {
    "일본": "라멘",
    "오사카": "타코야키",
    "도쿄": "스시",
    "중국": "샤오룽바오",
    "대만": "우육면",
    "홍콩": "딤섬",
    "베트남": "쌀국수",
    "태국": "팟타이",
    "싱가포르": "칠리 크랩",
    "미국": "바비큐",
    "프랑스": "크루아상",
    "이탈리아": "피자",
    "스페인": "빠에야",
    "튀르키예": "케밥",
    "호주": "미트파이",
    "멕시코": "타코",
}


ZONE_CLIMATE_STATS = {
    "열대몬순": {
        "temp": [27, 28, 29, 30, 30, 29, 29, 29, 29, 29, 28, 27],
        "rain": [20, 30, 50, 90, 220, 180, 170, 190, 300, 240, 80, 30],
        "rainy_season": [5, 6, 7, 8, 9, 10],
        "typhoon_season": [],
        "notes": "스콜성 소나기가 잦아 우산/방수 신발이 유용합니다.",
    },
    "동아시아해양": {
        "temp": [6, 7, 11, 16, 21, 24, 28, 29, 25, 20, 14, 8],
        "rain": [55, 60, 95, 120, 135, 180, 210, 190, 170, 120, 85, 55],
        "rainy_season": [6, 7],
        "typhoon_season": [8, 9, 10],
        "notes": "장마/태풍 시기엔 항공·페리 지연 가능성을 감안해야 합니다.",
    },
    "지중해": {
        "temp": [8, 9, 12, 16, 20, 25, 29, 29, 25, 20, 14, 10],
        "rain": [80, 70, 60, 55, 40, 20, 8, 15, 40, 85, 95, 90],
        "rainy_season": [11, 12, 1, 2],
        "typhoon_season": [],
        "notes": "여름철은 덥고 건조해 한낮 야외활동 난도가 높습니다.",
    },
    "온대대륙": {
        "temp": [-1, 1, 6, 12, 18, 22, 25, 24, 19, 13, 6, 1],
        "rain": [45, 40, 45, 55, 70, 75, 70, 65, 55, 50, 50, 45],
        "rainy_season": [6, 7, 8],
        "typhoon_season": [],
        "notes": "겨울엔 결빙/한파, 여름엔 소나기 가능성을 고려하세요.",
    },
    "사막": {
        "temp": [19, 21, 25, 30, 34, 36, 39, 39, 35, 31, 26, 21],
        "rain": [15, 20, 15, 8, 3, 1, 1, 1, 1, 2, 6, 12],
        "rainy_season": [],
        "typhoon_season": [],
        "notes": "한낮 폭염과 큰 일교차를 감수해야 하며 수분 보충이 중요합니다.",
    },
}


COUNTRY_CLIMATE_ZONE = {
    "태국": "열대몬순",
    "베트남": "열대몬순",
    "싱가포르": "열대몬순",
    "말레이시아": "열대몬순",
    "대만": "동아시아해양",
    "일본": "동아시아해양",
    "홍콩": "동아시아해양",
    "중국": "온대대륙",
    "미국": "온대대륙",
    "캐나다": "온대대륙",
    "영국": "온대대륙",
    "프랑스": "지중해",
    "이탈리아": "지중해",
    "스페인": "지중해",
    "포르투갈": "지중해",
    "독일": "온대대륙",
    "네덜란드": "온대대륙",
    "튀르키예": "지중해",
    "아랍에미리트": "사막",
    "호주": "온대대륙",
    "뉴질랜드": "온대대륙",
}


# 1. 페이지 설정 (유지)
st.set_page_config(page_title="NoRegret Trip", page_icon="✈️", layout="wide")

st.title("✈️ NoRegret Trip")
st.subheader("여행 가자 ^~^")

st.markdown(
    """
    <style>
    .cloud-chat-helper {
        position: fixed;
        left: 16px;
        top: 88px;
        z-index: 1001;
        background: #ffffff;
        color: #2f3e46;
        border: 1px solid #d0d7de;
        border-radius: 16px;
        padding: 8px 12px;
        font-size: 14px;
        font-weight: 600;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.14);
    }
    .cloud-chat-helper::after {
        content: "";
        position: absolute;
        left: 18px;
        bottom: -8px;
        width: 14px;
        height: 14px;
        background: #ffffff;
        border-right: 1px solid #d0d7de;
        border-bottom: 1px solid #d0d7de;
        transform: rotate(45deg);
    }
    .st-key-cloud_chat_icon {
        position: fixed;
        left: 16px;
        top: 132px;
        z-index: 1000;
    }
    .st-key-cloud_chat_icon button {
        border-radius: 999px;
        width: 44px;
        height: 44px;
        padding: 0;
        font-size: 28px;
        border: 1px solid #cfd8dc;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "latest_destinations" not in st.session_state:
    st.session_state.latest_destinations = []
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! ☁️ 추천이 마음에 안 들면 어떤 점이 별로였는지 말해 주세요. 더 잘 맞는 후보를 짧게 다시 추천해 드릴게요.",
        }
    ]


def get_followup_recommendations(api_key: str, user_message: str, destinations, profile_summary: str):
    """재추천·일정·관광지 제안을 포함한 여행 챗봇 응답을 생성합니다."""
    if not api_key:
        return "사이드바에 OpenAI API Key를 입력하면 바로 다시 추천해 드릴 수 있어요."

    destination_summary = "\n".join(
        [f"- {d.get('name_kr', '')}: {d.get('reason', '')}" for d in destinations[:3]]
    ) or "- 아직 추천 결과 없음"

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.8,
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 여행 도우미 챗봇입니다. "
                    "사용자의 의도를 먼저 파악해 아래 원칙으로 한국어로 답하세요. "
                    "1) 추천이 마음에 들지 않는다고 하면 공감 1문장 + 대체 여행지 2곳을 불릿으로 짧게 제안. "
                    "2) 추천이 마음에 들어 일정/관광지 요청을 하면 사용자의 요구를 반영한 일정 또는 관광지 리스트를 불릿으로 제안. "
                    "3) 정보가 부족하면 최대 2개의 짧은 확인 질문을 먼저 제시. "
                    "과도한 설명은 줄이고 바로 실행 가능한 제안을 중심으로 답하세요."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"[사용자 여행 프로필]\n{profile_summary}\n\n"
                    f"[직전 추천]\n{destination_summary}\n\n"
                    f"[사용자 피드백]\n{user_message}"
                ),
            },
        ],
    )

    return response.choices[0].message.content


st.markdown('<div class="cloud-chat-helper">내가 도와줄게...</div>', unsafe_allow_html=True)

if st.button("☁️", key="cloud_chat_icon", help="추천 재요청 챗봇 열기/닫기"):
    st.session_state.chat_open = not st.session_state.chat_open


def _extract_destination_keywords(query: str):
    """도시명(국가명) 형태 문자열에서 검색용 키워드를 추출합니다."""
    base = query.strip()
    if "(" in base:
        base = base.split("(")[0].strip()
    return [query, base]


def _extract_country_name(query: str):
    """도시명(국가명) 형태 문자열에서 국가명만 분리합니다."""
    match = re.search(r"\((.*?)\)", query)
    if match:
        return match.group(1).strip()
    return ""


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


def _get_unsplash_image(query: str):
    """Unsplash Source URL을 이용해 검색어 기반 이미지를 반환합니다."""
    keywords = _extract_destination_keywords(query)

    for keyword in keywords:
        try:
            encoded_query = requests.utils.quote(keyword)
            candidate_url = f"https://source.unsplash.com/1600x900/?{encoded_query}"
            response = requests.get(candidate_url, timeout=8, allow_redirects=True)
            response.raise_for_status()
            if "images.unsplash.com" in response.url:
                return response.url
        except requests.RequestException:
            continue

    return None


def get_landmark_image(query: str):
    """Unsplash + DuckDuckGo + Wikipedia 순으로 대표 이미지를 가져옵니다."""
    unsplash_image = _get_unsplash_image(f"{query} landmark")
    if unsplash_image:
        return unsplash_image, None

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
        return None, "Unsplash 또는 보조 이미지 서비스 접근이 제한되어 이미지를 불러오지 못했어요."


def get_representative_food(query: str):
    """도시/국가 기준 대표 먹거리 이름과 이미지를 반환합니다."""
    keywords = _extract_destination_keywords(query)
    country_name = _extract_country_name(query)
    if country_name:
        keywords.append(country_name)

    food_name = None
    for keyword in keywords:
        if keyword in REPRESENTATIVE_FOOD_BY_DESTINATION:
            food_name = REPRESENTATIVE_FOOD_BY_DESTINATION[keyword]
            break

    if not food_name:
        food_name = "현지 대표 요리"

    image_query = food_name if food_name != "현지 대표 요리" else f"{keywords[0]} 대표 음식"

    unsplash_image = _get_unsplash_image(image_query)
    if unsplash_image:
        return food_name, unsplash_image, None

    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.images(
                    keywords=image_query,
                    region="kr-kr",
                    safesearch="moderate",
                    size="Medium",
                    max_results=1,
                )
            )

        if results and results[0].get("image"):
            return food_name, results[0]["image"], None
    except Exception:
        pass

    food_image = _get_wikipedia_image(food_name)
    if food_image:
        return food_name, food_image, None

    return food_name, None, "대표 먹거리 이미지를 찾지 못했어요."


def get_best_travel_season(latitude: float):
    """위도 기반으로 여행하기 좋은 시기를 추천합니다."""
    abs_lat = abs(latitude)

    if abs_lat < 15:
        return "연중 여행 가능 (우기/건기 확인 권장)"

    if latitude >= 0:
        return "4~6월, 9~10월 (기온이 온화하고 이동이 편한 시기)"

    return "10~12월, 3~4월 (남반구 기준 쾌적한 계절)"


def _get_trip_months(travel_dates):
    """선택된 여행 날짜 범위에서 포함된 월 목록을 계산합니다."""
    if not travel_dates:
        return [datetime.now().month]

    if isinstance(travel_dates, (list, tuple)) and len(travel_dates) == 2:
        start_date, end_date = travel_dates
        if start_date > end_date:
            start_date, end_date = end_date, start_date
    else:
        start_date = end_date = travel_dates

    months = []
    cursor = datetime(start_date.year, start_date.month, 1)
    end_cursor = datetime(end_date.year, end_date.month, 1)

    while cursor <= end_cursor:
        months.append(cursor.month)
        if cursor.month == 12:
            cursor = datetime(cursor.year + 1, 1, 1)
        else:
            cursor = datetime(cursor.year, cursor.month + 1, 1)

    return months or [datetime.now().month]


def get_seasonal_travel_note(destination_name: str, latitude: float, travel_dates):
    """여행 기간 평균 기후와 우기/태풍 시즌 경고를 반환합니다."""
    country = extract_country_from_destination(destination_name)
    zone = COUNTRY_CLIMATE_ZONE.get(country)

    if not zone:
        zone = "온대대륙" if abs(latitude) >= 20 else "열대몬순"

    climate = ZONE_CLIMATE_STATS[zone]
    months = _get_trip_months(travel_dates)
    month_indexes = [month - 1 for month in months]

    avg_temp = sum(climate["temp"][idx] for idx in month_indexes) / len(month_indexes)
    avg_rain = sum(climate["rain"][idx] for idx in month_indexes) / len(month_indexes)

    rainy_overlap = [m for m in months if m in climate["rainy_season"]]
    typhoon_overlap = [m for m in months if m in climate["typhoon_season"]]

    cautions = []
    if rainy_overlap:
        cautions.append(
            f"⚠️ {', '.join(map(str, rainy_overlap))}월은 우기/강수 집중 구간입니다. {climate['notes']}"
        )
    if typhoon_overlap:
        cautions.append(
            f"⚠️ {', '.join(map(str, typhoon_overlap))}월은 태풍 영향 가능성이 있습니다. 일정 변동 가능성을 꼭 감안하세요."
        )

    if not cautions:
        cautions.append("✅ 선택한 기간은 계절 리스크가 비교적 낮은 편입니다.")

    tradeoff = "지금 가면 이런 점은 감수해야 합니다: "
    if avg_rain >= 150:
        tradeoff += "실외 일정 중 갑작스러운 비로 동선이 자주 끊길 수 있어요."
    elif avg_temp >= 32:
        tradeoff += "낮 시간대 야외 활동 피로도가 높아질 수 있어요."
    elif avg_temp <= 3:
        tradeoff += "일몰 후 체감온도가 낮아 방한 준비가 필수예요."
    else:
        tradeoff += "관광 밀집 시간대와 일교차를 고려해 일정에 여유를 두는 것이 좋아요."

    return (
        f"여행 기간 평균 기온은 **약 {avg_temp:.1f}°C**, 평균 강수량은 **약 {avg_rain:.0f}mm/월**입니다.\n"
        + "\n".join(cautions)
        + f"\n\n💬 {tradeoff}"
    )


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


def build_regret_summary(regret_risk_warnings):
    """후회 가능성 경고 목록을 상단 요약용 추천도 별점/한줄로 변환합니다."""
    warning_count = len(regret_risk_warnings)
    recommended_stars = max(1, 5 - warning_count)
    star_rating = "".join(["⭐" for _ in range(recommended_stars)] + ["☆" for _ in range(5 - recommended_stars)])
    if warning_count:
        one_liner = regret_risk_warnings[0]
    else:
        one_liner = "전반적으로 잘 맞는 여행지지만, 완벽한 여행지는 없어서 소소한 불편은 있을 수 있어요."
    return star_rating, one_liner


def ensure_minimum_regret_warning(regret_risk_warnings):
    """후회 가능성 상세에 항상 최소 1개 경고가 노출되도록 보정합니다."""
    if regret_risk_warnings:
        return regret_risk_warnings
    return ["⚠️ 완벽한 여행지는 없어요. 숙소/자연환경에 따라 벌레가 보일 수 있으니 방충 대비를 챙기세요."]


def build_weather_core_summary(weather_summary: str):
    """날씨 상세 텍스트에서 상단 요약용 핵심 정보를 추출합니다."""
    if "현재 날씨는" not in weather_summary:
        return weather_summary

    weather_match = re.search(
        r"현재 날씨는 \*\*(.*?)\*\*, 기온은 \*\*([\d\.-]+°C)\*\* \(체감 \*\*([\d\.-]+°C)\*\*\).+?약 (\d+)회",
        weather_summary,
    )
    if not weather_match:
        return weather_summary

    current_weather, current_temp, feels_like, rainy_slots = weather_match.groups()
    rainy_slots = int(rainy_slots)
    rainy_flag = "우산 준비" if rainy_slots >= 4 else "우기 아님"
    return f"{current_weather} / {current_temp} / 체감 {feels_like} / {rainy_flag}"


def build_weather_emoji_display(weather_summary: str):
    """날씨 핵심 문구를 이모지+설명으로 변환합니다."""
    weather_core = build_weather_core_summary(weather_summary)
    lower_text = weather_core.lower()

    if any(keyword in lower_text for keyword in ["비", "소나기", "rain", "drizzle"]):
        weather_emoji = "🌧️"
    elif any(keyword in lower_text for keyword in ["눈", "snow"]):
        weather_emoji = "❄️"
    elif any(keyword in lower_text for keyword in ["흐림", "구름", "cloud"]):
        weather_emoji = "☁️"
    elif any(keyword in lower_text for keyword in ["천둥", "storm", "번개"]):
        weather_emoji = "⛈️"
    else:
        weather_emoji = "☀️"

    return weather_emoji, weather_core


def build_budget_range_summary(total_budget_text: str):
    """총 예산 문구에서 ± 범위를 추정해 요약합니다."""
    numbers = [int(value.replace(",", "")) for value in re.findall(r"\d[\d,]*", total_budget_text)]
    if not numbers:
        return total_budget_text

    if len(numbers) >= 2:
        low, high = min(numbers), max(numbers)
        center = (low + high) / 2
        spread = (high - low) / 2
    else:
        center = numbers[0]
        spread = center * 0.2

    center_manwon = center / 10000
    spread_manwon = spread / 10000
    return f"약 {center_manwon:,.0f}만원 (±{spread_manwon:,.0f}만원)"


def to_manwon_text(raw_text: str):
    """숫자/원 단위 텍스트를 만원 단위 텍스트로 변환합니다."""
    numbers = [int(value.replace(",", "")) for value in re.findall(r"\d[\d,]*", raw_text)]
    if not numbers:
        return raw_text

    manwon_values = [f"{number / 10000:,.0f}만원" for number in numbers]

    if len(manwon_values) == 1:
        return f"약 {manwon_values[0]}"
    return " ~ ".join(manwon_values)


def build_primary_caution(regret_risk_warnings, seasonal_note: str):
    """상단 요약에 노출할 1줄 주의문을 반환합니다."""
    if regret_risk_warnings:
        return regret_risk_warnings[0]

    seasonal_alerts = [line.strip() for line in seasonal_note.splitlines() if line.strip().startswith("⚠️")]
    if seasonal_alerts:
        return seasonal_alerts[0]

    return "⚠️ 일교차와 야간 기온을 고려해 얇은 겉옷을 챙기세요."


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
    """여행지 분위기/지역성을 반영한 유튜브 BGM 플레이리스트를 반환합니다."""
    city = name_kr.split("(")[0].strip()
    country = extract_country_from_destination(name_kr)

    city_bgm_map = {
        "파리": ("파리 재즈 카페 & 샹송 무드", "https://www.youtube.com/watch?v=cTLTG4FTNBQ"),
        "도쿄": ("도쿄 시티팝 드라이브", "https://www.youtube.com/watch?v=3bNITQR4Uso"),
        "오사카": ("오사카 네온 스트리트 시티팝", "https://www.youtube.com/watch?v=3bNITQR4Uso"),
        "교토": ("교토 전통 악기 힐링 무드", "https://www.youtube.com/watch?v=4zG7WcW2nQ4"),
        "치앙마이": ("치앙마이 카페 감성 로파이", "https://www.youtube.com/watch?v=5qap5aO4i9A"),
        "방콕": ("방콕 루프탑 나이트 무드", "https://www.youtube.com/watch?v=JfVOs4VSpmA"),
        "다낭": ("다낭 해변 선셋 칠 음악", "https://www.youtube.com/watch?v=DWcJFNfaw9c"),
        "하노이": ("하노이 올드쿼터 베트남 감성", "https://www.youtube.com/watch?v=uaf4iR5Vw9s"),
        "뉴올리언스": ("뉴올리언스 스트리트 재즈", "https://www.youtube.com/watch?v=Dx5qFachd3A"),
        "리스본": ("리스본 파두(Fado) 감성", "https://www.youtube.com/watch?v=QhBwrn7fG9k"),
        "세비야": ("세비야 플라멩코 무드", "https://www.youtube.com/watch?v=t4H_Zoh7G5A"),
        "이비사": ("이비사 비치 하우스 뮤직", "https://www.youtube.com/watch?v=1bJY4wF2J3A"),
        "두바이": ("사막 드라이브 아라비안 라운지", "https://www.youtube.com/watch?v=4jP06Wk6M4Q"),
        "카이로": ("카이로 아라빅 오리엔탈 무드", "https://www.youtube.com/watch?v=_O6fQkS3SIA"),
        "울란바토르": ("몽골 초원 & 호미(Hoomei) 무드", "https://www.youtube.com/watch?v=9e9v4M9RjvY"),
    }

    country_bgm_map = {
        "일본": ("일본 여행 무드 시티팝/재즈", "https://www.youtube.com/watch?v=3bNITQR4Uso"),
        "중국": ("중국 전통 악기 + 현대 퓨전 무드", "https://www.youtube.com/watch?v=9U8kbM_BhWc"),
        "대만": ("대만 야시장 감성 인디팝", "https://www.youtube.com/watch?v=qM4vYf6A5LQ"),
        "홍콩": ("홍콩 야경 시네마틱 무드", "https://www.youtube.com/watch?v=AD8G7f8J6Vg"),
        "베트남": ("베트남 로컬 감성 어쿠스틱", "https://www.youtube.com/watch?v=uaf4iR5Vw9s"),
        "태국": ("태국 트로피컬 칠 & 로컬 무드", "https://www.youtube.com/watch?v=JfVOs4VSpmA"),
        "싱가포르": ("싱가포르 마리나 베이 라운지", "https://www.youtube.com/watch?v=6zXDo4dL7SU"),
        "미국": ("미국 로드트립 클래식 플레이리스트", "https://www.youtube.com/watch?v=gEPmA3USJdI"),
        "영국": ("런던 브릿팝 & 인디 감성", "https://www.youtube.com/watch?v=VbfpW0pbvaU"),
        "프랑스": ("프랑스 샹송 & 파리지앵 재즈", "https://www.youtube.com/watch?v=cTLTG4FTNBQ"),
        "스페인": ("스페인 플라멩코 & 기타 무드", "https://www.youtube.com/watch?v=t4H_Zoh7G5A"),
        "포르투갈": ("포르투갈 파두(Fado) 감성", "https://www.youtube.com/watch?v=QhBwrn7fG9k"),
        "튀르키예": ("이스탄불 보스포루스 오리엔탈 무드", "https://www.youtube.com/watch?v=T4k_qws0k4E"),
        "아랍에미리트": ("중동 라운지 & 아라비안 나이트", "https://www.youtube.com/watch?v=4jP06Wk6M4Q"),
        "이집트": ("이집트 전통 리듬 & 오리엔탈 무드", "https://www.youtube.com/watch?v=_O6fQkS3SIA"),
        "몽골": ("몽골 전통/초원 무드 사운드", "https://www.youtube.com/watch?v=9e9v4M9RjvY"),
    }

    fallback_candidates = [
        ("잔잔한 여행 로파이 라이브", "https://www.youtube.com/watch?v=jfKfPfyJRdk"),
        ("여행 브이로그용 감성 BGM 모음", "https://www.youtube.com/watch?v=DWcJFNfaw9c"),
    ]

    for keyword, bgm_info in city_bgm_map.items():
        if keyword in city:
            return pick_available_bgm([bgm_info], f"{city} travel bgm playlist")

    for keyword, bgm_info in country_bgm_map.items():
        if keyword in country:
            return pick_available_bgm([bgm_info], f"{country} travel bgm playlist")

    return pick_available_bgm(
        [
            (f"{country} 여행 분위기에 어울리는 로컬/무드 음악", "https://www.youtube.com/watch?v=2OEL4P1Rz04"),
            *fallback_candidates,
        ],
        f"{country} travel bgm playlist",
    )


@st.cache_data(ttl=3600)
def is_youtube_video_available(url: str):
    """YouTube oEmbed 응답으로 재생 가능한 영상인지 확인합니다."""
    try:
        response = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": url, "format": "json"},
            timeout=4,
        )
        return response.status_code == 200
    except Exception:
        return False


def pick_available_bgm(candidates, search_query: str):
    """후보 링크 중 재생 가능한 BGM을 우선 선택하고, 없으면 검색 결과에서 대체합니다."""
    for title, url in candidates:
        if is_youtube_video_available(url):
            return title, url

    try:
        with DDGS() as ddgs:
            items = list(
                ddgs.text(
                    keywords=f"site:youtube.com {search_query}",
                    region="wt-wt",
                    safesearch="moderate",
                    max_results=8,
                )
            )

        for item in items:
            title = item.get("title", "추천 BGM")
            href = item.get("href", "")
            if "youtube.com/watch" in href and is_youtube_video_available(href):
                return f"{title} (자동 추천)", href
    except Exception:
        pass

    return "재생 가능한 BGM을 찾지 못해 기본 라이브를 대신 재생합니다", "https://www.youtube.com/watch?v=jfKfPfyJRdk"


def extract_country_from_destination(name_kr: str):
    """도시명 (국가명) 문자열에서 국가명만 추출합니다."""
    if "(" in name_kr and ")" in name_kr:
        return name_kr.split("(")[-1].replace(")", "").strip()
    return name_kr.strip()


def get_regret_risk_warnings(style: str, destination_name: str, reason_text: str):
    """여행 스타일 미스매치 + 목적지의 보편적 리스크를 후회 가능성 경고로 반환합니다."""
    text = f"{destination_name} {reason_text}".lower()
    city = destination_name.split("(")[0].strip()
    destination_traits = {
        "쇼핑/도시": ["쇼핑", "야경", "도시", "몰", "백화점", "city", "nightlife"],
        "휴양/바다": ["휴양", "리조트", "해변", "바다", "비치", "beach"],
        "관광/유적": ["관광", "유적", "박물관", "역사", "궁전", "성당", "heritage"],
        "대자연/트레킹": ["대자연", "트레킹", "하이킹", "산", "국립공원", "빙하", "safari"],
        "미식/로컬푸드": ["미식", "로컬푸드", "야시장", "맛집", "레스토랑", "gourmet"],
    }
    mismatch_messages = {
        "휴양/바다 (물놀이)": {
            "쇼핑/도시": "⚠️ 이 도시는 쇼핑/야경 중심이라 물놀이·휴양 비중이 기대보다 낮을 수 있어요.",
            "관광/유적": "⚠️ 이 여행지는 역사·도보 관광 비중이 있어 완전 휴양형 여행과는 결이 다를 수 있어요.",
        },
        "관광/유적 (많이 걷기)": {
            "쇼핑/도시": "⚠️ 이 도시는 쇼핑/야경 중심이라 관광지를 많이 보는 스타일과는 맞지 않을 수 있습니다.",
            "휴양/바다": "⚠️ 휴양 중심 동선이면 유적·역사 탐방 밀도가 낮아 아쉬울 수 있어요.",
        },
        "쇼핑/도시": {
            "대자연/트레킹": "⚠️ 이 목적지는 자연/트레킹 중심이라 쇼핑 인프라가 제한적일 수 있어요.",
            "휴양/바다": "⚠️ 휴양지 특성상 대형 쇼핑 스폿이 적어 도시형 쇼핑 여행과 결이 다를 수 있어요.",
        },
        "대자연/트레킹": {
            "쇼핑/도시": "⚠️ 도시/쇼핑 비중이 높아 대자연 체험 시간을 충분히 확보하기 어려울 수 있어요.",
            "휴양/바다": "⚠️ 해변 휴양 중심 일정이면 트레킹 강도가 기대보다 약할 수 있어요.",
        },
        "미식/로컬푸드": {
            "대자연/트레킹": "⚠️ 자연/트레킹 위주 여행지는 식도락 선택지가 제한될 수 있어요.",
        },
    }

    generic_risk_rules = [
        {
            "keywords": ["스위스", "아이슬란드", "두바이", "런던", "뉴욕", "파리", "싱가포르"],
            "message": "⚠️ 현지 물가가 높은 편이라 식비·교통비·입장료가 예상보다 커질 수 있어요.",
        },
        {
            "keywords": ["런던", "파리", "암스테르담", "아이슬란드", "영국"],
            "message": "⚠️ 비·강풍 등 변덕스러운 날씨로 실외 일정이 자주 바뀔 수 있어요.",
        },
        {
            "keywords": ["로마", "바르셀로나", "파리", "방콕"],
            "message": "⚠️ 관광객이 많은 지역은 소매치기·잡상인 이슈가 있어 동선별 주의가 필요해요.",
        },
    ]

    distance_risk_rules = [
        {
            "keywords": ["미국", "캐나다", "영국", "프랑스", "독일", "스페인", "포르투갈", "이탈리아", "아이슬란드"],
            "message": "⚠️ 장거리 노선은 비행시간이 길고 시차 적응이 필요해, 실제 관광 가능한 시간이 예상보다 줄 수 있어요.",
        },
        {
            "keywords": ["이집트", "크로아티아", "포르투갈", "핀란드", "체코", "헝가리", "오스트리아", "노르웨이"],
            "message": "⚠️ 출발일/도시 조합에 따라 직항이 없거나 좌석이 적어 경유 대기시간이 길어질 수 있어요.",
        },
    ]

    local_adaptation_rules = [
        {
            "keywords": ["인도", "이집트", "몽골", "라오스", "베트남", "태국"],
            "message": "⚠️ 향신료·조리 방식·수질 차이로 음식이 낯설 수 있어 첫날은 무난한 메뉴로 적응하는 편이 안전해요.",
        },
        {
            "keywords": ["두바이", "아랍에미리트", "카이로", "울란바토르"],
            "message": "⚠️ 기온 편차(한낮 고온/야간 저온)나 건조한 공기로 컨디션이 흔들릴 수 있어 복장/보습 대비가 필요해요.",
        },
        {
            "keywords": ["런던", "암스테르담", "아이슬란드", "뉴질랜드"],
            "message": "⚠️ 날씨 변동 폭이 큰 지역이라 같은 날에도 비·바람이 반복될 수 있어 실내 대안 동선을 준비해 두세요.",
        },
    ]

    city_specific_risks = {
        "뉴욕": "⚠️ 맨해튼 중심 숙소/교통비가 높아 보이는 예산보다 현지 지출이 빠르게 커질 수 있어요.",
        "파리": "⚠️ 주요 관광지는 대기줄이 길어 사전 예약이 없으면 하루 동선이 크게 밀릴 수 있어요.",
        "런던": "⚠️ 지하철 파업·공사 이슈가 간헐적으로 있어 이동 동선 플랜B를 준비하는 것이 좋아요.",
        "방콕": "⚠️ 출퇴근 시간대 교통체증이 심해, 지도상 거리보다 이동시간이 2배 이상 걸릴 수 있어요.",
        "도쿄": "⚠️ 러시아워 전철 혼잡도가 높아 캐리어 이동은 피크 시간을 피하는 편이 좋아요.",
        "로마": "⚠️ 인기 유적지는 휴관일·예약 슬롯 변동이 잦아 일정 확정 전에 운영시간 재확인이 필요해요.",
    }

    detected_traits = {
        trait
        for trait, keywords in destination_traits.items()
        if any(keyword in text for keyword in keywords)
    }

    warnings = []
    for trait in detected_traits:
        warning = mismatch_messages.get(style, {}).get(trait)
        if warning and warning not in warnings:
            warnings.append(warning)

    for rule in generic_risk_rules:
        if any(keyword.lower() in text for keyword in rule["keywords"]):
            if rule["message"] not in warnings:
                warnings.append(rule["message"])

    for rule in distance_risk_rules:
        if any(keyword.lower() in text for keyword in rule["keywords"]):
            if rule["message"] not in warnings:
                warnings.append(rule["message"])

    for rule in local_adaptation_rules:
        if any(keyword.lower() in text for keyword in rule["keywords"]):
            if rule["message"] not in warnings:
                warnings.append(rule["message"])

    for keyword, message in city_specific_risks.items():
        if keyword in city and message not in warnings:
            warnings.append(message)

    fallback_messages = [
        "⚠️ 성수기에는 항공권·숙소 가격이 급등해 같은 예산으로 체감 퀄리티가 낮아질 수 있어요.",
        "⚠️ 관광지 오픈시간/휴무일이 수시로 바뀌므로 핵심 스팟은 공식 사이트에서 재확인하세요.",
        "⚠️ 현지 교통 파업·행사·우천 변수로 당일 동선이 바뀔 수 있어 대체 코스를 미리 정해두는 게 좋아요.",
    ]

    for message in fallback_messages:
        if len(warnings) >= 3:
            break
        if message not in warnings:
            warnings.append(message)

    return warnings


def get_destination_issue_summary(destination_name: str):
    """검색 결과 스니펫을 바탕으로 여행지의 자주 언급되는 이슈를 요약합니다."""
    search_query = f"{destination_name} 여행 단점 문제점 주의할 점"

    try:
        with DDGS() as ddgs:
            items = list(
                ddgs.text(
                    keywords=search_query,
                    region="kr-kr",
                    safesearch="moderate",
                    max_results=4,
                )
            )

        if not items:
            return ["검색 기반 문제점을 찾지 못했어요. 최신 후기는 출발 전 다시 확인해 주세요."], None

        issue_summaries = []
        for item in items[:3]:
            title = item.get("title", "검색 결과")
            snippet = item.get("body", "요약 정보 없음")
            issue_summaries.append(f"- **{title}**: {snippet}")

        source = items[0].get("href")
        return issue_summaries, source
    except Exception as exc:
        return [f"문제점 검색 요약을 가져오지 못했어요: {exc}"], None


def _summarize_entry_requirement_from_search(country: str):
    """검색 결과 스니펫을 바탕으로 비자/입국 요건을 요약합니다."""
    search_query = f"{country} 대한민국 여권 비자 체류 기간 ETA ESTA 여권 유효기간"
    search_results_url = f"https://duckduckgo.com/?q={quote_plus(search_query)}"

    fallback = {
        "visa": "검색 결과 기준 최신 정책 확인 필요",
        "stay": "검색 결과에서 체류기간 확인 필요",
        "eta": "검색 결과에서 ETA/ESTA 여부 확인 필요",
        "passport": "대부분 국가에서 6개월 이상 유효기간 권장",
        "source": search_results_url,
    }

    try:
        with DDGS() as ddgs:
            items = list(
                ddgs.text(
                    keywords=search_query,
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

        return {
            "visa": visa,
            "stay": stay,
            "eta": eta,
            "passport": passport,
            "source": search_results_url,
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
    no_drive = st.checkbox("운전 못해요ㅠㅠ (렌트카 없이 다니고 싶어요)")

today = datetime.now().date()
travel_dates = st.date_input(
    "여행 날짜 (선택)",
    value=(today, today),
    min_value=today,
    help="오늘 이후 일정만 선택할 수 있어요. 선택한 기간 기준으로 평균 기온/강수량과 우기·태풍 정보를 안내합니다.",
)

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
                - 운전 가능 여부: {'어려움 (렌트카 없이 이동 선호)' if no_drive else '가능'}
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
                   - 사용자가 "운전 못해요ㅠㅠ"를 체크한 경우, 특히 휴양지 추천 시 렌터카 의존도가 높은 지역(대중교통/셔틀/도보 이동이 불편한 지역)은 제외하세요.

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
                - 예산 수준별 산정 기준을 반드시 반영하세요.
                  - '가성비 (아끼기)': 저가 항공(LCC) + 호스텔/게스트하우스(또는 2성급) + 대중교통/도보 중심으로 보수적으로 계산.
                  - '적당함 (평균)': 일반 항공 + 3성급 전후 호텔 + 대중교통/택시 혼합 기준으로 계산.
                  - '럭셔리 (플렉스)': 국적기/프리미엄 항공 + 5성급 호텔 + 택시/프라이빗 투어를 포함한 상향 기준으로 계산.
                - 예산 수치는 여행 기간, 성수기 여부, 목적지 물가를 반영해 과도하게 낙관적이지 않게 작성하세요.
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
                st.session_state.latest_destinations = destinations

                st.success(f"'{duration}' 동안 다녀오기 좋은, 전 세계 여행지를 엄선했습니다! 🌍")

                tabs = st.tabs([d['name_kr'] for d in destinations])

                for i, tab in enumerate(tabs):
                    with tab:
                        dest = destinations[i]
                        st.header(f"📍 {dest['name_kr']}")

                        map_data = pd.DataFrame({'lat': [dest['latitude']], 'lon': [dest['longitude']]})
                        st.map(map_data, zoom=4)

                        image_url, image_error = get_landmark_image(dest['name_kr'])
                        food_name, food_image_url, food_image_error = get_representative_food(dest['name_kr'])

                        st.markdown("#### 🖼️ 여행지/먹거리 미리보기")
                        image_col, food_col = st.columns(2)

                        with image_col:
                            if image_url:
                                st.image(
                                    image_url,
                                    caption=f"{dest['name_kr']} 대표 랜드마크",
                                    width=220,
                                )
                            else:
                                st.caption(image_error)

                        with food_col:
                            if food_image_url:
                                st.image(
                                    food_image_url,
                                    caption=f"대표 먹거리: {food_name}",
                                    width=220,
                                )
                            else:
                                st.caption(food_image_error)

                        st.info(f"💡 **추천 이유**: {dest['reason']}")

                        regret_risk_warnings = get_regret_risk_warnings(style, dest['name_kr'], dest['reason'])
                        weather_summary = get_weather_summary(dest['latitude'], dest['longitude'], weather_api_key)
                        seasonal_note = get_seasonal_travel_note(dest['name_kr'], dest['latitude'], travel_dates)
                        festival_summary = get_festival_summary(dest['name_kr'])
                        country, entry_info, is_search_based = get_entry_requirement_for_korean_passport(dest['name_kr'])

                        regret_ratings, regret_one_liner = build_regret_summary(regret_risk_warnings)
                        regret_risk_warnings = ensure_minimum_regret_warning(regret_risk_warnings)
                        weather_emoji, weather_core = build_weather_emoji_display(weather_summary)
                        budget_summary = build_budget_range_summary(dest['total_budget'])
                        total_budget_in_manwon = to_manwon_text(dest['total_budget'])

                        st.markdown("#### ✅ 상단 요약")
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        with metric_col1:
                            st.metric("추천도", regret_ratings)
                            st.caption(regret_one_liner)
                        with metric_col2:
                            st.markdown("**날씨 핵심**")
                            st.markdown(f"<div style='font-size: 4rem; line-height: 1;'>{weather_emoji}</div>", unsafe_allow_html=True)
                            st.caption(weather_core)
                        with metric_col3:
                            st.metric("예산 총액", budget_summary)
                            st.caption(total_budget_in_manwon)

                        with st.expander("🧠 😢 상세", expanded=False):
                            for warning_message in regret_risk_warnings:
                                st.warning(warning_message)

                        with st.expander("🌤️ 날씨 자세히", expanded=False):
                            st.write(weather_summary)
                            st.markdown("#### 🌦️ 여행 기간 기후/시기 적합성")
                            st.markdown(seasonal_note)

                        with st.expander("🛂 비자/입국 조건", expanded=False):
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

                        with st.expander("🎉 축제/이벤트", expanded=False):
                            st.markdown(festival_summary)

                        bgm_title, bgm_url = get_destination_bgm(dest['name_kr'])
                        with st.expander("🎵 여행지 무드 BGM", expanded=False):
                            st.caption(bgm_title)
                            st.video(bgm_url)

                        with st.expander("🗓️ 일정/예산 상세", expanded=False):
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


if st.session_state.chat_open:
    st.markdown("### ☁️ 재추천 챗봇")
    st.caption("재추천은 물론, 마음에 드는 여행지의 일정·관광지도 원하는 스타일에 맞춰 추천해 드려요.")

    chat_container = st.container(border=True)
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    user_feedback = st.chat_input("예: 재추천해줘 / 오사카 3박4일 일정 짜줘 / 비 오는 날 갈만한 관광지 추천해줘")
    if user_feedback:
        st.session_state.chat_messages.append({"role": "user", "content": user_feedback})

        profile_summary = (
            f"기간={duration}, 난이도={difficulty}, 스타일={style}, 예산={budget_level}, 동행={companion}, 운전={no_drive}, 추가요청={etc_req or '없음'}"
        )

        with st.spinner("피드백 반영해서 다시 골라볼게요..."):
            try:
                reply = get_followup_recommendations(
                    api_key=api_key,
                    user_message=user_feedback,
                    destinations=st.session_state.latest_destinations,
                    profile_summary=profile_summary,
                )
            except Exception as e:
                reply = f"재추천 중 오류가 발생했어요: {e}"

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()
