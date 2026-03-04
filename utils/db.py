from sqlalchemy import create_engine
import pandas as pd

def connect_db():
    return create_engine('postgresql://username:password@localhost/upi_dashboard')

def load_data_from_csv():
    df = pd.read_csv('data/sample_upi_data.csv')
    engine = connect_db()
    df.to_sql('upi_transactions', engine, if_exists='replace', index=False)

def get_data():
    engine = connect_db()
    return pd.read_sql("SELECT * FROM upi_transactions", engine)