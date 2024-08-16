from sqlalchemy import create_engine
import hashlib
import pandas as pd;
import re

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.docstore.document import Document
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_iris import IRISVector

class SQLZilla:
    def __init__(self, connection_string, openai_api_key):
        self.log('SQLZilla created')
        self.openai_api_key = openai_api_key
        self.schema_name = None
        self.engine = create_engine(connection_string)
        self.conn_wrapper = self.engine.connect()
        self.connection = self.conn_wrapper.connection
        self.log('connection opened')
        self.context = {}
        self.context["top_k"] = 3
        self.tables_vector_store = None
        self.example_selector = None
        self.chain_model = None
        self.example_prompt = None
        self.create_chain_model()

    def create_examples_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS sqlzilla.examples (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                prompt VARCHAR(255) NOT NULL,
                query VARCHAR(255) NOT NULL,
                schema_name VARCHAR(255) NOT NULL
            );
        """
        self.execute_query(sql)
    
    def get_examples(self):
        sql = "SELECT prompt, query FROM sqlzilla.examples WHERE schema_name = %s"
        self.log('sql: ' + sql)
        self.log('params: ' + str([self.schema_name]))
        rows = self.execute_query(sql, [self.schema_name])
        examples = [{
                "input": row[0], 
                "query": row[1]
            } for row in rows]
        return examples
    
    def add_example(self, prompt, query):
        sql = "INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES (%s, %s, %s)"
        self.execute_query(sql, [prompt, query, self.schema_name])

    def __del__(self):
        self.log('SQLZilla deleted')
        if not self.connection is None:
            self.log('connection closed')
            self.connection.close()
        if not self.engine is None:
            self.engine.dispose()

    def log(self, msg):
        import os
        os.write(1, f"{msg}\n".encode())

    def get_table_definitions_array(self, schema, table=None):
        cursor = self.connection.cursor()

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
        
        cursor = self.connection.cursor()
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
        
        cursor = self.connection.cursor()
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

    def schema_context_management(self, schema):
        if self.tables_vector_store is None:
            table_def = self.get_table_definitions_array(schema)
            self.table_df = pd.DataFrame(data=table_def, columns=["col_def"])
            self.table_df["id"] = self.table_df.index + 1
            loader = DataFrameLoader(self.table_df, page_content_column="col_def")
            documents = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=20, separator="\n")
            self.tables_docs = text_splitter.split_documents(documents)
            self.log('schema_name: ' + str(self.schema_name))
            collection_name_tables = "sql_tables_"+self.schema_name
            new_tables_docs, tables_docs_ids = self.filter_not_in_collection(
                collection_name_tables, 
                self.tables_docs, 
                self.get_ids_from_string_array([x.page_content for x in self.tables_docs])
            )
            self.tables_docs_ids = tables_docs_ids
            self.tables_vector_store = IRISVector.from_documents(
                embedding = OpenAIEmbeddings(openai_api_key=self.openai_api_key), 
                documents = self.tables_docs,
                connection=self.conn_wrapper,
                collection_name=collection_name_tables,
                ids=self.tables_docs_ids
            )
        
        if self.example_selector is None:
            examples = self.get_examples()
            collection_name_examples = "sql_samples_"+self.schema_name
            new_sql_samples, sql_samples_ids = self.filter_not_in_collection(
                collection_name_examples, 
                examples, 
                self.get_ids_from_string_array([x['input'] for x in examples])
            )
            self.example_selector = SemanticSimilarityExampleSelector.from_examples(
                new_sql_samples,
                OpenAIEmbeddings(openai_api_key=self.openai_api_key),
                IRISVector,
                k=5,
                input_keys=["input"],
                connection=self.conn_wrapper,
                collection_name=collection_name_examples,
                ids=sql_samples_ids
            )

    def create_chain_model(self):
        if not self.chain_model is None:
            return self.chain_model
        
        iris_sql_template = """
You are an InterSystems IRIS expert. Given an input question, first create a syntactically correct InterSystems IRIS query to run and return the answer to the input question.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the TOP clause as per InterSystems IRIS. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in single quotes ('') to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use CAST(CURRENT_DATE as date) function to get the current date, if the question involves "today".
Use double quotes to delimit columns identifiers.
Return just plain SQL; don't apply any kind of formatting.
        """
        tables_prompt_template = """
        Only use the following tables:
        {table_info}
        """
        prompt_sql_few_shots_template = """
        Below are a number of examples of questions and their corresponding SQL queries.

        {examples_value}
        """
        example_prompt_template = "User input: {input}\nSQL query: {query}"
        example_prompt = PromptTemplate.from_template(example_prompt_template)
        self.example_prompt = example_prompt

        user_prompt = "\n"+example_prompt.invoke({"input": "{input}", "query": ""}).to_string()
        prompt = (
            ChatPromptTemplate.from_messages([("system", iris_sql_template)])
            + ChatPromptTemplate.from_messages([("system", tables_prompt_template)])
            + ChatPromptTemplate.from_messages([("system", prompt_sql_few_shots_template)])
            + ChatPromptTemplate.from_messages([("human", user_prompt)])
        )

        model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=self.openai_api_key)
        output_parser = StrOutputParser()
        self.chain_model = prompt | model | output_parser
    
    def prompt(self, input):
        self.context["input"] = input

        relevant_tables_docs = self.tables_vector_store.similarity_search(input)
        relevant_tables_docs_indices = [x.metadata["id"] for x in relevant_tables_docs]
        indices = self.table_df["id"].isin(relevant_tables_docs_indices)
        relevant_tables_array = [x for x in self.table_df[indices]["col_def"]]
        self.context["table_info"] = "\n\n".join(relevant_tables_array)

        self.context["examples_value"] = "\n\n".join([
            self.example_prompt.invoke(x).to_string() for x in self.example_selector.select_examples({"input": self.context["input"]})
        ])

        self.log(self.context)

        response = self.create_chain_model().invoke({
            "top_k": self.context["top_k"],
            "table_info": self.context["table_info"],
            "examples_value": self.context["examples_value"],
            "input": self.context["input"]
        })
        return response

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        # Execute the query
        cursor.execute(query, params)

        if re.search(r"\s*SELECT\s+", query, re.IGNORECASE):
            # Fetch the results
            return cursor.fetchall()
        elif re.search(r"\s*INSERT\s+", query, re.IGNORECASE):
            self.connection.commit()
        elif re.search(r"\s*UPDATE\s+", query, re.IGNORECASE):
            self.connection.commit()
        elif re.search(r"\s*DELETE\s+", query, re.IGNORECASE):
            self.connection.commit()
        return None
