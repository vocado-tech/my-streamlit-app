import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import json
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from duckduckgo_search import DDGS


COUNTRY_NAME_ALIASES = {
    "일본": "japan",
    "중국": "china",
    "대만": "taiwan",
    "홍콩": "hong kong",
    "베트남": "vietnam",
    "태국": "thailand",
    "싱가포르": "singapore",
    "말레이시아": "malaysia",
    "미국": "united states",
    "캐나다": "canada",
    "영국": "united kingdom",
    "프랑스": "france",
    "독일": "germany",
    "이탈리아": "italy",
    "스페인": "spain",
    "포르투갈": "portugal",
    "네덜란드": "netherlands",
    "크로아티아": "croatia",
    "아이슬란드": "iceland",
    "튀르키예": "turkey",
    "아랍에미리트": "united arab emirates",
    "호주": "australia",
    "뉴질랜드": "new zealand",
    "몽골": "mongolia",
    "라오스": "laos",
    "이집트": "egypt",
    "필리핀": "philippines",
    "인도네시아": "indonesia",
    "인도": "india",
    "스위스": "switzerland",
    "오스트리아": "austria",
    "체코": "czech republic",
    "헝가리": "hungary",
    "핀란드": "finland",
    "노르웨이": "norway",
    "덴마크": "denmark",
    "벨기에": "belgium",
    "아일랜드": "ireland",
    "멕시코": "mexico",
    "스웨덴": "sweden",
    "폴란드": "poland",
    "그리스": "greece",
    "브라질": "brazil",
    "아르헨티나": "argentina",
    "칠레": "chile",
    "페루": "peru",
    "남아프리카공화국": "south africa",
    "모로코": "morocco",
    "카타르": "qatar",
    "대한민국": "south korea",
    "한국": "south korea",
    "마카오": "macao",
    "캄보디아": "cambodia",
    "미얀마": "myanmar",
    "네팔": "nepal",
    "스리랑카": "sri lanka",
    "우즈베키스탄": "uzbekistan",
    "카자흐스탄": "kazakhstan",
    "조지아": "georgia",
}

