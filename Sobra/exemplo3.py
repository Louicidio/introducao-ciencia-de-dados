import sqlalchemy as sqla

engine = sqla.create_engine('sqlite:///mydatanovo.sqlite')

with engine.connect() as conn:
    conn.execute(sqla.text("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            idade INTEGER
        )
    """))

    with engine.connect() as conn: 
        conn.execute(sqla.text("""
            INSERT INTO usuarios (nome, idade)
            VALUES ('Ana', 25), ('Bruno', 28)
        """))
    conn.commit()
import pandas as pd 

df = pd.read_sql('SELECT * FROM test', engine)
print(df)
