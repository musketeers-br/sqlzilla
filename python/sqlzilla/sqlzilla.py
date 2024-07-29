
from sqlalchemy import create_engine

import hashlib

import pandas as pd;

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.docstore.document import Document
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_iris import IRISVector

class SQLZilla:
    def __init__(self, engine, cnx):
        self.engine = engine
        self.cnx = cnx

    def get_table_definitions_array(self, schema, table=None):
        cursor = self.cnx.cursor()

        # Base query to get columns information
        query = """
        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, PRIMARY_KEY, null EXTRA
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
        """
        
        # Parameters for the query
        params = [schema]

        # Adding optional filters
        if table:
            query += " AND TABLE_NAME = %s"
            params.append(table)
        
        # Execute the query
        cursor.execute(query, params)

        # Fetch the results
        rows = cursor.fetchall()
        
        # Process the results to generate the table definition(s)
        table_definitions = {}
        for row in rows:
            table_schema, table_name, column_name, column_type, is_nullable, column_default, column_key, extra = row
            if table_name not in table_definitions:
                table_definitions[table_name] = []
            table_definitions[table_name].append({
                "column_name": column_name,
                "column_type": column_type,
                "is_nullable": is_nullable,
                "column_default": column_default,
                "column_key": column_key,
                "extra": extra
            })

        primary_keys = {}
        
        # Build the output string
        result = []
        for table_name, columns in table_definitions.items():
            table_def = f"CREATE TABLE {schema}.{table_name} (\n"
            column_definitions = []
            for column in columns:
                column_def = f"  {column['column_name']} {column['column_type']}"
                if column['is_nullable'] == "NO":
                    column_def += " NOT NULL"
                if column['column_default'] is not None:
                    column_def += f" DEFAULT {column['column_default']}"
                if column['extra']:
                    column_def += f" {column['extra']}"
                column_definitions.append(column_def)
            if table_name in primary_keys:
                pk_def = f"  PRIMARY KEY ({', '.join(primary_keys[table_name])})"
                column_definitions.append(pk_def)
            table_def += ",\n".join(column_definitions)
            table_def += "\n);"
            result.append(table_def)

        return result

    def get_table_definitions(self, schema, table=None):
        return "\n\n".join(self.get_table_definitions_array(schema=schema, table=table))

    def get_ids_from_string_array(self, array):
        return [str(hashlib.md5(x.encode()).hexdigest()) for x in array]

    def exists_in_db(self, collection_name, id):
        schema_name = "SQLUser"
        
        cursor = self.cnx.cursor()
        query = f"""
        SELECT TOP 1 id
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = %s and TABLE_NAME = %s
        """
        params = [schema_name, collection_name]
        cursor.execute(query, params)
        rows = cursor.fetchall()
        if len(rows) == 0:
            return False

        del cursor, query, params, rows
        
        cursor = self.cnx.cursor()
        query = f"""
        SELECT TOP 1 id
        FROM {collection_name}
        WHERE id = %s
        """
        params = [id]
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return len(rows) > 0

    def filter_not_in_collection(self, collection_name, docs_array, ids_array):
        filtered = [x for x in zip(docs_array, ids_array) if not self.exists_in_db(collection_name, x[1])]
        return list(zip(*filtered)) or ([], [])