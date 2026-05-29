import os
import pandas as pd

from sqlalchemy import create_engine
from dotenv import load_dotenv

# =====================================================
# LOAD ENV VARIABLES
# =====================================================
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# =====================================================
# EXTRACT DATABASE (RAW)
# =====================================================
EXTRACT_DB = "postgres"

extract_engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{EXTRACT_DB}"
)

# =====================================================
# TRANSFORM DATABASE (CLEANED)
# =====================================================
TRANSFORM_DB = "db_banking"

transform_engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{TRANSFORM_DB}"
)

# =====================================================
# MAPPINGS
# =====================================================

frequency_mapping = {
    "POPLATEK MESICNE": "Monthly Issuance",
    "POPLATEK TYDNE": "Weekly Issuance",
    "POPLATEK PO OBRATU": "Issuance after Transaction"
}

loan_status_mapping = {
    "A": "Contract finished, no problems",
    "B": "Contract finished, loan not payed",
    "C": "Running contract, OK so far",
    "D": "Running contract, client in debt"
}

order_k_symbol_mapping = {
    "POJISTNE": "Insurance Payment",
    "SIPO": "Household Payment",
    "LEASING": "Leasing",
    "UVER": "Loan Payment"
}

trans_type_mapping = {
    "PRIJEM": "Credit",
    "VYDAJ": "Withdrawal"
}

trans_operation_mapping = {
    "VYBER KARTOU": "Credit card withdrawal",
    "VKLAD": "Credit in cash",
    "PREVOD Z UCTU": "Collection from another bank",
    "VYBER": "Withdrawal in cash",
    "PREVOD NA UCET": "Remittance to another bank"
}

trans_k_symbol_mapping = {
    "POJISTNE": "Insurance Payment",
    "SLUZBY": "Payment for statement",
    "UROK": "Interest credited",
    "SANKC. UROK": "Sanction interest if negative balance",
    "SIPO": "Household Payment",
    "DUCHOD": "Old-age pension",
    "UVER": "Loan Payment"
}

# =====================================================
# DATE FUNCTIONS
# =====================================================

def convert_date(value):

    if pd.isna(value):
        return None

    # Convert to string
    value = str(value)

    # Remove time part if exists
    value = value.split(" ")[0]

    # Ensure 6 digits
    value = value.zfill(6)

    yy = int(value[:2])
    mm = int(value[2:4])
    dd = int(value[4:6])

    return f"{1900 + yy}-{mm:02d}-{dd:02d}"

# =====================================================
# READ RAW TABLES
# =====================================================

print("\nReading raw tables from db_postgres...")

account_df = pd.read_sql(
    "SELECT * FROM account",
    extract_engine
)

card_df = pd.read_sql(
    "SELECT * FROM card",
    extract_engine
)

client_df = pd.read_sql(
    "SELECT * FROM client",
    extract_engine
)

disp_df = pd.read_sql(
    "SELECT * FROM disp",
    extract_engine
)

district_df = pd.read_sql(
    "SELECT * FROM district",
    extract_engine
)

loan_df = pd.read_sql(
    "SELECT * FROM loan",
    extract_engine
)

# order is reserved keyword
order_df = pd.read_sql(
    'SELECT * FROM "order"',
    extract_engine
)

# trans optional
try:

    trans_df = pd.read_sql(
        "SELECT * FROM trans",
        extract_engine
    )

except:

    trans_df = None

print("Raw tables loaded.")

# =====================================================
# TRANSFORM ACCOUNT
# =====================================================

print("\nTransforming account...")

account_df["frequency"] = (
    account_df["frequency"]
    .replace(frequency_mapping)
)

account_df["date"] = (
    account_df["date"]
    .apply(convert_date)
)

# =====================================================
# TRANSFORM CARD
# =====================================================

print("Transforming card...")

card_df["issued"] = (
    card_df["issued"]
    .apply(convert_date)
)

# =====================================================
# TRANSFORM CLIENT
# =====================================================

print("Transforming client...")

# Create gender column
def get_gender(value):

    if pd.isna(value):
        return None

    value = str(int(value)).zfill(6)

    mm = int(value[2:4])

    if mm > 50:
        return "Female"
    else:
        return "Male"


# Convert birth_number -> birth_date
def convert_birth_number(value):

    if pd.isna(value):
        return None

    value = str(int(value)).zfill(6)

    yy = int(value[:2])
    mm = int(value[2:4])
    dd = int(value[4:6])

    # Female logic
    if mm > 50:
        mm -= 50

    return f"{1900 + yy}-{mm:02d}-{dd:02d}"


# Create new columns
client_df["gender"] = (
    client_df["birth_number"]
    .apply(get_gender)
)

client_df["birth_number"] = (
    client_df["birth_number"]
    .apply(convert_birth_number)
)

# =====================================================
# TRANSFORM LOAN
# =====================================================

print("Transforming loan...")

loan_df["date"] = (
    loan_df["date"]
    .apply(convert_date)
)

loan_df["status"] = (
    loan_df["status"]
    .replace(loan_status_mapping)
)

# =====================================================
# TRANSFORM ORDER
# =====================================================

print("Transforming order...")

order_df["k_symbol"] = (
    order_df["k_symbol"]
    .replace(order_k_symbol_mapping)
)

# =====================================================
# TRANSFORM TRANS
# =====================================================

if trans_df is not None:

    print("Transforming trans...")

    trans_df["date"] = (
        trans_df["date"]
        .apply(convert_date)
    )

    trans_df["type"] = (
        trans_df["type"]
        .replace(trans_type_mapping)
    )

    trans_df["operation"] = (
        trans_df["operation"]
        .replace(trans_operation_mapping)
    )

    trans_df["k_symbol"] = (
        trans_df["k_symbol"]
        .replace(trans_k_symbol_mapping)
    )

# =====================================================
# LOAD CLEANED TABLES TO db_banking
# =====================================================

print("\nLoading cleaned tables into db_banking...")

account_df.to_sql(
    "account",
    transform_engine,
    if_exists="replace",
    index=False
)

card_df.to_sql(
    "card",
    transform_engine,
    if_exists="replace",
    index=False
)

client_df.to_sql(
    "client",
    transform_engine,
    if_exists="replace",
    index=False
)

disp_df.to_sql(
    "disp",
    transform_engine,
    if_exists="replace",
    index=False
)

district_df.to_sql(
    "district",
    transform_engine,
    if_exists="replace",
    index=False
)

loan_df.to_sql(
    "loan",
    transform_engine,
    if_exists="replace",
    index=False
)

order_df.to_sql(
    "order",
    transform_engine,
    if_exists="replace",
    index=False
)

if trans_df is not None:

    trans_df.to_sql(
        "trans",
        transform_engine,
        if_exists="replace",
        index=False
    )

print("\nAll cleaned tables loaded into db_banking successfully!")