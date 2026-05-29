# =========================================================
# LOAN RISK PREDICTION PIPELINE
# =========================================================
# Goal:
# Predict risky loan status using banking behavior
#
# Risky:
# - Contract finished, loan not payed
# - Running contract, client in debt
#
# Safe:
# - Contract finished, no problems
# - Running contract, OK so far
#
# =========================================================

import os
import numpy as np
import pandas as pd

from sqlalchemy import create_engine
from dotenv import load_dotenv

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score
)

from sklearn.ensemble import RandomForestClassifier

# =========================================================
# LOAD ENV VARIABLES
# =========================================================
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

DB_NAME = "db_banking"

# =========================================================
# POSTGRES CONNECTION
# =========================================================
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# =========================================================
# EXTRACT DATA
# =========================================================

print("\nLoading data from PostgreSQL...")

loan = pd.read_sql("SELECT * FROM loan", engine)
loan = loan.rename(columns={
    "amount": "loan_amount",
    "payments": "monthly_payment"
})
trans = pd.read_sql("SELECT * FROM trans", engine)
account = pd.read_sql("SELECT * FROM account", engine)
client = pd.read_sql("SELECT * FROM client", engine)
disp = pd.read_sql("SELECT * FROM disp", engine)
card = pd.read_sql("SELECT * FROM card", engine)

print("Data loaded successfully.")

# =========================================================
# TARGET VARIABLE
# =========================================================

print("\nCreating target variable...")

loan["target"] = np.where(
    loan["status"].isin([
        "Contract finished, loan not payed",
        "Running contract, client in debt"
    ]),
    1,
    0
)

# =========================================================
# FEATURE ENGINEERING
# =========================================================

print("\nCreating features...")

# ---------------------------------------------------------
# 1. Average Balance
# ---------------------------------------------------------
avg_balance = (
    trans
    .groupby("account_id")["balance"]
    .mean()
    .reset_index(name="avg_balance")
)

# ---------------------------------------------------------
# 2. Transaction Count
# ---------------------------------------------------------
transaction_count = (
    trans
    .groupby("account_id")["trans_id"]
    .count()
    .reset_index(name="transaction_count")
)

# ---------------------------------------------------------
# 3. Withdrawal Ratio
# ---------------------------------------------------------

withdrawals = (
    trans[trans["type"] == "Withdrawal"]
    .groupby("account_id")["amount"]
    .sum()
    .reset_index(name="withdrawal_amount")
)

total_transactions = (
    trans
    .groupby("account_id")["amount"]
    .sum()
    .reset_index(name="total_amount")
)

withdrawal_ratio = withdrawals.merge(
    total_transactions,
    on="account_id",
    how="left"
)

withdrawal_ratio["withdrawal_ratio"] = (
    withdrawal_ratio["withdrawal_amount"]
    / withdrawal_ratio["total_amount"]
)

withdrawal_ratio = withdrawal_ratio[[
    "account_id",
    "withdrawal_ratio"
]]

# ---------------------------------------------------------
# 4. Transaction Volatility
# ---------------------------------------------------------
volatility = (
    trans
    .groupby("account_id")["amount"]
    .std()
    .reset_index(name="transaction_volatility")
)

# ---------------------------------------------------------
# 5. Negative Balance Count
# ---------------------------------------------------------
negative_balance = (
    trans[trans["balance"] < 0]
    .groupby("account_id")
    .size()
    .reset_index(name="negative_balance_count")
)

# ---------------------------------------------------------
# 6. Card Ownership
# ---------------------------------------------------------
card_ownership = (
    disp[["disp_id", "account_id"]]
    .merge(card[["disp_id"]], on="disp_id", how="left")
)

card_ownership["has_card"] = np.where(
    card_ownership["disp_id"].notna(),
    1,
    0
)

card_ownership = (
    card_ownership
    .groupby("account_id")["has_card"]
    .max()
    .reset_index()
)

