import pandas as pd

from sqlalchemy import create_engine
import sqlalchemy as db


def pstgr_engine():
    user = "postgres"
    password = "Naruhina"
    host = "localhost"
    dbname = "TrackInfo"
    port = "5432"

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
    headers = [header.strip() for header in headers]

    content = read_file.iloc[5:, 1:]

    main_df = pd.DataFrame(content.values, columns=headers)

    new_headers = ['number', 'home_enterprise', 'wagon_type', 'construction_year', 'building_plant',
                   'state_of_use', 'date_to_z', 'last_dr', 'last_kr_1', 'last_kr_2', 'last_kvr',
                   'assigned_service_life', 'service_life', 'planned_write_of_date', 'wagon_model', 'wagon_tare',
                   'body_color', 'sleeping_place_count', 'sitting_place_count', 'far_and_air_condition_system',
                   'generator_type', 'generator_drive_design']

    rename_dict = {old: new for new, old in zip(new_headers, headers)}

    main_df = main_df.rename(columns=rename_dict)

    df_obj = main_df.select_dtypes(['object'])

    main_df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

    return main_df


def create_upsert_method(meta: db.MetaData, on_conflict_column):
    def method(table, conn, keys, data_iter):
        sql_table = db.Table(table.name, meta, autoload=True)

        values_to_insert = [dict(zip(keys, data)) for data in data_iter]

        insert_stmt = db.dialects.postgresql.insert(sql_table, values_to_insert)

        update_stmt = {exc_k.key: exc_k for exc_k in insert_stmt.excluded}

        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[on_conflict_column],  # index elements are primary keys of a table
            set_=update_stmt  # the SET part of an INSERT statement
        )

        conn.execute(upsert_stmt)

    return method


def upsert(table_name, df, db_engine):
    try:
        meta = db.MetaData(db_engine)
        table_name = table_name
        upsert_method = create_upsert_method(meta, "number")

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
        return "Fail" + str(e)



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
