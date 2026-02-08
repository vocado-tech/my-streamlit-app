import requests
import streamlit as st

st.title("💬 명언 API 테스트")

if st.button("결과 보기"):
    response = requests.get("https://zenquotes.io/api/random")
    data = response.json()

    st.success("오늘의 명언")
    st.write(f"\"{data[0]['q']}\"")
    st.write(f"- {data[0]['a']}")