# ---------------------------------------------------------
# 7. Client Demographics
# ---------------------------------------------------------
client_info = (
    disp[["client_id", "account_id"]]
    .merge(
        client[["client_id", "gender", "birth_number", "district_id"]],
        on="client_id",
        how="left"
    )
)

# Age
current_year = 2025

client_info["birth_number"] = pd.to_datetime(
    client_info["birth_number"]
)

client_info["age"] = (
    current_year
    - client_info["birth_number"].dt.year
)

client_info = client_info[[
    "account_id",
    "gender",
    "age",
    "district_id"
]]

# =========================================================
# BUILD FEATURE TABLE
# =========================================================

print("\nBuilding feature dataset...")

features = loan.merge(
    avg_balance,
    on="account_id",
    how="left"
)

features = features.merge(
    transaction_count,
    on="account_id",
    how="left"
)

features = features.merge(
    withdrawal_ratio,
    on="account_id",
    how="left"
)

features = features.merge(
    volatility,
    on="account_id",
    how="left"
)

features = features.merge(
    negative_balance,
    on="account_id",
    how="left"
)

features = features.merge(
    card_ownership,
    on="account_id",
    how="left"
)

features = features.merge(
    client_info,
    on="account_id",
    how="left"
)

# =========================================================
# SELECT FEATURES
# =========================================================

model_df = features[[
    "loan_amount",
    "duration",
    "monthly_payment",
    "avg_balance",
    "transaction_count",
    "withdrawal_ratio",
    "transaction_volatility",
    "negative_balance_count",
    "has_card",
    "gender",
    "age",
    "district_id",
    "target"
]].copy()


# =========================================================
# HANDLE MISSING VALUES
# =========================================================

model_df["withdrawal_ratio"] = (
    model_df["withdrawal_ratio"]
    .fillna(0)
)

model_df["negative_balance_count"] = (
    model_df["negative_balance_count"]
    .fillna(0)
)

model_df["has_card"] = (
    model_df["has_card"]
    .fillna(0)
)

# =========================================================
# SPLIT X / y
# =========================================================

X = model_df.drop(columns=["target"])
y = model_df["target"]

# =========================================================
# FEATURE TYPES
# =========================================================

numeric_features = [
    "loan_amount",
    "duration",
    "monthly_payment",
    "avg_balance",
    "transaction_count",
    "withdrawal_ratio",
    "transaction_volatility",
    "negative_balance_count",
    "has_card",
    "age"
]

categorical_features = [
    "gender",
    "district_id"
]

# =========================================================
# PREPROCESSING
# =========================================================

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median"))
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)

# =========================================================
# MODEL
# =========================================================

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42
)

# =========================================================
# FULL PIPELINE
# =========================================================

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", model)
])

# =========================================================
# TRAIN TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# =========================================================
# TRAIN MODEL
# =========================================================

print("\nTraining model...")

pipeline.fit(X_train, y_train)

print("Model training completed.")

# =========================================================
# PREDICTIONS
# =========================================================

y_pred = pipeline.predict(X_test)

y_prob = pipeline.predict_proba(X_test)[:, 1]

# =========================================================
# EVALUATION
# =========================================================

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

auc = roc_auc_score(y_test, y_prob)

print(f"\nROC-AUC Score: {auc:.4f}")

# =========================================================
# FEATURE IMPORTANCE
# =========================================================

print("\nTop Feature Importance:")

encoded_features = (
    numeric_features
    + list(
        pipeline.named_steps["preprocessor"]
        .transformers_[1][1]
        .named_steps["onehot"]
        .get_feature_names_out(categorical_features)
    )
)

importance_df = pd.DataFrame({
    "feature": encoded_features,
    "importance": pipeline.named_steps["model"].feature_importances_
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

print(importance_df.head(15))

# =========================================================
# SAVE FEATURE TABLE
# =========================================================

model_df.to_sql(
    "loan_risk_features",
    engine,
    if_exists="replace",
    index=False
)

print("\nFeature table saved to PostgreSQL.")

print("\nLoan Risk Prediction Pipeline Completed!")