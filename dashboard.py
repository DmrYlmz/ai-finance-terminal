import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from translations import UI_TEXT


st.set_page_config(page_title="AI Finans Terminali", layout="wide", initial_sidebar_state="expanded")


lang = st.sidebar.selectbox("Language / Dil / Sprache", ["TR", "EN", "DE"])
t = UI_TEXT[lang] 


st.sidebar.title(t["sidebar_mode"])
st.sidebar.markdown(t["sidebar_select"])
app_mode = st.sidebar.radio("", [t["single_title"], t["multi_title"]]) 

st.sidebar.markdown("---")
st.sidebar.info("FastAPI sunucusunun (uvicorn main:app --reload) arka planda çalıştığından emin olun.")


if app_mode == t["single_title"]:
    st.title(t["single_title"])
    st.markdown(t["single_desc"])
    
    c1, c2, c3 = st.columns(3)
    with c1:
        single_symbol = st.text_input(t["symbol_label"], value="RHM.DE").upper()
    with c2:
        single_horizon = st.selectbox(t["horizon_label"], t["horizon_options"], index=1)
    with c3:
        single_entry = st.number_input(t["entry_label"], value=0.0, step=0.1)
    if st.button(t["start_btn"], type="primary", use_container_width=True):
        with st.spinner(f"{single_symbol} için LangGraph ajanları çalışıyor..."):
            api_url = "http://127.0.0.1:8000/analyze"
            payload = {
                "symbol": single_symbol,
                "entry_price": single_entry if single_entry > 0 else None,
                "investment_horizon": single_horizon,
                "language" : lang
            }
            
            try:
                response = requests.post(api_url, json=payload)
                
                
                if response.status_code != 200:
                    st.error(f"🚨 Arka Plan (FastAPI) Çöktü! Hata Kodu: {response.status_code}")
                    st.code(response.text)
                else:
                    data = response.json()
                    
                    if data.get("error"):
                        st.error(data["error"])
                    else:
                        col_chart, col_metrics = st.columns([2, 1])
                        with col_chart:
                            st.subheader(f"{single_symbol} {t['graph_title']}") 
                            hist = yf.Ticker(single_symbol).history(period="6mo")
                            if not hist.empty:
                                fig = go.Figure(data=[go.Candlestick(
                                    x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']
                                )])
                                fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=400, xaxis_rangeslider_visible=False, template="plotly_dark")
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col_metrics:
                            st.subheader(t["agent_metrics"]) 
                            m1, m2 = st.columns(2)
                            m1.metric(t["current_price"], f"{data.get('current_price', 'N/A')}")
                            m2.metric("RSI (14)", data.get("rsi", "N/A"))
                            st.metric(t["market_sentiment"], data.get("sentiment", "N/A"))
                            st.caption(f"{t['selected_horizon']}: {single_horizon}")
                            
                            st.markdown(f"### {t['strategy_title']}")
                            st.info(data.get("strategy", "Strateji üretilemedi."))
                            
            except requests.exceptions.ConnectionError:
                st.error("API'ye bağlanılamadı. FastAPI çalışıyor mu?")


elif app_mode == t["multi_title"]:
    st.title("📈 Portföy Analizi (Map-Reduce)")
    st.markdown("Listenize birden fazla varlık ekleyin ve LangGraph ajanlarının paralel analizini başlatın.")

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []

    st.subheader("1. Portföye Varlık Ekle")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        new_symbol = st.text_input("Sembol:").upper()
    with c2:
        new_horizon = st.selectbox("Vade:", ["KISA", "ORTA", "UZUN"], key="multi_horizon")
    with c3:
        new_entry = st.number_input("Alış Fiyatınız:", value=0.0, step=0.1, key="multi_entry")
    with c4:
        st.write("")
        st.write("")
        if st.button("➕ Ekle", use_container_width=True):
            if new_symbol:
                st.session_state.portfolio.append({
                    "symbol": new_symbol,
                    "entry_price": new_entry if new_entry > 0 else None,
                    "investment_horizon": new_horizon
                })
                st.success(f"{new_symbol} eklendi!")
                st.rerun()

    if st.session_state.portfolio:
        st.markdown("---")
        df = pd.DataFrame(st.session_state.portfolio)
        st.dataframe(df, use_container_width=True)

        if st.button("🚀 Tüm Portföyü Analiz Et", type="primary", use_container_width=True):
            with st.spinner("Ajanlar paralel çalışıyor..."):
                api_url = "http://127.0.0.1:8000/analyze_portfolio"
                payload = {"assets": st.session_state.portfolio}

                try:
                    response = requests.post(api_url, json=payload)
                    
                    
                    if response.status_code != 200:
                        st.error(f"🚨 Arka Plan (FastAPI) Çöktü! Hata Kodu: {response.status_code}")
                        st.code(response.text)
                    else:
                        data = response.json()

                        if "detail" in data:
                            st.error(data["detail"])
                        else:
                            st.markdown("---")
                            st.header("🎯 Portföy Yöneticisi Genel Değerlendirmesi")
                            st.success(data.get("portfolio_summary", "Özet alınamadı."))

                            st.markdown("---")
                            st.header("🔍 Bireysel Varlık Analizleri")
                            individual_results = data.get("individual_results", [])
                            if individual_results:
                                symbols = [res["symbol"] for res in individual_results]
                                tabs = st.tabs(symbols)
                                
                                for i, tab in enumerate(tabs):
                                    res = individual_results[i]
                                    with tab:
                                        st.write(f"**Anlık Fiyat:** {res.get('current_price')} | **RSI:** {res.get('rsi')} | **Duyarlılık:** {res.get('sentiment')}")
                                        st.info(res.get("strategy", "Strateji üretilemedi."))
                                        
                except requests.exceptions.ConnectionError:
                    st.error("API'ye bağlanılamadı. FastAPI çalışıyor mu?")

        if st.button("🗑️ Portföyü Temizle"):
            st.session_state.portfolio = []
            st.rerun()


