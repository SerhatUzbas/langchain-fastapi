from sqlalchemy import text
from lib.database import get_db


def get_table_columns():
    with get_db() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    table_schema,
                    table_name,
                    column_name,
                    data_type
                FROM
                    information_schema.columns
                WHERE
                    table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY
                    table_schema, table_name, ordinal_position;
            """
            )
        )
        columns = result.fetchall()

    return columns


def get_foreign_keys():

    with get_db() as connection:
        result = connection.execute(
            text(
                """
        SELECT
            tc.table_schema, 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY';
        """
            )
        )
        foreign_keys = result.fetchall()

    return foreign_keys


def get_columns_and_foreign_keys():
    columns = get_table_columns()
    foreign_keys = get_foreign_keys()

    columns_dict = {}
    for column in columns:
        schema, table, col, data_type = column
        key = (schema, table)
        if key not in columns_dict:
            columns_dict[key] = []
        columns_dict[key].append(
            {"column_name": col, "data_type": data_type, "foreign_key": None}
        )

    for fk in foreign_keys:
        schema, table, column, foreign_schema, foreign_table, foreign_column = fk
        key = (schema, table)
        if key in columns_dict:
            for col in columns_dict[key]:
                if col["column_name"] == column:
                    col["foreign_key"] = {
                        "foreign_table_schema": foreign_schema,
                        "foreign_table_name": foreign_table,
                        "foreign_column_name": foreign_column,
                    }

    return columns_dict


def format_columns_and_foreign_keys():
    columns_and_fks = get_columns_and_foreign_keys()
    formatted_output = ""
    for (schema, table), cols in columns_and_fks.items():
        formatted_output += f"Table: {schema}.{table}\n"
        for col in cols:
            formatted_output += (
                f"  Column: {col['column_name']}, Data Type: {col['data_type']}"
            )
            if col["foreign_key"]:
                fk = col["foreign_key"]
                formatted_output += f", Foreign Key: {fk['foreign_table_schema']}.{fk['foreign_table_name']}.{fk['foreign_column_name']}"
            formatted_output += "\n"
    return formatted_output
