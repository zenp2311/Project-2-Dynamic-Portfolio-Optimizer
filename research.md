# Research: Portfolio Optimizer

## Existing Foundations

1. **PyPortfolioOpt**
   - **What it does:** A specialized Python library that provides "out-of-the-box" solutions for financial portfolio optimization. It implements classical techniques like Markowitz Mean-Variance Optimization, the Efficient Frontier, Black-Litterman allocation, and Hierarchical Risk Parity.
   - **How it's relevant:** Directly solves the core requirement of finding optimal weights, calculating expected returns, and the covariance matrix. Its API is built specifically for this and saves us from implementing optimization solvers from scratch.

2. **CVXPY**
   - **What it does:** A general-purpose modeling language for convex optimization problems.
   - **How it's relevant:** While PyPortfolioOpt uses `cvxpy` under the hood, we could use CVXPY directly if we need deeply custom constraints (e.g., sector bounds, ESG constraints, transaction cost modeling) that aren't natively supported.

3. **yfinance / pandas-datareader**
   - **What it does:** Fetches historical market data.
   - **How it's relevant:** Fulfills the requirement of retrieving historical price data for the 5-15 specific tickers input by the user without requiring a paid data feed initially.

## Architecture

Typical Streamlit + Portfolio Optimization Architecture:
- **UI & Input:** Streamlit sidebar for ticker input and parameter configuration (e.g., date ranges, risk tolerance).
- **Data Layer:** `yfinance` to grab adjusted closing prices. `pandas` to calculate daily/monthly returns and covariance matrices.
- **Optimization Engine:** `PyPortfolioOpt` to minimize volatility for a target return or maximize the Sharpe ratio.
- **Output:** Streamlit charts (using `plotly` or native Streamlit charts) to display the optimal portfolio weights (pie chart), the efficient frontier, and key metrics (expected return, expected risk/volatility, Sharpe ratio).
