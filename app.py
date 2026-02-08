import streamlit as st
import requests

st.title("💬 나의 명언 제조기")

# "결과 보기" 버튼 생성
if st.button("결과 보기 (오늘의 명언)"):
    
    # 1. ZenQuotes API에서 데이터 가져오기
    try:
        response = requests.get("https://zenquotes.io/api/random")
        response.raise_for_status()  # 혹시 에러가 나면 알려줌
        data = response.json()

        # 2. 명언과 저자 분리하기
        quote = data[0]['q']   # 명언 내용
        author = data[0]['a']  # 저자 이름

        # 3. 화면에 예쁘게 보여주기
        st.success("오늘의 명언이 도착했습니다! 💌")
        st.markdown(f"### *\"{quote}\"*")
        st.markdown(f"**- {author} -**")

    except Exception as e:
        st.error(f"에러가 발생했습니다: {e}")
