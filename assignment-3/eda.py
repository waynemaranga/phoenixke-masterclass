import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def eda(db_path) -> None:
    conn: sqlite3.Connection = sqlite3.connect(db_path)
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()

    for table in tables:
        print(f"\n[EDA] {table}")
        df: pd.DataFrame = pd.read_sql_query(f"SELECT * FROM {table}", conn)

        print(df.describe())

        plt.figure(figsize=(6, 4))
        df['star_rating'].value_counts().sort_index().plot(kind='bar', color='teal')
        plt.title(f"{table} – Star Ratings")
        plt.xlabel("Stars")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(f"{table}_stars.png")

        plt.figure(figsize=(6, 4))
        df.boxplot(column="price")
        plt.title(f"{table} – Price Boxplot")
        plt.ylabel("£ Price")
        plt.tight_layout()
        plt.savefig(f"{table}_price.png")

    conn.close()
    print("[EDA] Plots saved.")

if __name__ == "__main__":
    eda("mini.db")
