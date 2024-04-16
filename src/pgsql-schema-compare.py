#!/usr/bin/env python3

import argparse
import logging
import re

from collections import defaultdict

logging.basicConfig(level=logging.ERROR)


def parse_file(filename):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')

    # Remove comments and SET statements and empty lines
    lines = [line for line in lines if not line.startswith('--')]
    lines = [line for line in lines if not line.startswith('SET')]
    lines = [line for line in lines if line.strip() != '']

    table_structure = defaultdict(dict)
    table_name = None

    for line in lines:
        if "CREATE TABLE" in line:
            table_name = re.search(r"CREATE TABLE (.*) \(", line).group(1)

        # If the line contains a field definition : a field_name, a field_type and a field_modifier
        # field_modifier should be ignored

        pattern = re.compile(r'\s*(\w+)\s+(\w+).*')
        match = pattern.match(line)
        if match:
            column_name = match.group(1)
            column_type = match.group(2)
            table_structure[table_name][column_name] = column_type

            continue

        if ");" in line and table_name:
            table_name = None

    return table_structure


def compare_schemas(schema1, schema2):
    all_tables = set(list(schema1.keys()) + list(schema2.keys()))
    result = []

    for table in all_tables:
        diff_columns = []
        schema1_columns = schema1.get(table, {})
        schema2_columns = schema2.get(table, {})
        if not schema1_columns and schema2_columns:
            # If table exists in schema2 but not schema1, table was added
            table_added_lines = ["La table entière a été ajoutée avec les paramètres :"]
            for column, column_type in schema2_columns.items():
                table_added_lines.append(f"- Ajout du paramètre `{column}` de type `{column_type}`")
            result.append((table, "\n".join(table_added_lines)))
            continue
        elif schema1_columns and not schema2_columns:
            # If table exists in schema1 but not schema2, table was deleted
            result.append((table,"La table entière a été supprimée"))
            continue

        all_columns = set(list(schema1_columns.keys()) + list(schema2_columns.keys()))
        for column in all_columns:
            # If the field is only in schema1, it was deleted
            if column in schema1_columns and column not in schema2_columns:
                diff_columns.append(f"- Suppression du paramètre `{column}` de type `{schema1_columns[column]}`")
            # If the field is only in schema2, it was added
            elif column not in schema1_columns and column in schema2_columns:
                diff_columns.append(f"- Ajout du paramètre `{column}` de type `{schema2_columns[column]}`")
            # If field type is different in schema1 and schema2, it has been modified
            elif schema1_columns.get(column) != schema2_columns.get(column):
                diff_columns.append(f"- Modification du paramètre `{column}` de `{schema1_columns[column]}` à `{schema2_columns[column]}`")
        if diff_columns:
            result.append((table, "\n".join(diff_columns)))
    
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pgsql-schema-compare', description='Compare two PostgreSQL schemas')
    parser.add_argument('-v', help="verbose mode", action="count")

    parser.add_argument('--source', help="source schema filename", required=True)
    parser.add_argument('--destination', help="target schema filename", required=True)

    args = parser.parse_args()

    if args.v is not None:
        if args.v == 1:
            logging.basicConfig(level=logging.INFO)
        elif args.v > 1:
            logging.basicConfig(level=logging.DEBUG)

    old_schema_filename = args.source
    new_schema_filename = args.destination

    schema1 = parse_file(old_schema_filename)
    schema2 = parse_file(new_schema_filename)

    differences = compare_schemas(schema1, schema2)

    for difference in differences:
        print(difference[0])
        for diff in difference[1].split("\n"):
            print(diff)
