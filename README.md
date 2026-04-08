# Dynamic Portfolio Optimizer

## 1. Project Description and Goals
The **Dynamic Portfolio Optimizer** is a quantitative financial tool built in Python and Streamlit. It solves the common problem of "black-boxed" optimization by providing portfolio managers with an interactive, immediate, and intuitive visual representation of Modern Portfolio Theory (Markowitz Mean-Variance Optimization). 

**Key Features:**
- Seamlessly fetches historical market data for custom ticker inputs.
- Provides interactive constraints, allowing users to set maximum single-stock weight exposure limits.
- Toggles between purely minimizing volatility ("Min Volatility") and maximizing risk-adjusted returns ("Max Sharpe").
- Instantly graphs the Efficient Frontier, a Monte Carlo feasible set of 2,000 random portfolios, and the specific optimal portfolio on an interactive Plotly chart.

## 2. Running Locally

### Prerequisites
Ensure you have Python 3.9+ installed.

### Installation
Open your terminal and install the required dependencies:
```bash
pip install streamlit yfinance PyPortfolioOpt plotly pandas numpy
```

### Execution
Navigate to the project directory and run the application:
```bash
streamlit run app.py
```
A local server will start, and your browser will automatically open the dashboard at `http://localhost:8501`.

---

## 3. DRIVER Workflow Summary
DRIVER plugin (https://github.com/CinderZhang/driver-plugin).

We utilized the **DRIVER** framework to structure the development sequentially:

1. **DEFINE (开题调研):** We began by identifying the problem and reviewing existing libraries. We selected `yfinance` for data ingestion, `PyPortfolioOpt` for heavy-lifting math algorithms, and `Streamlit` with `Plotly` for a dynamic UI, capturing this in the Product Overview.
2. **REPRESENT:** We broke the project into four distinct, buildable pieces inside our `roadmap.md`: Data Pipeline, Core Math, UI & Constraints, and Dynamic Visualization. 
3. **IMPLEMENT:** We adopted a "Show Don't Tell" methodology. We built the Data Pipeline script, immediately ran the server to output raw Pandas dataframes, and iterated structurally through Core Math and UI components.
4. **VALIDATE:** The human operator actively stress-tested the mathematical boundaries (checking 1/N allocation limits) and manually analyzed outputs to verify there were 0 Data NAs before proceeding to optimization calculations.
5. **EVOLVE:** We refined the codebase significantly when we encountered a critical `yfinance` API feature change (where it passes MultiIndex columns). We successfully re-scoped and debugged the `load_data` function to safely extract the standard 'Close' column array, ensuring downstream pipeline stability. 
6. **REFLECT:** Covered in the disclosure below, capturing the collaborative learning loops between AI implementation and human financial validation.

---

## 4. AI Usage Disclosure and Reflection

*Note: This section captures the required reflection of the human-AI partnership mapping for this course output.*

**AI Model Used:** Antigravity (Gemini 3.1 Pro High / Deepmind Advanced Agentic Coding)

**Division of Labor:**
- **AI (Cognition Mate):** Tasked with generating boilerplate architecture, orchestrating Streamlit rendering loops, building the heavy-lifting Plotly visual generation logic, and suggesting structural data extraction bug-fixes (the yfinance MultiIndex resolution).
- **Human (Pilot-in-Command):** Maintained absolute human centrality by establishing the initial product vision, breaking down the milestones, validating the raw financial math from `PyPortfolioOpt`, and enforcing stringent data scrubbing requirements (forward filling and dropping NAs to prevent silent solver crashes) prior to visualization. 

## 5. Open-Source Attribution & Usage Disclosure

This application was made possible by the following open-source frameworks and libraries. Their documentation and active maintainers provided the foundation for this project:

* **Python (3.9+):** The core programming environment.
* **Streamlit:** Utilized for the frontend web framework, enabling the reactive UI, sidebar constraints, and real-time state management without a separate backend.
* **PyPortfolioOpt (`pypfopt`):** The primary quantitative engine used to calculate historical expected returns, generate the sample covariance matrix, and solve the Markowitz Mean-Variance Optimization boundaries.
* **yfinance:** Utilized for data ingestion to reliably query and download historical daily market prices.
* **Plotly:** Powered the dynamic, interactive visualization of the Efficient Frontier and the 2,000-simulation Monte Carlo scatter plot.
* **Pandas & NumPy:** Provided the essential data structures for time-series manipulation, NA-handling, and the underlying matrix algebra required for risk calculation.

**Reflections on the Workflow:**
The tight feedback loops encouraged by the DRIVER framework prevented massive code debt. Instead of prompting for a massive un-testable script, breaking the application into raw data outputs -> raw math outputs -> UI -> Visualization meant that critical errors (like the `yfinance` MultiIndex API change) were caught immediately in Milestone 1, rather than silently cascading through Milestone 4. 

This human-in-the-loop oversight ensured that while the AI generated code at scale, the actual algorithmic strategy and dataset validity remained solely under human jurisdiction.
