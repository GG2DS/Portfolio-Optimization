import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import scipy.optimize as sco
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine

# 1. Database Configuration
db_user = "postgres"
db_password = "test1234"
db_host = "localhost"
db_port = "5432"
db_name = "portfolio_db"

# Create SQLAlchemy engine
engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# 2. Fetch a Diversified Selection of Assets from PostgreSQL
selected_assets_query = """
    SELECT asset FROM asset_pool 
    WHERE industry IN (SELECT DISTINCT industry FROM asset_pool)
    ORDER BY RANDOM()
    LIMIT 20
"""
selected_assets = pd.read_sql(selected_assets_query, engine)['asset'].tolist()

# Ensure at least some assets are selected
if not selected_assets:
    raise ValueError("No assets were selected. Please check your database or selection criteria.")

# 3. Fetch Stock Data from Yahoo Finance
pf_data = pd.DataFrame()

for asset in selected_assets:
    try:
        pf_data[asset] = yf.download(asset, start='2015-01-01')['Close']
    except Exception as e:
        print(f"Warning: Could not download data for {asset}: {e}")

# Drop any assets that had issues retrieving data
pf_data.dropna(axis=1, how='all', inplace=True)
selected_assets = pf_data.columns.tolist()  # Update list based on successful downloads

# 4. Scrape ESG Ratings from Yahoo Finance
def get_esg_rating(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/sustainability"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        esg_data = {"asset": ticker}

        # Mapping of Yahoo Finance ESG sections
        esg_sections = {
            "TOTAL_ESG_SCORE": "total_esg_risk_score",
            "ENVIRONMENT_SCORE": "environmental_risk_score",
            "SOCIAL_SCORE": "social_risk_score",
            "GOVERNANCE_SCORE": "governance_risk_score"
        }

        for testid, column_name in esg_sections.items():
            section = soup.find("section", {"data-testid": testid})
            if section:
                score_element = section.find("h4")
                if score_element:
                    esg_data[column_name] = score_element.text.strip()
                else:
                    esg_data[column_name] = None
            else:
                esg_data[column_name] = None

        return esg_data

    except Exception as e:
        print(f"⚠️ Error fetching ESG rating for {ticker}: {e}")
        return None

# 5. Fetch ESG Ratings for Selected Assets
esg_data = []
for asset in selected_assets:
    esg_scores = get_esg_rating(asset)
    if esg_scores:  # Only add assets with valid ESG data
        esg_data.append(esg_scores)

# Convert ESG data to a DataFrame
esg_df = pd.DataFrame(esg_data)

# Save ESG Ratings to PostgreSQL
if not esg_df.empty:
    esg_df.to_sql("esg_ratings", engine, if_exists='replace', index=False, method="multi")
    print("ESG ratings successfully fetched and stored in PostgreSQL!")
else:
    print("No ESG ratings were found for the selected assets.")

# 6. Calculate Log Returns
log_returns = np.log(pf_data / pf_data.shift(1))
num_assets = len(selected_assets)

# 7. Simulating Random Portfolios
pf_returns = []
pf_volatilities = []

for _ in range(2000):
    weights = np.random.random(num_assets)
    weights /= np.sum(weights)
    pf_returns.append(np.sum(weights * log_returns.mean()) * 250)
    pf_volatilities.append(np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 250, weights))))

# Convert to DataFrame
portfolios = pd.DataFrame({'return': pf_returns, 'volatility': pf_volatilities})

# 8. Portfolio Optimization Functions
annual_returns = log_returns.mean() * 250
annual_cov = log_returns.cov() * 250

def portfolio_return(weights, returns):
    return np.sum(weights * returns)

def portfolio_volatility(weights, cov_matrix):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

def min_volatility(target_return):
    """
    Minimize portfolio volatility for a given target return.
    """
    def objective(weights):
        return portfolio_volatility(weights, annual_cov)

    constraints = (
        {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1},  # Weights must sum to 1
        {'type': 'eq', 'fun': lambda weights: portfolio_return(weights, annual_returns) - target_return}  # Achieve target return
    )

    bounds = tuple((0, 1) for _ in range(num_assets))  # No short selling
    initial_guess = np.array(num_assets * [1. / num_assets])

    result = sco.minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    return result

# 9. Generate Multiple Optimal Portfolios for Different Target Returns
pf_returns = np.array(pf_returns)
target_returns = np.linspace(np.min(pf_returns), np.max(pf_returns), 50)

frontier_volatilities = []
optimal_portfolios = []

for target in target_returns:
    res = min_volatility(target)
    if res.success:
        vol = portfolio_volatility(res.x, annual_cov)
        frontier_volatilities.append(vol)

        # Store optimal weights for this target return
        for asset, weight in zip(selected_assets, res.x):
            optimal_portfolios.append({'target_return': target, 'asset': asset, 'weight': weight})
    else:
        frontier_volatilities.append(np.nan)

# Create DataFrame for the Efficient Frontier
frontier_df = pd.DataFrame({
    'target_return': target_returns,
    'efficient_volatility': frontier_volatilities
})

# Create DataFrame for Optimal Portfolio Allocations
optimal_weights_df = pd.DataFrame(optimal_portfolios)

# 10. Save Data to PostgreSQL
portfolios.to_sql("simulated_portfolios", engine, if_exists='replace', index=False)
frontier_df.to_sql("efficient_frontier", engine, if_exists='replace', index=False)
optimal_weights_df.to_sql("optimal_weights", engine, if_exists='replace', index=False)

print("Data has been saved to the PostgreSQL database '", db_name, "' successfully.")

# Debugging check
print("\n🔎 ESG Ratings Preview:")
print(esg_df.head())
print(f"Total ESG ratings fetched: {len(esg_df)}")
