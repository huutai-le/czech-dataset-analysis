import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import kagglehub

# =========================
# Load environment variables
# =========================
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# =========================
# PostgreSQL connection
# =========================
EXTRACT_DB = "postgres"

extract_engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{EXTRACT_DB}"
)

# =========================
# Download dataset from Kaggle
# =========================
print("Downloading dataset...")

dataset_path = kagglehub.dataset_download(
    "marceloventura/the-berka-dataset"
)

print("Dataset downloaded to:")
print(dataset_path)

# =========================
# CSV files to load
# =========================
csv_files = [
    "account.csv",
    "card.csv",
    "client.csv",
    "disp.csv",
    "district.csv",
    "loan.csv",
    "order.csv",
    "trans.csv"
]

# =========================
# Load each CSV to PostgreSQL
# =========================
for file_name in csv_files:

    file_path = Path(dataset_path) / file_name

    print(f"\nLoading {file_name}...")

    # Read CSV
    df = pd.read_csv(file_path, sep=";")
    
    # Table name = file name without .csv
    table_name = file_name.replace(".csv", "")

    # Upload to PostgreSQL
    df.to_sql(
        table_name,
        extract_engine,
        if_exists="replace",   # replace old table
        index=False
    )

    print(f"Table '{table_name}' created successfully.")

print("\nAll tables loaded successfully!")

# =========================
# SQL statements
# =========================
sql_commands = [

    # =========================
    # PRIMARY KEYS
    # =========================

    """
    ALTER TABLE district
    ADD PRIMARY KEY ("A1");
    """,

    """
    ALTER TABLE account
    ADD PRIMARY KEY (account_id);
    """,

    """
    ALTER TABLE client
    ADD PRIMARY KEY (client_id);
    """,

    """
    ALTER TABLE disp
    ADD PRIMARY KEY (disp_id);
    """,

    """
    ALTER TABLE loan
    ADD PRIMARY KEY (loan_id);
    """,

    """
    ALTER TABLE card
    ADD PRIMARY KEY (card_id);
    """,

    """
    ALTER TABLE "order"
    ADD PRIMARY KEY (order_id);
    """,

    """
    ALTER TABLE trans
    ADD PRIMARY KEY (trans_id);
    """,

    # =========================
    # FOREIGN KEYS
    # =========================

    # account -> district
    """
    ALTER TABLE account
    ADD CONSTRAINT fk_account_district
    FOREIGN KEY (district_id)
    REFERENCES district("A1");
    """,

    # client -> district
    """
    ALTER TABLE client
    ADD CONSTRAINT fk_client_district
    FOREIGN KEY (district_id)
    REFERENCES district("A1");
    """,

    # disp -> account
    """
    ALTER TABLE disp
    ADD CONSTRAINT fk_disp_account
    FOREIGN KEY (account_id)
    REFERENCES account(account_id);
    """,

    # disp -> client
    """
    ALTER TABLE disp
    ADD CONSTRAINT fk_disp_client
    FOREIGN KEY (client_id)
    REFERENCES client(client_id);
    """,

    # loan -> account
    """
    ALTER TABLE loan
    ADD CONSTRAINT fk_loan_account
    FOREIGN KEY (account_id)
    REFERENCES account(account_id);
    """,

    # order -> account
    """
    ALTER TABLE "order"
    ADD CONSTRAINT fk_order_account
    FOREIGN KEY (account_id)
    REFERENCES account(account_id);
    """,

    # trans -> account
    """
    ALTER TABLE trans
    ADD CONSTRAINT fk_trans_account
    FOREIGN KEY (account_id)
    REFERENCES account(account_id);
    """,

    # card -> disp
    """
    ALTER TABLE card
    ADD CONSTRAINT fk_card_disp
    FOREIGN KEY (disp_id)
    REFERENCES disp(disp_id);
    """
]

# =========================
# Execute SQL
# =========================
with extract_engine.connect() as connection:

    for command in sql_commands:

        try:
            connection.execute(text(command))
            connection.commit()
            print("SUCCESS:")
            print(command)

        except Exception as e:
            print("ERROR:")
            print(command)
            print(e)

print("\nAll relationships created successfully!")
