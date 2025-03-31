import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime
import re

# 분석 기준 정의
categories = {
    "채택: 선정 기준/평가": ["평가표", "기준", "추천의견서", "선정기준"],
    "채택: 위원회 운영": ["위원회", "협의회", "대표교사", "위원"],
    "채택: 회의/심의 진행": ["회의", "회의록", "심의", "심사", "운영"],
    "배송": ["배송"],
    "배송: 지도서/전시본 도착": ["도착", "왔어요", "전시본", "지도서", "박스"],
    "배송: 라벨/정리 업무": ["라벨", "분류", "정리", "전시 준비"],
    "주문: 시스템 사용": ["나이스", "에듀파인", "등록", "입력"],
    "주문: 공문/정산": ["공문", "정산", "마감일", "요청"],
    "출판사: 자료 수령/이벤트": ["보조자료", "자료", "기프티콘", "이벤트"],
    "출판사: 자료 회수/요청": ["회수", "요청", "교사용"]
}

publishers = ["미래엔", "비상", "동아", "아이스크림", "천재", "좋은책", "지학사", "대교", "이룸", "명진", "천재교육"]
subjects = ["국어", "수학", "사회", "과학", "영어", "도덕", "음악", "미술", "체육"]
complaint_keywords = ["안 왔어요", "아직", "늦게", "없어요", "오류", "문제", "왜", "헷갈려", "불편", "안옴", "지연", "안보여요", "못 받았", "힘들어요"]

# 분류 함수
def classify_category(text):
    if "배송" in text:
        return "배송"
    for category, keywords in categories.items():
        if any(k in text for k in keywords):
            return category
    return "기타"

def extract_publisher(text):
    for pub in publishers:
        if pub in text:
            return pub
    return None

def extract_subject(text):
    for subject in subjects:
        if subject in text:
            return subject
    return None

def detect_complaint(text):
    return any(k in text for k in complaint_keywords)

# Streamlit 앱 시작
st.title("📊 카카오톡 교과서 단톡방 분석기")
uploaded_file = st.file_uploader("카카오톡 .txt 파일을 업로드하세요")

if uploaded_file:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    text = stringio.read()

    pattern = re.compile(r"(\d{4}년 \d{1,2}월 \d{1,2}일 (오전|오후) \d{1,2}:\d{2}), (.+?) : (.+)")
    matches = pattern.findall(text)

    rows = []
    for date_str, ampm, sender, message in matches:
        if sender == "오픈채팅봇":
            continue
        try:
            dt = datetime.strptime(date_str.replace("오전", "AM").replace("오후", "PM"), "%Y년 %m월 %d일 %p %I:%M")
            rows.append({
                "날짜": dt.date(),
                "시간": dt.time(),
                "보낸 사람": sender.strip(),
                "메시지": message.strip(),
                "카테고리": classify_category(message),
                "출판사": extract_publisher(message),
                "과목": extract_subject(message),
                "불만 여부": detect_complaint(message)
            })
        except Exception:
            continue

    df = pd.DataFrame(rows)

    st.success("✅ 대화 분석이 완료되었습니다!")
    st.dataframe(df.head(20))

    st.download_button(
        "📥 전체 메시지 엑셀 다운로드",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="카카오톡_분석_결과.csv",
        mime="text/csv"
    )
