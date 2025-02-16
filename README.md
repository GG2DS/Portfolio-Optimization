# Portfolio Optimization & ESG Analysis

## Project Overview
This project builds a **dynamic portfolio optimization model** that allows users to:
- **Select stocks dynamically** from a **diversified asset pool**.
- **Optimize portfolio weights** based on expected return & risk (volatility).
- **Evaluate ESG (Environmental, Social, and Governance) ratings** for selected companies.
- **Analyze risk-return relationships** and visualize the **Efficient Frontier**.
- **Store and manage data using PostgreSQL**, with integration into **Power BI** for interactive analysis.

---

## Technologies Used
- **Python** (Data Collection, Portfolio Optimization, SQL Integration)
- **PostgreSQL** (Data Storage, SQL Queries, Views)
- **Power BI** (Visualization, Dynamic Dashboards)
- **Yahoo Finance API** (Stock Price & ESG Data)
- **SQLAlchemy** (Database Connection)
- **Scipy & NumPy** (Mathematical Optimization)
- **Matplotlib** (Plotting & Data Visualization)

---

## Project Structure
```
📁 Portfolio-Optimization-ESG
│── 📄 README.md  # Documentation
│── 📄 requirements.txt  # Python dependencies
│── 📂 sql-scripts  # SQL queries for database setup
│── 📂 powerbi-dashboard  # Power BI .pbix file
│── 📄 portfolio_analysis.py  # Main Python script for data processing
│── 📂 data  # Stored dataset snapshots
│── 📂 notebooks  # Jupyter Notebooks (optional)
```

---

Step 1: Setup PostgreSQL Database
Create Database & Tables
Run the following SQL commands to **set up the required tables:
```sql
CREATE DATABASE portfolio_db;

-- Table: Asset Metadata (Tickers, Company Names, Industry, ESG Scores)
CREATE TABLE asset_metadata (
    asset TEXT PRIMARY KEY,
    company_name TEXT,
    industry TEXT,
    total_esg_risk_score DOUBLE PRECISION
);

-- Table: ESG Ratings
CREATE TABLE esg_ratings (
    asset TEXT PRIMARY KEY,
    total_esg_risk_score DOUBLE PRECISION,
    FOREIGN KEY (asset) REFERENCES asset_metadata(asset)
);

-- Table: Simulated Portfolios (Randomly Generated Portfolios)
CREATE TABLE simulated_portfolios (
    return DOUBLE PRECISION,
    volatility DOUBLE PRECISION
);

-- Table: Efficient Frontier (Optimized Portfolio Data)
CREATE TABLE efficient_frontier (
    target_return DOUBLE PRECISION,
    efficient_volatility DOUBLE PRECISION
);

-- Table: Optimal Weights for Portfolios
CREATE TABLE optimal_weights (
    target_return DOUBLE PRECISION,
    asset TEXT,
    weight DOUBLE PRECISION,
    FOREIGN KEY (asset) REFERENCES asset_metadata(asset)
);
```

Populate the Tables with Asset Data
```sql
INSERT INTO asset_metadata (asset, company_name, industry) VALUES
('AAPL', 'Apple', 'Technology'),
('MSFT', 'Microsoft', 'Technology'),
('GOOGL', 'Google', 'Technology'),
('NVDA', 'NVIDIA', 'Technology'),
('AMD', 'AMD', 'Technology'),
('JPM', 'JPMorgan Chase', 'Financials'),
('GS', 'Goldman Sachs', 'Financials'),
('V', 'Visa', 'Financials'),
('PYPL', 'PayPal', 'Financials'),
('AMZN', 'Amazon', 'Consumer Discretionary');
```

---

## ** Step 2: Run the Python Script**
Install Dependencies**
Run the following command to install necessary packages:
```bash
pip install -r requirements.txt
```

### **🚀 Execute the Script**
```bash
python portfolio_analysis.py
```
This script will:
✅ **Fetch stock data from Yahoo Finance**
✅ **Calculate log returns and portfolio volatility**
✅ **Optimize portfolios based on a target return**
✅ **Store results into PostgreSQL**
✅ **Extract ESG scores for selected companies**

---

## ** Step 3: Power BI Dashboard**
After running the script, **import the SQL tables into Power BI** and create an interactive dashboard:

### **🔹 Key Visuals in Power BI**
1️ **Scatter Plot of Efficient Frontier** *(Risk vs. Return)*
2️ **Pie Chart of Portfolio Weights** *(Asset Allocation)*
3️ **KPI Cards for Expected Return, Volatility, & ESG Score**
4️ **Slicer for Selecting Portfolio Assets**
5️ **Dynamic ESG Tooltip for Selected Assets**

### ** Import Data into Power BI**
- Click **Get Data** → **PostgreSQL Database**
- Enter **Server: localhost**, **Database: portfolio_db**
- Load tables: `simulated_portfolios`, `efficient_frontier`, `optimal_weights`, `asset_metadata`

---

## ** How to Interpret the Portfolio Volatility & ESG Score?**

### ** Understanding Expected Volatility**
- A **portfolio volatility of 0.15 (15%)** means returns fluctuate **±15% annually**.
- Compare to benchmarks:
  - **S&P 500** volatility: ~18%
  - **Bond portfolios**: ~5%
  - **Tech stocks**: ~25%-30%

### ** Understanding ESG Score**
- **Lower ESG score (0-20):** Negligible risk 🌱
- **Medium ESG score (20-40):** Moderate risk ⚠️
- **High ESG score (40+):** Significant risk 🔴

---

## **🌍 Future Enhancements**
✅ **Automate asset selection using AI models** 🤖
✅ **Expand ESG metrics (carbon footprint, governance score)** 🌱
✅ **Integrate real-time market data for live tracking** 📊

---



