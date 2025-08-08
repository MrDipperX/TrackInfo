import pandas as pd
import numpy as np

from sqlalchemy import create_engine
import sqlalchemy as db
from environs import Env

# Environment variables
env = Env()
env.read_env()


DATE_COLS = [
    'date_to_z', 'last_dr', 'last_kr_1', 'last_kr_2',
    'last_kvr', 'planned_write_of_date'
]

INT_COLS = [
    'construction_year', 'assigned_service_life',
    'service_life', 'sleeping_place_count', 'sitting_place_count'
]

FLOAT_COLS = ['wagon_tare']

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    # Стрип строк
    df_obj = df.select_dtypes(include=['object'])
    df[df_obj.columns] = df_obj.apply(lambda s: s.astype(str).str.strip())

    # Псевдо-пустые значения -> NaN
    EMPTY_MARKERS = {"", "—", "-", "NULL", "None", "nan", "NaT"}
    for col in df.columns:
        df[col] = df[col].apply(lambda x: None if (pd.isna(x) or str(x).strip() in EMPTY_MARKERS) else x)

    # Даты: DD.MM.YYYY -> date
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce').dt.date

    # Целые
    for col in INT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            # Чтобы в БД ушли настоящие NULL, заменим <NA> на None
            df[col] = df[col].where(df[col].notna(), None)

    # Float
    for col in FLOAT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].where(df[col].notna(), None)

    return df

def pstgr_engine():

    user = env.str('PSTG_USER')
    password = env.str('PASSWORD')
    host = env.str('HOST')
    dbname = env.str('DBNAME')
    port = env.str('PORT')

    engine = None
    try:
        engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}")

    except Exception as e:
        print(e)

    finally:
        return engine


def from_xlsx_to_df(xlsx_file):
    read_file = pd.read_excel(xlsx_file)

    headers = read_file.iloc[4:, 1:].head(1).squeeze().to_list()
    headers = [str(header).strip() for header in headers]
    content = read_file.iloc[5:, 1:]
    df = pd.DataFrame(content.values, columns=headers)

    new_headers = ['number', 'home_enterprise', 'wagon_type', 'construction_year', 'building_plant',
                   'state_of_use', 'date_to_z', 'last_dr', 'last_kr_1', 'last_kr_2', 'last_kvr',
                   'assigned_service_life', 'service_life', 'planned_write_of_date', 'wagon_model', 'wagon_tare',
                   'body_color', 'sleeping_place_count', 'sitting_place_count', 'far_and_air_condition_system',
                   'generator_type', 'generator_drive_design']
    rename_dict = {old: new for new, old in zip(new_headers, headers)}
    df = df.rename(columns=rename_dict)

    # Нормализация типов и дат
    df = normalize_df(df)
    return df


def create_upsert_method(on_conflict_column: str, schema: str = "public"):
    def method(table, conn, keys, data_iter):
        # table: pandas-given TableClause (имеет .name)
        # conn:  SQLAlchemy Connection
        meta = db.MetaData()  # НЕ передаём engine сюда
        # Рефлектим реальную таблицу из БД
        sql_table = db.Table(table.name, meta, schema=schema, autoload_with=conn)

        values_to_insert = [dict(zip(keys, row)) for row in data_iter]

        insert_stmt = db.dialects.postgresql.insert(sql_table)
        # excluded.<col> для апдейта
        update_stmt = {col.name: getattr(insert_stmt.excluded, col.name) for col in sql_table.columns}

        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[getattr(sql_table.c, on_conflict_column)],  # ВАЖНО: колонку, а не строку-имя
            set_=update_stmt
        )

        # executemany
        conn.execute(upsert_stmt, values_to_insert)
    return method


def upsert(table_name, df, db_engine):
    try:
        upsert_method = create_upsert_method(on_conflict_column="number", schema="public")

        df.to_sql(
            table_name,
            db_engine,
            schema="public",
            if_exists="append",
            index=False,
            method=upsert_method,
            chunksize=200
        )
        return "Upsert was Done"
    except Exception as e:
        print(e)


# def execute_values(xlsx_file: str) -> bool:
#     # "07325392" 28
#     table_name = "track_manage_passengertrack"
#     read_file = pd.read_excel(xlsx_file).fillna("NULL")
#
#     series = [tuple(read_file[key].astype(str).apply(lambda x: x.strip()).tolist()) for key in read_file]
#
#     conn = psycopg2.connect("host=localhost dbname=TrackInfo user=postgres password=Naruhina")
#     cur = conn.cursor()
#
#     cur.execute(f'SELECT * FROM {table_name} LIMIT 0')
#     colnames = [desc[0] for desc in cur.description]
#     cols = tuple(colnames[1:])
#
#     objects_list = []
#     for i in range(len(series[0])):
#         obj = [serie[i] for serie in series]
#         for n, j in enumerate(obj):
#             if j == "NULL":
#                 obj[n] = None
#         objects_list.append(tuple(obj))
#
#     print(objects_list)
#
#     query = sql.SQL("""INSERT INTO {table}({columns})VALUES %s ON CONFLICT({number})
#         DO UPDATE SET ({cols_update}) = ({excluded_cols})""").\
#         format(
#         table=sql.Identifier(table_name),
#         columns=sql.SQL(',').join([sql.Identifier(col) for col in cols]),
#         number=sql.Identifier(cols[0]),
#         cols_update=sql.SQL(',').join([sql.Identifier(col) for col in cols[1:]]),
#         excluded_cols=sql.SQL(',').join([sql.Identifier("excluded", col) for col in cols[1:]])
#                )
#
#     # query = sql.SQL("""INSERT INTO {table}({columns})VALUES %s""").format(
#     #     table=sql.Identifier(table_name),
#     #     columns=sql.SQL(',').join([sql.Identifier(col) for col in cols]))
#     try:
#         extras.execute_values(cur, query, objects_list)
#         conn.commit()
#
#     except (Exception, psycopg2.DatabaseError) as error:
#         print("Error: %s" % error)
#         conn.rollback()
#         cur.close()
#         return False
#     cur.close()
#     return True
