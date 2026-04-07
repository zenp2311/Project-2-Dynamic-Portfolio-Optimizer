import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go
from pypfopt import expected_returns, risk_models, EfficientFrontier

@st.cache_data
def load_data(tickers, years=3):
    start_date = datetime.now() - timedelta(days=years*365)
    end_date = datetime.now()
    
    # Download data
    raw_data = yf.download(tickers, start=start_date, end=end_date)
    
    # Extract 'Close' prices (handles recent yfinance multi-index changes)
    if isinstance(raw_data.columns, pd.MultiIndex):
        data = raw_data['Close']
    else:
        # For a single ticker it might not be a MultiIndex
        data = raw_data['Close']
        
    # Ensure it's a DataFrame in case a single ticker is passed
    if isinstance(data, pd.Series):
        data = data.to_frame(name=tickers[0])
        
    # Clean data: Forward fill to handle random missing days, then drop any rows that still have NAs 
    clean_data = data.ffill().dropna()
    
    return clean_data

st.set_page_config(page_title="Portfolio Optimizer", layout="wide")

st.title("Dynamic Portfolio Optimizer")

with st.sidebar:
    st.header("Portfolio Parameters")
    default_tickers = "AAPL, MSFT, GOOGL, AMZN, META"
    tickers_input = st.text_input("Enter Tickers (comma separated):", default_tickers)
    
    objective = st.radio("Optimization Objective", ["Max Sharpe", "Min Volatility"])
    
    # 10% to 100% slider
    max_weight_pct = st.slider("Max Weight per Stock (%)", min_value=10, max_value=100, value=100, step=5)
    max_weight = max_weight_pct / 100.0

if tickers_input:
    tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
    
    # Validation: Max weight cannot be mathematically less than 1/N 
    min_allowable_weight = 1.0 / len(tickers)
    if max_weight < min_allowable_weight:
        st.error(f"With {len(tickers)} tickers, the maximum weight cannot be less than {min_allowable_weight*100:.1f}% to sum to 100%. Please increase the Max Weight slider or reduce the number of tickers.")
        st.stop()
        
    try:
        with st.spinner('Downloading data and calculating...'):
            df = load_data(tickers)
            
            mu = expected_returns.mean_historical_return(df)
            S = risk_models.sample_cov(df)
            
            # Optimization
            ef = EfficientFrontier(mu, S, weight_bounds=(0, max_weight))
            
            if objective == "Max Sharpe":
                raw_weights = ef.max_sharpe()
            else:
                raw_weights = ef.min_volatility()
                
            cleaned_weights = ef.clean_weights()
            ret, vol, sharpe = ef.portfolio_performance()
            
            st.success("Optimization Complete!")
            
            st.write("---")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader(f"Optimal Weights ({objective})")
                weights_df = pd.DataFrame.from_dict(cleaned_weights, orient='index', columns=['Weight'])
                # Sort descending and filter small weights
                weights_df = weights_df[weights_df['Weight'] > 0.0001].sort_values(by='Weight', ascending=False)
                st.dataframe(weights_df.style.format("{:.2%}"))
                
            with col2:
                st.subheader("Expected Portfolio Performance")
                m1, m2, m3 = st.columns(3)
                m1.metric("Expected Annual Return", f"{ret:.2%}")
                m2.metric("Annual Volatility (Risk)", f"{vol:.2%}")
                m3.metric("Sharpe Ratio", f"{sharpe:.2f}")
                
            st.write("---")
            st.subheader("Efficient Frontier Analysis")
            
            with st.spinner('Generating Efficient Frontier Visualization...'):
                n_samples = 2000
                w = np.random.dirichlet(np.ones(len(tickers)), n_samples)
                
                # Math for random portfolios
                rp_ret = w.dot(mu)
                rp_var = np.einsum('ij,jk,ik->i', w, S.values, w)
                rp_vol = np.sqrt(rp_var)
                rp_sharpe = rp_ret / rp_vol
                
                # Math for Efficient Frontier Curve
                ef_vols = []
                ef_rets = []
                
                ef_minvol = EfficientFrontier(mu, S, weight_bounds=(0, max_weight))
                try:
                    ef_minvol.min_volatility()
                    min_vol_ret = ef_minvol.portfolio_performance()[0]
                except:
                    min_vol_ret = mu.min()
                
                tr_sweep = np.linspace(min_vol_ret, mu.max(), 50)
                for tr in tr_sweep:
                    ef_sweep = EfficientFrontier(mu, S, weight_bounds=(0, max_weight))
                    try:
                        ef_sweep.efficient_return(target_return=tr)
                        ef_vols.append(ef_sweep.portfolio_performance()[1])
                        ef_rets.append(tr)
                    except:
                        pass
                
                # Plotly Figure
                fig = go.Figure()
                
                # Random Portfolios (Feasible Set)
                fig.add_trace(go.Scatter(
                    x=rp_vol, y=rp_ret, 
                    mode='markers', 
                    marker=dict(color=rp_sharpe, colorscale='Viridis', size=5, showscale=True, colorbar=dict(title='Sharpe')),
                    name='Random Portfolios',
                    opacity=0.6,
                    hovertemplate='<b>Ret:</b> %{y:.2%}<br><b>Vol:</b> %{x:.2%}<br><b>Sharpe:</b> %{marker.color:.2f}<extra></extra>'
                ))
                
                # EF Curve
                if len(ef_vols) > 0:
                    fig.add_trace(go.Scatter(
                        x=ef_vols, y=ef_rets,
                        mode='lines',
                        line=dict(color='black', width=3, dash='dash'),
                        name='Efficient Frontier Constraints'
                    ))
                    
                # Optimal Portfolio Marker
                fig.add_trace(go.Scatter(
                    x=[vol], y=[ret],
                    mode='markers',
                    marker=dict(color='red', symbol='star', size=18, line=dict(width=2, color='DarkSlateGrey')),
                    name=f'Optimal: {objective}',
                    hovertemplate='<b>Optimal Portfolio</b><br>Ret: %{y:.2%}<br>Vol: %{x:.2%}<extra></extra>'
                ))
                
                fig.update_layout(
                    xaxis_title="Volatility (Risk)",
                    yaxis_title="Expected Return",
                    height=600,
                    template='plotly_white',
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error during optimization: {str(e)}")