CITY_NAME_ALIASES = {
    "도쿄": "tokyo",
    "오사카": "osaka",
    "교토": "kyoto",
    "후쿠오카": "fukuoka",
    "삿포로": "sapporo",
    "나고야": "nagoya",
    "베이징": "beijing",
    "상하이": "shanghai",
    "광저우": "guangzhou",
    "선전": "shenzhen",
    "타이베이": "taipei",
    "가오슝": "kaohsiung",
    "홍콩": "hong kong",
    "하노이": "hanoi",
    "호치민": "ho chi minh city",
    "다낭": "da nang",
    "방콕": "bangkok",
    "푸켓": "phuket",
    "싱가포르": "singapore",
    "쿠알라룸푸르": "kuala lumpur",
    "뉴욕": "new york",
    "로스앤젤레스": "los angeles",
    "샌프란시스코": "san francisco",
    "밴쿠버": "vancouver",
    "토론토": "toronto",
    "런던": "london",
    "파리": "paris",
    "베를린": "berlin",
    "로마": "rome",
    "마드리드": "madrid",
    "바르셀로나": "barcelona",
    "리스본": "lisbon",
    "암스테르담": "amsterdam",
    "두브로브니크": "dubrovnik",
    "레이캬비크": "reykjavik",
    "이스탄불": "istanbul",
    "두바이": "dubai",
    "시드니": "sydney",
    "멜버른": "melbourne",
    "오클랜드": "auckland",
    "울란바토르": "ulaanbaatar",
    "비엔티안": "vientiane",
    "카이로": "cairo",
    "마닐라": "manila",
    "세부": "cebu",
    "발리": "bali",
    "자카르타": "jakarta",
    "델리": "delhi",
    "뭄바이": "mumbai",
    "취리히": "zurich",
    "빈": "vienna",
    "프라하": "prague",
    "부다페스트": "budapest",
    "헬싱키": "helsinki",
    "오슬로": "oslo",
    "코펜하겐": "copenhagen",
    "브뤼셀": "brussels",
    "더블린": "dublin",
    "스톡홀름": "stockholm",
    "바르샤바": "warsaw",
    "아테네": "athens",
    "멕시코시티": "mexico city",
    "리우데자네이루": "rio de janeiro",
    "부에노스아이레스": "buenos aires",
    "산티아고": "santiago",
    "리마": "lima",
    "케이프타운": "cape town",
    "마라케시": "marrakesh",
    "도하": "doha",
    "서울": "seoul",
    "부산": "busan",
    "제주": "jeju",
    "마카오": "macao",
    "프놈펜": "phnom penh",
    "시엠립": "siem reap",
    "양곤": "yangon",
    "카트만두": "kathmandu",
    "콜롬보": "colombo",
    "타슈켄트": "tashkent",
    "알마티": "almaty",
    "트빌리시": "tbilisi",
}

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
    "스웨덴": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "폴란드": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "그리스": {
        "visa": "쉥겐 90일 이하 무비자",
        "stay": "180일 중 최대 90일",
        "eta": "ESTA/ETA 불필요 (ETIAS 시행 시 변경 가능)",
        "passport": "출국예정일 기준 3개월 이상 + 발급 후 10년 이내",
    },
    "브라질": {
        "visa": "단기 방문 무비자",
        "stay": "최대 90일 (연장 가능 여부 별도 확인)",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국 시 통상 6개월 이상 유효기간 권장",
    },
    "아르헨티나": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "체류기간 동안 유효한 여권 필요",
    },
    "칠레": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "체류기간 이상 유효한 여권 필요",
    },
    "페루": {
        "visa": "무비자 입국 가능",
        "stay": "통상 최대 90일 (입국 심사 재량)",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국일 기준 6개월 이상 유효기간 권장",
    },
    "남아프리카공화국": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국일 기준 30일 이상 + 빈 사증면 필요",
    },
    "모로코": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국 시 통상 6개월 이상 유효기간 권장",
    },
    "카타르": {
        "visa": "무비자 입국 가능 (입국 시 체류 허가)",
        "stay": "통상 최대 30일",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국 시 통상 6개월 이상 유효기간 필요",
    },
    "대한민국": {
        "visa": "해당 없음 (자국민)",
        "stay": "해당 없음",
        "eta": "해당 없음",
        "passport": "해당 없음",
    },
    "마카오": {
        "visa": "90일 이하 무비자",
        "stay": "최대 90일",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국 시 통상 3개월 이상 유효기간 권장",
    },
    "캄보디아": {
        "visa": "비자 필요 (e-Visa/도착비자 가능)",
        "stay": "통상 30일",
        "eta": "e-Arrival Card 등 사전 등록 여부 확인 권장",
        "passport": "입국 시 6개월 이상 유효기간 필요",
    },
    "미얀마": {
        "visa": "비자 필요 (전자비자 가능 여부 수시 변동)",
        "stay": "비자 종류 및 승인 조건에 따름",
        "eta": "전자비자(eVisa) 가능 여부 최신 공지 확인 필요",
        "passport": "입국 시 6개월 이상 유효기간 필요",
    },
    "네팔": {
        "visa": "도착비자 또는 e-Visa 가능",
        "stay": "통상 15/30/90일 옵션",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국 시 6개월 이상 유효기간 권장",
    },
    "스리랑카": {
        "visa": "전자여행허가(ETA) 사전 신청 필요",
        "stay": "통상 30일",
        "eta": "스리랑카 ETA 필요",
        "passport": "입국 시 통상 6개월 이상 유효기간 필요",
    },
    "우즈베키스탄": {
        "visa": "30일 이하 무비자",
        "stay": "최대 30일",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국 시 통상 6개월 이상 유효기간 권장",
    },
    "카자흐스탄": {
        "visa": "30일 이하 무비자",
        "stay": "최대 30일",
        "eta": "ESTA/ETA 불필요",
        "passport": "입국 시 통상 6개월 이상 유효기간 권장",
    },
    "조지아": {
        "visa": "무비자 입국 가능",
        "stay": "통상 최대 1년",
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


THEMEALDB_AREA_BY_COUNTRY = {
    "미국": "American",
    "영국": "British",
    "캐나다": "Canadian",
    "중국": "Chinese",
    "크로아티아": "Croatian",
    "네덜란드": "Dutch",
    "이집트": "Egyptian",
    "프랑스": "French",
    "인도": "Indian",
    "아일랜드": "Irish",
    "이탈리아": "Italian",
    "말레이시아": "Malaysian",
    "멕시코": "Mexican",
    "폴란드": "Polish",
    "포르투갈": "Portuguese",
    "러시아": "Russian",
    "스페인": "Spanish",
    "태국": "Thai",
    "튀르키예": "Turkish",
    "우크라이나": "Ukrainian",
    "베트남": "Vietnamese",
    "일본": "Japanese",
}


# 1. 페이지 설정 (유지)
st.set_page_config(page_title="NoRegret Trip", page_icon="✈️", layout="wide")

st.title("✈️ NoRegret Trip")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #eef7ff;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] input,
    [data-testid="stSidebar"] [data-baseweb="textarea"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div {
        background-color: #f5fbff;
    }
    .cloud-chat-helper {
        position: fixed;
        right: 16px;
        bottom: 132px;
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
        right: 18px;
        bottom: -8px;
        width: 14px;
        height: 14px;
        background: #ffffff;
        border-right: 1px solid #d0d7de;
        border-bottom: 1px solid #d0d7de;
        transform: rotate(45deg);
    }
    [data-testid="stAppViewContainer"] h1 {
        font-weight: 700;
    }
    .st-key-cloud_chat_icon {
        position: fixed;
        right: 16px;
        bottom: 72px;
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
    .st-key-cloud_chat_popup {
        position: fixed;
        right: 24px;
        bottom: 136px;
        width: min(570px, calc(100vw - 40px));
        max-height: 85vh;
        overflow-y: auto;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.2);
        z-index: 999;
        padding: 14px;
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

if st.button("☁️", key="cloud_chat_icon"):
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


def extract_place_name(name_kr: str):
    """수식어가 포함된 도시 문자열에서 실제 지명만 추출합니다."""
    place = name_kr.strip()
    if "(" in place:
        place = place.split("(")[0].strip()
    if "," in place:
        place = place.split(",")[-1].strip()
    return place


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


def get_landmark_images(query: str, limit: int = 3):
    """대표 랜드마크 이미지를 최대 limit개 반환합니다."""
    images = []

    primary_image, _ = get_landmark_image(query)
    if primary_image:
        images.append(primary_image)

    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.images(
                    keywords=f"{query} landmark",
                    region="kr-kr",
                    safesearch="moderate",
                    size="Large",
                    max_results=max(limit * 2, 4),
                )
            )

        for item in results:
            image_url = item.get("image") or item.get("thumbnail") or item.get("url")
            if image_url and image_url not in images:
                images.append(image_url)
            if len(images) >= limit:
                break
    except Exception:
        pass

    return images[:limit]


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


@st.cache_data(ttl=3600)
def get_local_food_recommendations(destination_name: str, limit: int = 3):
    """TheMealDB로 목적지 국가의 추천 로컬 푸드(레시피/이미지)를 반환합니다."""
    country = extract_country_from_destination(destination_name)
    meal_area = THEMEALDB_AREA_BY_COUNTRY.get(country)

    if not meal_area:
        return []

    try:
        area_response = requests.get(
            "https://www.themealdb.com/api/json/v1/1/filter.php",
            params={"a": meal_area},
            timeout=8,
        )
        area_response.raise_for_status()
        meals = (area_response.json() or {}).get("meals") or []

        if not meals:
            return []

        recommendations = []
        for meal in meals[:limit]:
            meal_id = meal.get("idMeal")
            recipe = ""
            source_url = ""

            if meal_id:
                detail_response = requests.get(
                    "https://www.themealdb.com/api/json/v1/1/lookup.php",
                    params={"i": meal_id},
                    timeout=8,
                )
                detail_response.raise_for_status()
                detail = ((detail_response.json() or {}).get("meals") or [{}])[0]
                recipe = detail.get("strInstructions", "")
                source_url = detail.get("strSource") or detail.get("strYoutube") or ""

            recommendations.append(
                {
                    "name": meal.get("strMeal", "Unknown Meal"),
                    "image": meal.get("strMealThumb", ""),
                    "recipe": recipe,
                    "source": source_url,
                }
            )

        return recommendations
    except requests.RequestException:
        return []


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


def _resolve_travel_date_range(travel_dates):
    """여행 날짜 입력값을 시작일/종료일로 정규화합니다."""
    today = datetime.now().date()

    if not travel_dates:
        return today, today

    if isinstance(travel_dates, (list, tuple)) and len(travel_dates) == 2:
        start_date, end_date = travel_dates
    else:
        start_date = end_date = travel_dates

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    return start_date, end_date


def _get_trip_days_from_duration(duration_label: str) -> int:
    duration_days = {
        "1박 2일": 2,
        "2박 3일": 3,
        "3박 4일": 4,
        "4박 5일": 5,
        "일주일 (6박 7일)": 7,
        "일주일 이상 (장기/유럽/미주 가능)": 8,
    }
    return duration_days.get(duration_label, 2)


def build_flight_search_links(destination_name: str, airport_code: str, travel_dates):
    """Skyscanner 검색 링크를 반환합니다."""
    start_date, end_date = _resolve_travel_date_range(travel_dates)

    return {
        "skyscanner": (
            f"https://www.skyscanner.co.kr/transport/flights/sela/{airport_code.lower()}/"
            f"{start_date.strftime('%y%m%d')}/{end_date.strftime('%y%m%d')}/"
        ),
    }


def _strip_html_tags(raw_html: str):
    return re.sub(r"<[^>]+>", "", raw_html or "").strip()


def _extract_city_country(destination_name: str):
    city_name = destination_name.split("(")[0].strip()
    country_name = ""
    if "(" in destination_name and ")" in destination_name:
        country_name = destination_name.split("(")[-1].replace(")", "").strip()
    return city_name, country_name


def _build_teleport_queries(destination_name: str):
    city_name, country_name = _extract_city_country(destination_name)
    city_alias = CITY_NAME_ALIASES.get(city_name, city_name)
    country_alias = COUNTRY_NAME_ALIASES.get(country_name, country_name)

    candidates = [
        city_name,
        city_alias,
        f"{city_alias}, {country_alias}".strip(", "),
        f"{city_name}, {country_alias}".strip(", "),
    ]

    queries = []
    for query in candidates:
        cleaned = " ".join((query or "").split())
        if cleaned and cleaned.lower() not in [q.lower() for q in queries]:
            queries.append(cleaned)

    return city_name, queries


def _build_teleport_pros_cons(city_name: str, category_scores: dict, quality_score):
    """Teleport 점수를 바탕으로 여행자 관점의 장단점을 생성합니다."""
    category_labels = {
        "Safety": "치안",
        "Cost of Living": "생활비",
        "Housing": "숙소/주거비",
        "Healthcare": "의료 접근성",
        "Education": "교육/교양 인프라",
        "Environmental Quality": "환경 쾌적성",
        "Tolerance": "포용성",
        "Taxation": "세금/가격 구조",
        "Economy": "경제 활력",
        "Leisure & Culture": "여가/문화",
        "Commute": "이동/교통",
    }

    high_templates = {
        "Safety": "밤 시간에도 주요 관광지 이동 동선의 심리적 부담이 상대적으로 낮아요.",
        "Cost of Living": "식비·교통비 체감이 비교적 안정적이라 같은 예산으로 더 오래 머물기 좋아요.",
        "Housing": "숙소 선택 폭이 넓은 편이라 일정 스타일에 맞춘 숙소 전략을 세우기 유리해요.",
        "Healthcare": "여행 중 컨디션 이슈가 생겨도 의료 접근성 측면에서 상대적으로 안심할 수 있어요.",
        "Environmental Quality": "공기·도시 환경 체감이 쾌적해 도보 위주 일정의 피로도가 덜한 편이에요.",
        "Tolerance": "다양한 여행자에 익숙한 분위기라 혼행/커플/가족 모두 비교적 편하게 즐길 수 있어요.",
        "Economy": "도시 전반의 활력이 좋아 상점·서비스 운영 시간대와 선택지가 풍부한 편이에요.",
        "Leisure & Culture": "볼거리·즐길거리 밀도가 높아 짧은 일정에도 콘텐츠가 끊기지 않아요.",
        "Commute": "대중교통 기반 이동 효율이 좋아 렌터카 없이도 동선 짜기 수월해요.",
    }

    low_templates = {
        "Safety": "야간 외곽 이동이나 인적 드문 구간은 피하고, 귀가 동선은 미리 정해두는 게 좋아요.",
        "Cost of Living": "외식·카페·교통비가 빠르게 누적될 수 있어 일일 예산 상한선을 정해두면 좋아요.",
        "Housing": "성수기엔 숙소 가성비가 급격히 낮아질 수 있어 위치/가격 타협이 필요할 수 있어요.",
        "Healthcare": "여행자 보험을 넉넉히 준비하고 상비약을 챙기면 리스크를 줄일 수 있어요.",
        "Environmental Quality": "미세먼지·소음·혼잡 이슈가 있을 수 있어 일정 중 휴식 시간을 의도적으로 넣는 걸 추천해요.",
        "Tolerance": "지역별 문화 차이를 존중하는 복장/에티켓을 사전에 확인하면 훨씬 편하게 여행할 수 있어요.",
        "Taxation": "부가세·서비스 요금이 체감 물가를 높일 수 있어 결제 전 최종 금액 확인이 중요해요.",
        "Economy": "지역/시간대에 따라 서비스 편차가 있을 수 있어 예약형 동선을 선호하는 편이 안전해요.",
        "Leisure & Culture": "핵심 명소 외 선택지가 제한될 수 있어 사전 예약형 일정 구성이 특히 중요해요.",
        "Commute": "출퇴근 혼잡/환승 변수로 이동 시간이 늘어날 수 있어 하루 방문지 수를 욕심내지 않는 게 좋아요.",
    }

    valid_scores = [(name, score) for name, score in category_scores.items() if isinstance(score, (int, float))]
    if not valid_scores:
        return ["✅ 데이터가 제한적이지만, 일정/예산만 맞추면 충분히 만족도 높은 여행을 만들 수 있어요."], []

    top_categories = sorted(valid_scores, key=lambda item: item[1], reverse=True)[:3]
    bottom_categories = sorted(valid_scores, key=lambda item: item[1])[:2]

    pros = []
    for key, score in top_categories:
        if score >= 6.0:
            label = category_labels.get(key, key)
            insight = high_templates.get(key, "여행 만족도에 긍정적인 영향을 줄 가능성이 높아요.")
            pros.append(f"✅ **{city_name}**의 **{label}** 지표가 **{score:.1f}/10**으로 강점이에요. {insight}")

    if isinstance(quality_score, (int, float)) and quality_score >= 60:
        pros.append(f"✅ Teleport 종합 점수도 **{quality_score:.1f}/100**으로, 첫 방문자도 무난하게 즐길 가능성이 높아요.")

    if not pros:
        pros.append("✅ 핵심 지표가 전반적으로 평균권이라, 일정 난이도와 예산을 맞추면 안정적으로 즐길 수 있어요.")

    cons = []
    for key, score in bottom_categories:
        if score <= 5.5:
            label = category_labels.get(key, key)
            caution = low_templates.get(key, "여행 전에 관련 리스크를 미리 확인하면 좋아요.")
            cons.append(f"⚠️ **{city_name}**의 **{label}** 지표는 **{score:.1f}/10**으로 약점 구간이에요. {caution}")

    return pros, cons


@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def get_teleport_city_insights(destination_name: str):
    """Teleport API로 도시 생활 인사이트(생활비/안전/삶의 질/요약/사진)를 가져옵니다."""
    original_city_name, search_queries = _build_teleport_queries(destination_name)
    search_url = "https://api.teleport.org/api/cities/"

    try:
        urban_area_href = None
        resolved_city_name = original_city_name

        for query in search_queries:
            search_res = requests.get(search_url, params={"search": query, "limit": 5}, timeout=12)
            search_res.raise_for_status()
            search_data = search_res.json()
            city_results = search_data.get("_embedded", {}).get("city:search-results", [])

            for result in city_results:
                city_href = result.get("_links", {}).get("city:item", {}).get("href")
                if not city_href:
                    continue

                city_detail_res = requests.get(city_href, timeout=12)
                city_detail_res.raise_for_status()
                city_detail = city_detail_res.json()
                candidate_urban_area = city_detail.get("_links", {}).get("city:urban_area", {}).get("href")

                if candidate_urban_area:
                    urban_area_href = candidate_urban_area
                    resolved_city_name = city_detail.get("full_name", original_city_name).split(",")[0].strip()
                    break

            if urban_area_href:
                break

        if not urban_area_href:
            return None

        scores_res = requests.get(f"{urban_area_href}scores/", timeout=12)
        scores_res.raise_for_status()
        scores_data = scores_res.json()

        images_res = requests.get(f"{urban_area_href}images/", timeout=12)
        images_res.raise_for_status()
        images_data = images_res.json()

        categories = {
            item.get("name"): round(item.get("score_out_of_10", 0), 1)
            for item in scores_data.get("categories", [])
            if item.get("name")
        }

        summary = _strip_html_tags(scores_data.get("summary", "요약 정보가 없습니다."))
        image_url = images_data.get("photos", [{}])[0].get("image", {}).get("web")

        quality_score = scores_data.get("teleport_city_score")
        pros, cons = _build_teleport_pros_cons(resolved_city_name, categories, quality_score)

        category_rank = sorted(
            [(name, score) for name, score in categories.items() if isinstance(score, (int, float))],
            key=lambda item: item[1],
            reverse=True,
        )
        top_categories = category_rank[:3]
        bottom_categories = sorted(category_rank, key=lambda item: item[1])[:2]

        return {
            "city_name": resolved_city_name,
            "summary": summary,
            "quality_score": quality_score,
            "categories": categories,
            "top_categories": top_categories,
            "bottom_categories": bottom_categories,
            "image_url": image_url,
            "teleport_url": scores_data.get("teleport_city_url"),
            "source": urban_area_href,
            "pros": pros,
            "cons": cons,
        }
    except Exception:
        return None


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


def build_regret_summary(api_key: str, destination_name: str, reason_text: str, regret_risk_warnings, teleport_insight=None):
    """AI로 추천도 별점/한줄 요약을 생성하고, 실패 시 휴리스틱으로 보정합니다."""
    warning_count = len(regret_risk_warnings)
    quality_score = None
    if teleport_insight:
        quality_score = teleport_insight.get("quality_score")

    fallback_stars = max(1, min(5, 4 - max(0, warning_count - 1)))
    if quality_score is not None:
        if quality_score >= 70:
            fallback_stars += 1
        elif quality_score < 50:
            fallback_stars -= 1
        fallback_stars = max(1, min(5, fallback_stars))

    fallback_star_rating = "".join(["⭐" for _ in range(fallback_stars)] + ["☆" for _ in range(5 - fallback_stars)])
    fallback_one_liner = (
        regret_risk_warnings[0]
        if warning_count
        else "전반적으로 잘 맞는 여행지예요. 취향에 맞는 일정만 잘 짜면 만족도가 높을 가능성이 큽니다."
    )

    if not api_key:
        return fallback_star_rating, fallback_one_liner

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 여행지 추천 품질 평가자입니다. "
                        "입력 정보를 바탕으로 솔직하게 1~5점 별점을 매기고 한 줄 코멘트를 작성하세요. "
                        "점수 기준: 5 매우 추천, 4 추천, 3 보통, 2 아쉬움 큼, 1 비추천. "
                        "출력은 JSON으로만 반환: {\"stars\": int, \"one_liner\": string}."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "destination_name": destination_name,
                            "reason_text": reason_text,
                            "regret_risk_warnings": regret_risk_warnings,
                            "teleport_quality_score": quality_score,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        )
        ai_result = json.loads(response.choices[0].message.content)
        stars = int(ai_result.get("stars", fallback_stars))
        stars = max(1, min(5, stars))
        one_liner = str(ai_result.get("one_liner", fallback_one_liner)).strip() or fallback_one_liner
        star_rating = "".join(["⭐" for _ in range(stars)] + ["☆" for _ in range(5 - stars)])
        return star_rating, one_liner
    except Exception:
        return fallback_star_rating, fallback_one_liner


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


def _season_keyword_from_dates(travel_dates):
    """여행 날짜를 기준으로 검색용 계절 키워드를 계산합니다."""
    if not travel_dates:
        month = datetime.now().month
    else:
        month = travel_dates[0].month

    if month in (3, 4, 5):
        return "봄"
    if month in (6, 7, 8):
        return "여름"
    if month in (9, 10, 11):
        return "가을"
    return "겨울"


def get_local_seasonal_highlights(query: str, travel_dates):
    """대표 축제 외 지역 명절/계절 포인트/제철 음식 정보를 검색해 요약합니다."""
    current_year = datetime.now().year
    season_keyword = _season_keyword_from_dates(travel_dates)

    search_topics = [
        {
            "title": "🏮 대표 명절·지역 전통 행사",
            "keywords": f"{query} local holiday traditional event {current_year}",
            "fallback": "해당 기간의 지역 명절·전통 행사는 공식 관광청/지자체 일정에서 확인해 주세요.",
        },
        {
            "title": f"❄️🌸 계절 포인트 ({season_keyword})",
            "keywords": f"{query} {season_keyword} seasonal highlights nature scenery",
            "fallback": "계절별 자연/풍경 포인트 정보는 관광청 계절 가이드에서 최신 상태를 확인해 주세요.",
        },
        {
            "title": f"🍽️ {season_keyword} 제철 음식",
            "keywords": f"{query} {season_keyword} seasonal food local cuisine",
            "fallback": "제철 음식은 현지 시장·식당의 계절 메뉴 기준으로 변동될 수 있어요.",
        },
    ]

    sections = []
    try:
        with DDGS() as ddgs:
            for topic in search_topics:
                items = list(
                    ddgs.text(
                        keywords=topic["keywords"],
                        region="kr-kr",
                        safesearch="moderate",
                        max_results=2,
                    )
                )

                section_lines = [f"#### {topic['title']}"]
                if items:
                    top_item = items[0]
                    title = top_item.get("title", "관련 정보")
                    snippet = top_item.get("body", "자세한 내용은 링크에서 확인해 주세요.")
                    section_lines.append(f"- **{title}**: {snippet}")
                else:
                    section_lines.append(f"- {topic['fallback']}")

                sections.append("\n".join(section_lines))

        if not sections:
            return "검색 결과를 찾지 못했어요. 잠시 후 다시 시도해 주세요."

        return "\n\n".join(sections)
    except Exception as exc:
        return f"지역 시즌 정보를 가져오지 못했어요: {exc}"


def get_destination_bgm(name_kr: str):
    """여행지 분위기/지역성을 반영한 유튜브 BGM 플레이리스트를 반환합니다."""
    city = extract_place_name(name_kr)
    country = extract_country_from_destination(name_kr)

    city_bgm_map = {
        "파리": [
            ("파리 재즈 카페 & 샹송 무드", "https://www.youtube.com/watch?v=cTLTG4FTNBQ"),
            ("프렌치 카페 아코디언 무드", "https://www.youtube.com/watch?v=DX9xA7gQ8V8"),
        ],
        "도쿄": [
            ("도쿄 시티팝 드라이브", "https://www.youtube.com/watch?v=3bNITQR4Uso"),
            ("도쿄 나이트 시티 재즈", "https://www.youtube.com/watch?v=neV3EPgvZ3g"),
        ],
        "오사카": [
            ("오사카 네온 스트리트 시티팝", "https://www.youtube.com/watch?v=3bNITQR4Uso"),
            ("일본 야경 감성 로파이", "https://www.youtube.com/watch?v=5yx6BWlEVcY"),
        ],
        "교토": [
            ("교토 전통 악기 힐링 무드", "https://www.youtube.com/watch?v=4zG7WcW2nQ4"),
            ("일본 전통 선율 명상 무드", "https://www.youtube.com/watch?v=H6M0EulApMM"),
        ],
        "치앙마이": [
            ("치앙마이 카페 감성 로파이", "https://www.youtube.com/watch?v=5qap5aO4i9A"),
            ("트로피컬 카페 칠 무드", "https://www.youtube.com/watch?v=rUxyKA_-grg"),
        ],
        "방콕": [
            ("방콕 루프탑 나이트 무드", "https://www.youtube.com/watch?v=JfVOs4VSpmA"),
            ("태국 야시장 감성 비트", "https://www.youtube.com/watch?v=M5QY2_8704o"),
        ],
        "다낭": [
            ("다낭 해변 선셋 칠 음악", "https://www.youtube.com/watch?v=DWcJFNfaw9c"),
            ("비치 선셋 칠아웃 라운지", "https://www.youtube.com/watch?v=7NOSDKb0HlU"),
        ],
        "하노이": [
            ("하노이 올드쿼터 베트남 감성", "https://www.youtube.com/watch?v=uaf4iR5Vw9s"),
            ("베트남 카페 어쿠스틱 무드", "https://www.youtube.com/watch?v=qaK4C8f8QeY"),
        ],
        "뉴올리언스": [
            ("뉴올리언스 스트리트 재즈", "https://www.youtube.com/watch?v=Dx5qFachd3A"),
            ("스윙 재즈 클럽 라이브", "https://www.youtube.com/watch?v=HMnrl0tmd3k"),
        ],
        "리스본": [
            ("리스본 파두(Fado) 감성", "https://www.youtube.com/watch?v=QhBwrn7fG9k"),
            ("포르투갈 기타 나이트 무드", "https://www.youtube.com/watch?v=EJeM7Q2q5Hw"),
        ],
        "세비야": [
            ("세비야 플라멩코 무드", "https://www.youtube.com/watch?v=t4H_Zoh7G5A"),
            ("스페인 기타 & 플라멩코 라이브", "https://www.youtube.com/watch?v=6jS8k6JwB-A"),
        ],
        "이비사": [
            ("이비사 비치 하우스 뮤직", "https://www.youtube.com/watch?v=1bJY4wF2J3A"),
            ("비치 클럽 칠 하우스", "https://www.youtube.com/watch?v=Q6MemVxEquE"),
        ],
        "두바이": [
            ("사막 드라이브 아라비안 라운지", "https://www.youtube.com/watch?v=4jP06Wk6M4Q"),
            ("미들 이스트 라운지 무드", "https://www.youtube.com/watch?v=tTL3kGxbl9M"),
        ],
        "카이로": [
            ("카이로 아라빅 오리엔탈 무드", "https://www.youtube.com/watch?v=_O6fQkS3SIA"),
            ("오리엔탈 전통 퍼커션 무드", "https://www.youtube.com/watch?v=owtDZFilZ6A"),
        ],
        "울란바토르": [
            ("몽골 초원 & 호미(Hoomei) 무드", "https://www.youtube.com/watch?v=9e9v4M9RjvY"),
            ("몽골 전통 현악/목가적 무드", "https://www.youtube.com/watch?v=p_5yt5IX38I"),
        ],
    }

    country_bgm_map = {
        "일본": [
            ("일본 여행 무드 시티팝/재즈", "https://www.youtube.com/watch?v=3bNITQR4Uso"),
            ("일본 로파이/재즈 플레이리스트", "https://www.youtube.com/watch?v=neV3EPgvZ3g"),
        ],
        "중국": [
            ("중국 전통 악기 + 현대 퓨전 무드", "https://www.youtube.com/watch?v=9U8kbM_BhWc"),
            ("중국 고전 선율 힐링 플레이리스트", "https://www.youtube.com/watch?v=Mh0x8mH5vPM"),
        ],
        "대만": [
            ("대만 야시장 감성 인디팝", "https://www.youtube.com/watch?v=qM4vYf6A5LQ"),
            ("대만 카페 감성 로파이", "https://www.youtube.com/watch?v=5qap5aO4i9A"),
        ],
        "홍콩": [
            ("홍콩 야경 시네마틱 무드", "https://www.youtube.com/watch?v=AD8G7f8J6Vg"),
            ("네온 시티 신스웨이브 무드", "https://www.youtube.com/watch?v=MVPTGNGiI-4"),
        ],
        "베트남": [
            ("베트남 로컬 감성 어쿠스틱", "https://www.youtube.com/watch?v=uaf4iR5Vw9s"),
            ("동남아 트래블 칠 플레이리스트", "https://www.youtube.com/watch?v=DWcJFNfaw9c"),
        ],
        "태국": [
            ("태국 트로피컬 칠 & 로컬 무드", "https://www.youtube.com/watch?v=JfVOs4VSpmA"),
            ("트로피컬 하우스 여행 무드", "https://www.youtube.com/watch?v=7NOSDKb0HlU"),
        ],
        "싱가포르": [
            ("싱가포르 마리나 베이 라운지", "https://www.youtube.com/watch?v=6zXDo4dL7SU"),
            ("어반 라운지/칠아웃 플레이리스트", "https://www.youtube.com/watch?v=qGaOlfmX8rQ"),
        ],
        "미국": [
            ("미국 로드트립 클래식 플레이리스트", "https://www.youtube.com/watch?v=gEPmA3USJdI"),
            ("로드트립 인디/포크 무드", "https://www.youtube.com/watch?v=V1Pl8CzNzCw"),
        ],
        "영국": [
            ("런던 브릿팝 & 인디 감성", "https://www.youtube.com/watch?v=VbfpW0pbvaU"),
            ("UK 인디 감성 플레이리스트", "https://www.youtube.com/watch?v=lTRiuFIWV54"),
        ],
        "프랑스": [
            ("프랑스 샹송 & 파리지앵 재즈", "https://www.youtube.com/watch?v=cTLTG4FTNBQ"),
            ("프렌치 카페 무드 재즈", "https://www.youtube.com/watch?v=DX9xA7gQ8V8"),
        ],
        "스페인": [
            ("스페인 플라멩코 & 기타 무드", "https://www.youtube.com/watch?v=t4H_Zoh7G5A"),
            ("스페인 기타 칠 무드", "https://www.youtube.com/watch?v=6jS8k6JwB-A"),
        ],
        "포르투갈": [
            ("포르투갈 파두(Fado) 감성", "https://www.youtube.com/watch?v=QhBwrn7fG9k"),
            ("파두 기타 라이브 감성", "https://www.youtube.com/watch?v=EJeM7Q2q5Hw"),
        ],
        "튀르키예": [
            ("이스탄불 보스포루스 오리엔탈 무드", "https://www.youtube.com/watch?v=T4k_qws0k4E"),
            ("터키 전통 & 현대 퓨전 무드", "https://www.youtube.com/watch?v=9fM2v1Vh4hk"),
        ],
        "아랍에미리트": [
            ("중동 라운지 & 아라비안 나이트", "https://www.youtube.com/watch?v=4jP06Wk6M4Q"),
            ("아라비안 라운지 칠아웃", "https://www.youtube.com/watch?v=tTL3kGxbl9M"),
        ],
        "이집트": [
            ("이집트 전통 리듬 & 오리엔탈 무드", "https://www.youtube.com/watch?v=_O6fQkS3SIA"),
            ("오리엔탈 클래식 인스트루멘탈", "https://www.youtube.com/watch?v=owtDZFilZ6A"),
        ],
        "몽골": [
            ("몽골 전통/초원 무드 사운드", "https://www.youtube.com/watch?v=9e9v4M9RjvY"),
            ("몽골 민속 선율 플레이리스트", "https://www.youtube.com/watch?v=p_5yt5IX38I"),
        ],
    }

    fallback_candidates = [
        ("잔잔한 여행 로파이 라이브", "https://www.youtube.com/watch?v=jfKfPfyJRdk"),
        ("여행 브이로그용 감성 BGM 모음", "https://www.youtube.com/watch?v=DWcJFNfaw9c"),
        ("트래블 칠아웃 플레이리스트", "https://www.youtube.com/watch?v=7NOSDKb0HlU"),
        ("카페 로파이 집중 음악", "https://www.youtube.com/watch?v=5qap5aO4i9A"),
    ]

    for keyword, bgm_candidates in city_bgm_map.items():
        if keyword in city:
            return pick_available_bgm([*bgm_candidates, *fallback_candidates], f"{city} travel bgm playlist")

    for keyword, bgm_candidates in country_bgm_map.items():
        if keyword in country:
            return pick_available_bgm([*bgm_candidates, *fallback_candidates], f"{country} travel bgm playlist")

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
        if len(warnings) >= 2:
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

    if country in {"한국", "South Korea", "Korea", "Republic of Korea"}:
        country = "대한민국"

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
            <div style="display:flex; align-items:center; gap:6px; font-size:14px; font-weight:600; color:#333;">
                <span>공유 메세지</span>
            <button id="kakao-copy-btn"
                style="
                    background:transparent;
                    color:#333;
                    border:1px solid #d9d9d9;
                    border-radius:6px;
                    width:30px;
                    height:30px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:16px;
                    cursor:pointer;
                ">
                📋
            </button>
            </div>
            <p id="kakao-copy-status" style="margin-top:6px; font-size:13px;"></p>
        </div>
        <script>
            const button = document.getElementById("kakao-copy-btn");
            const status = document.getElementById("kakao-copy-status");
            const textToCopy = {safe_text};

            button.addEventListener("click", async () => {{
                try {{
                    await navigator.clipboard.writeText(textToCopy);
                    status.textContent = "복사 완료!";
                }} catch (error) {{
                    status.textContent = "자동 복사 실패: 아래 텍스트를 수동 복사해 주세요.";
                }}
            }});
        </script>
        """,
        height=78,
    )


# 2. 사이드바 (유지)
with st.sidebar:
    st.subheader("여행 가자 ^~^")
    st.markdown("---")
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    weather_api_key = st.text_input("OpenWeather API Key를 입력하세요", type="password")
    st.markdown("---")
    st.write("💡 **팁**")
    st.write("- **'일주일 이상'**을 선택해야 유럽/미주 등 장거리 추천이 나옵니다.")
    st.write("- **'모험가'**를 선택하면 더 이색적인 곳이 나옵니다.")
    st.write("- 오른쪽 아래 **☁️ 버튼**을 누르면 재추천/일정 상담 챗봇이 열립니다.")

    st.markdown("---")
    st.markdown("### 🌐 외부 정보 연동")
    st.caption("대표 이미지는 Unsplash(보조: DuckDuckGo/Wikipedia), 검색 기반 요약은 DuckDuckGo, 날씨는 OpenWeather API를 사용합니다.")

# 3. 메인 화면 입력 (유지)
st.markdown("#### 여행 스타일을 골라주세요")

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
trip_days = _get_trip_days_from_duration(duration)
st.session_state["trip_days"] = trip_days


def _sync_travel_date_range():
    selected_range = st.session_state.get("travel_date_range")

    if isinstance(selected_range, (list, tuple)) and len(selected_range) >= 1:
        departure = selected_range[0]
    else:
        departure = selected_range or today

    if departure < today:
        departure = today

    arrival = departure + timedelta(days=st.session_state["trip_days"] - 1)
    st.session_state["departure_date"] = departure
    st.session_state["travel_date_range"] = (departure, arrival)


if "departure_date" not in st.session_state:
    st.session_state["departure_date"] = today

if st.session_state["departure_date"] < today:
    st.session_state["departure_date"] = today

arrival_date = st.session_state["departure_date"] + timedelta(days=trip_days - 1)
auto_range = (st.session_state["departure_date"], arrival_date)

if st.session_state.get("travel_date_range") != auto_range:
    st.session_state["travel_date_range"] = auto_range

travel_dates = st.date_input(
    "여행 날짜",
    value=st.session_state["travel_date_range"],
    min_value=today,
    help="출발일을 클릭하면 여행 기간에 맞춰 도착일이 자동 선택됩니다.",
    key="travel_date_range",
    on_change=_sync_travel_date_range,
)

if isinstance(travel_dates, (list, tuple)) and len(travel_dates) == 2:
    departure_date, arrival_date = travel_dates
else:
    departure_date = travel_dates
    arrival_date = departure_date + timedelta(days=trip_days - 1)

travel_dates = (departure_date, arrival_date)

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

                tabs = st.tabs([extract_place_name(d['name_kr']) for d in destinations])

                for i, tab in enumerate(tabs):
                    with tab:
                        dest = destinations[i]
                        st.header(f"📍 {dest['name_kr']}")

                        map_data = pd.DataFrame({'lat': [dest['latitude']], 'lon': [dest['longitude']]})
                        st.map(map_data, zoom=4)

                        landmark_images = get_landmark_images(dest['name_kr'], limit=3)
                        teleport_insight = get_teleport_city_insights(dest['name_kr'])

                        if landmark_images:
                            st.markdown("#### 🖼️ 여행지 대표 이미지")
                            image_cols = st.columns(3, gap="small")
                            for idx, image_url in enumerate(landmark_images[:3]):
                                with image_cols[idx]:
                                    st.image(
                                        image_url,
                                        caption=f"{extract_place_name(dest['name_kr'])} 대표 이미지 {idx + 1}",
                                        use_container_width=True,
                                    )

                        st.info(f"💡 **추천 이유**: {dest['reason']}")

                        if teleport_insight:
                            with st.expander("🛰️ Teleport 도시 인사이트", expanded=False):
                                if teleport_insight.get("summary"):
                                    st.markdown(f"**도시 한줄 요약**: {teleport_insight['summary']}")

                                top_categories = teleport_insight.get("top_categories", [])
                                bottom_categories = teleport_insight.get("bottom_categories", [])
                                if top_categories or bottom_categories:
                                    category_rows = []
                                    for category_name, score in top_categories:
                                        category_rows.append({"구분": "강점", "지표": category_name, "점수(0~10)": score})
                                    for category_name, score in bottom_categories:
                                        category_rows.append({"구분": "유의", "지표": category_name, "점수(0~10)": score})
                                    st.dataframe(pd.DataFrame(category_rows), hide_index=True, use_container_width=True)

                                if teleport_insight.get("teleport_url"):
                                    st.link_button("🔗 Teleport 도시 프로필 보기", teleport_insight["teleport_url"])

                        regret_risk_warnings = get_regret_risk_warnings(style, dest['name_kr'], dest['reason'])
                        weather_summary = get_weather_summary(dest['latitude'], dest['longitude'], weather_api_key)
                        seasonal_note = get_seasonal_travel_note(dest['name_kr'], dest['latitude'], travel_dates)
                        seasonal_highlights = get_local_seasonal_highlights(dest['name_kr'], travel_dates)
                        country, entry_info, is_search_based = get_entry_requirement_for_korean_passport(dest['name_kr'])

                        regret_ratings, regret_one_liner = build_regret_summary(
                            api_key,
                            dest['name_kr'],
                            dest['reason'],
                            regret_risk_warnings,
                            teleport_insight,
                        )
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

                            st.markdown("<div style='font-size: 0.95rem; font-weight: 500; margin: 0.25rem 0 0.5rem;'>🌟 그래도 좋은 점</div>", unsafe_allow_html=True)
                            if teleport_insight:
                                for pro_text in teleport_insight.get("pros", []):
                                    st.success(pro_text)
                            else:
                                st.success("✅ 단점이 있더라도 일정 난이도·예산만 맞추면 충분히 만족도 높은 여행이 될 수 있어요.")

                            if teleport_insight and teleport_insight.get("cons"):
                                st.markdown("#### ⚠️ Teleport 기반 단점/주의점")
                                for con_text in teleport_insight.get("cons", []):
                                    st.warning(con_text)

                        with st.expander("🌤️ 날씨 자세히", expanded=False):
                            st.write(weather_summary)
                            st.markdown("#### 🌦️ 여행 기간 기후/시기 적합성")
                            st.markdown(seasonal_note)

                        flight_links = build_flight_search_links(dest['name_kr'], dest['airport_code'], travel_dates)

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

                        with st.expander("🧭 지역 시즌 하이라이트", expanded=False):
                            st.markdown(seasonal_highlights)

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

                                local_foods = get_local_food_recommendations(dest['name_kr'])
                                if local_foods:
                                    st.markdown("#### 🍽️ 추천 음식 / 로컬 푸드")
                                    meal_cols = st.columns(min(3, len(local_foods)))
                                    for idx, meal in enumerate(local_foods[:3]):
                                        with meal_cols[idx]:
                                            st.markdown(f"**{meal['name']}**")
                                            if meal.get("image"):
                                                st.image(meal["image"], width=160)

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
                        st.link_button(f"✈️ {extract_place_name(dest['name_kr'])} 항공권 검색", flight_links["skyscanner"])

                st.markdown("---")
                st.markdown("#### 🗳️ 친구들에게 투표받기")
                share_options = [f"{idx + 1}. {d['name_kr']}" for idx, d in enumerate(destinations[:3])]
                share_text = (
                    "나 이번에 여행 가는데 어디가 좋을까? "
                    + " ".join(share_options)
                    + " 투표 좀!"
                )
                render_kakao_share_copy_button(share_text)
                st.text_area("공유 텍스트 미리보기", value=share_text, height=72)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")


if st.session_state.chat_open:
    chat_container = st.container(border=True, key="cloud_chat_popup")
    with chat_container:
        st.markdown("### ☁️ 재추천 챗봇")
        st.caption("재추천은 물론, 마음에 드는 여행지의 일정·관광지도 원하는 스타일에 맞춰 추천해 드려요.")
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_feedback = st.text_input(
            "메시지 입력",
            key="cloud_chat_input",
            label_visibility="collapsed",
            placeholder="예: 재추천해줘 / 오사카 3박4일 일정 짜줘 / 비 오는 날 갈만한 관광지 추천해줘",
        )
        send_clicked = st.button("전송", key="cloud_chat_send")

    if send_clicked and user_feedback.strip():
        user_feedback = user_feedback.strip()
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
        st.session_state.cloud_chat_input = ""
        st.rerun()
