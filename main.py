import streamlit as st
st.title('나의 먹잘알 서비스 만들기^^')
a=st.text_input('이름을 입력해라')
b=st.selectbox('왓츠유얼페이보릿푸드',['한정선','오돌뼈','석류'])
if st.button('인사말 생성'):
  st.write('반갑습니다')
  st.info(a+'님 안녕하세연')
  st.warning(b+'와 ㄹㅈㄷ 먹잘알')
  st.error('우리 같이 푸파해요~')
  st.balloons()
