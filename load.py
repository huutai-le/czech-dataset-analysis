import os
import pandas as pd

from sqlalchemy import create_engine
from dotenv import load_dotenv

# ==========================================
# LOAD ENV
# ==========================================
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

TRANSFORM_DB = "db_banking"
TARGET_DB = "db_target"

# ==========================================
# CONNECTIONS
# ==========================================
transform_engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{TRANSFORM_DB}"
)

target_engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{TARGET_DB}"
)

# ==========================================
# LOAD TABLES
# ==========================================
account = pd.read_sql("SELECT * FROM account", transform_engine)
client = pd.read_sql("SELECT * FROM client", transform_engine)
disp = pd.read_sql("SELECT * FROM disp", transform_engine)
district = pd.read_sql("SELECT * FROM district", transform_engine)
loan = pd.read_sql("SELECT * FROM loan", transform_engine)
card = pd.read_sql("SELECT * FROM card", transform_engine)
orders = pd.read_sql('SELECT * FROM "order"', transform_engine)
trans = pd.read_sql("SELECT * FROM trans", transform_engine)

# ==========================================
# DIM_CUSTOMERS
# ==========================================
dim_customers = (
    client
    .merge(disp, on="client_id", how="left")
    [["client_id", "account_id", "gender", "birth_number", "district_id"]]
)

# ==========================================
# DIM_DISTRICTS
# ==========================================
dim_districts = district.rename(columns={
    "A1": "district_id",
    "A2": "district_name",
    "A3": "region",
    "A4": "population",
    "A10": "urban_ratio"
})

# ==========================================
# DIM_ACCOUNTS
# ==========================================
dim_accounts = account[[
    "account_id",
    "district_id",
    "frequency",
    "date"
]].rename(columns={
    "date": "account_created_date"
})

# ==========================================
# DIM_CARDS
# ==========================================
dim_cards = card.rename(columns={
    "type": "card_type",
    "issued": "issued_date"
})

# ==========================================
# FACT_TRANSACTIONS
# ==========================================
fact_transactions = trans[[
    "trans_id",
    "account_id",
    "date",
    "type",
    "operation",
    "amount",
    "balance",
    "k_symbol"
]].rename(columns={
    "date": "transaction_date",
    "type": "transaction_type"
})

# ==========================================
# FACT_LOANS
# ==========================================
fact_loans = loan[[
    "loan_id",
    "account_id",
    "date",
    "amount",
    "duration",
    "payments",
    "status"
]].rename(columns={
    "date": "loan_date",
    "amount": "loan_amount",
    "payments": "monthly_payment"
})

# ==========================================
# FACT_ORDERS
# ==========================================
fact_orders = orders.rename(columns={
    "amount": "order_amount"
})

# ==========================================
# DIM_DATES
# ==========================================
all_dates = pd.concat([
    fact_transactions["transaction_date"],
    fact_loans["loan_date"],
    dim_accounts["account_created_date"]
]).dropna().unique()

dim_dates = pd.DataFrame({
    "date": pd.to_datetime(all_dates)
})

dim_dates["year"] = dim_dates["date"].dt.year
dim_dates["month"] = dim_dates["date"].dt.month
dim_dates["quarter"] = dim_dates["date"].dt.quarter
dim_dates["day"] = dim_dates["date"].dt.day

# ==========================================
# LOAD TO db_targer
# ==========================================
dim_customers.to_sql(
    "dim_customers",
    target_engine,
    if_exists="replace",
    index=False
)

dim_districts.to_sql(
    "dim_districts",
    target_engine,
    if_exists="replace",
    index=False
)

dim_accounts.to_sql(
    "dim_accounts",
    target_engine,
    if_exists="replace",
    index=False
)

dim_cards.to_sql(
    "dim_cards",
    target_engine,
    if_exists="replace",
    index=False
)

dim_dates.to_sql(
    "dim_dates",
    target_engine,
    if_exists="replace",
    index=False
)

fact_transactions.to_sql(
    "fact_transactions",
    target_engine,
    if_exists="replace",
    index=False
)

fact_loans.to_sql(
    "fact_loans",
    target_engine,
    if_exists="replace",
    index=False
)

fact_orders.to_sql(
    "fact_orders",
    target_engine,
    if_exists="replace",
    index=False
)

print("Target tables created successfully!")