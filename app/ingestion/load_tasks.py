import pandas as pd
from sqlalchemy import create_engine, text


def main() -> None:
    db_user = "cleaning"
    db_password = "cleaning"
    db_host = "localhost"
    db_port = "5436"
    db_name = "cleaning_analytics"

    csv_path = "data/raw/cleaning_tasks.csv"
    df = pd.read_csv(csv_path)

    df["scheduled_date"] = pd.to_datetime(df["scheduled_date"])
    df["completed_date"] = pd.to_datetime(df["completed_date"], errors="coerce")

    engine = create_engine(
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE cleaning_tasks;"))

    df.to_sql("cleaning_tasks", engine, if_exists="append", index=False)
    print(f"{len(df)} cleaning tasks loaded into PostgreSQL")


if __name__ == "__main__":
    main()