import streamlit as st
import yfinance as yf
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime

# --- 웹페이지 설정 ---
st.set_page_config(page_title="ETF 분석기", page_icon="📈")

# 제목 및 설명
st.title("📈 ETF 수익률 & 추세 분석기")
st.markdown("원하는 **ETF 티커**를 입력하면 수익률과 이동평균선을 분석해드립니다.")

# 사이드바 (입력창)
with st.sidebar:
    st.header("🔍 검색 설정")
    ticker = st.text_input("티커 입력 (예: QQQ, SPY)", value="QQQ").upper().strip()
    run_btn = st.button("분석 시작")

# --- 분석 로직 ---
if run_btn:
    if not ticker:
        st.warning("티커를 입력해주세요.")
    else:
        try:
            with st.spinner(f"'{ticker}' 데이터 불러오는 중..."):
                # 데이터 가져오기 (2년치)
                stock = yf.Ticker(ticker)
                df = stock.history(period="2y")

                if df.empty:
                    st.error("데이터를 찾을 수 없습니다. 티커를 확인해주세요.")
                else:
                    # 데이터 처리
                    price = df['Close']
                    latest_price = price.iloc[-1]
                    latest_date = price.index[-1].strftime('%Y-%m-%d')

                    # 1. 요약 정보 출력
                    st.success(f"**{ticker}** 분석 완료! (기준일: {latest_date})")
                    st.metric(label="현재 주가", value=f"${latest_price:,.2f}")

                    # 2. 화면 분할 (왼쪽: 수익률, 오른쪽: 이평선)
                    col1, col2 = st.columns(2)

                    # === [왼쪽] 기간별 수익률 ===
                    with col1:
                        st.subheader("📅 기간별 수익률")
                        returns_data = []
                        
                        for i in range(1, 13):
                            target_date = price.index[-1] - relativedelta(months=i)
                            # 과거 데이터 찾기 (truncate)
                            past_data = price.truncate(after=target_date)
                            
                            if not past_data.empty:
                                past_price = past_data.iloc[-1]
                                days_diff = (target_date - past_data.index[-1]).days
                                
                                if days_diff <= 15:
                                    ret = (latest_price / past_price) - 1
                                    emoji = "🔥" if ret > 0 else "💧"
                                    returns_data.append({
                                        "기간": f"{i}개월 전",
                                        "수익률": f"{ret*100:+.2f}%",
                                        "상태": emoji
                                    })
                        
                        # 표로 보여주기
                        st.dataframe(pd.DataFrame(returns_data), hide_index=True, use_container_width=True)

                    # === [오른쪽] 이동평균선 ===
                    with col2:
                        st.subheader("📈 이동평균선 추세")
                        ma_days = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
                        ma_data = []

                        for days in ma_days:
                            if len(price) >= days:
                                ma_val = price.tail(days).mean()
                                is_up = latest_price >= ma_val
                                status = "상승 (정배열) 🔴" if is_up else "하락 (역배열) 🔵"
                                
                                ma_data.append({
                                    "이평선": f"{days}일선",
                                    "가격": f"${ma_val:,.2f}",
                                    "추세": status
                                })
                        
                        st.dataframe(pd.DataFrame(ma_data), hide_index=True, use_container_width=True)
                    
                    # 3. 차트 그리기 (보너스 기능)
                    st.subheader("📊 최근 1년 주가 차트")
                    st.line_chart(price.tail(252))

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
