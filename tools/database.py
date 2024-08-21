from langchain_core.tools import tool, BaseTool
from langchain_openai import ChatOpenAI
from sqlalchemy import text
from lib.database import get_db
from langchain_community.utilities import SQLDatabase
from pydantic import BaseModel, Field
import json


class Joke(BaseModel):
    message: str = Field(description="explanation of postgresql query")
    query: str = Field(description="postgresql query")


class SchemaTool(BaseTool):
    name: str = "schema_tool"
    description: str = (
        "Retrieves the schema information including tables, columns, and keys from the database."
    )

    db: SQLDatabase  # Declare the db field with type annotation

    class InputSchema(BaseModel):
        pass  # No input required to get the schema

    def _run(self) -> str:
        # Retrieve tables, columns, and keys
        tables = self.db.get_table_names()
        schema_info = []
        for table in tables:
            schema_info.append(self.db.get_table_info_no_throw([table]))
        return "\n".join(schema_info), tables


class QueryTool(BaseTool):
    name: str = "query_tool"
    description: str = "Creates a SQL query based on the schema information."

    llm: ChatOpenAI  # Define the LLM as an attribute with type annotation

    class InputSchema(BaseModel):
        question: str
        schema_info: str
        tables: str

    def _run(self, question: str, schema_info: str, tables: str, error: str) -> str:
        prompt = f"""
        You are an agent designed to interact with a SQL database of Rami Library.
        Then, Given an input question, create a syntactically correct Postgresql query to run.
        Remember, table names always starts with public in postgres (e.g. public.libraries).
        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
        To start you should ALWAYS look at the schema information  to see what you can query.
        Do NOT skip this step.
        DO NOT make any any extra explanation. You SHOULD only give postgresql query.
        Table names: {tables}
        Schema information: {schema_info}
        Create a SQL query to answer the following question: {question}

        If there is an error from your last query, it is : {error} 

        Please return the output in the following JSON format but do not write json:
        {{
            "message": "<A brief message about the query generation>",
            "query": "<The generated SQL query>"
        }}
        Do not make any explanations, You must return only JSON.
        """

        if error:
            prompt += f"\n\nPreviously encountered error: {error}"

        response = self.llm.invoke(input=prompt)
        content = response.content

        return content.strip()


class QueryCheckerTool(BaseTool):
    name: str = "query_checker_tool"
    description: str = "Checks the correctness of a SQL query and attempts to run it."

    db: SQLDatabase  # SQL database object to execute the query

    class InputSchema(BaseModel):
        query: str

    def _run(self, query: str) -> str:
        try:
            print(query)
            query_data = json.loads(query)
            print(query_data, "contentntntntntntntntntntn")
            sql_query = query_data.get("query")

            if not sql_query:
                return "Error: No query found in the input JSON."
            # Attempt to execute the query
            with get_db() as connection:

                result = connection.execute(text(sql_query))
                return (
                    result.fetchall()
                    if result.returns_rows
                    else "Query executed successfully."
                )
        except Exception as e:
            # If an error occurs, return the error message
            return f"Error: {str(e)}"


class ExplanatorTool(BaseTool):
    name: str = "explanator_tool"
    description: str = "Return to the user the best message through user request."

    llm: ChatOpenAI  # Define the LLM as an attribute with type annotation

    class InputSchema(BaseModel):
        question: str
        sql_query_result: str

    async def _run(self, question: str, sql_query_result: str):
        prompt = f"""
        You are an agent responsible from return best message to user througs its question.
        You will have the user question, sql query result.
        Your message MUST be easy to read, understandable from user, clean and direct.
        "Make sure to include <h2> tags for titles, <h3> tags for subtitles, <p> tags for paragraphs,"
        "<b> tags for bold text, and <br> tags for line breaks. Separate paragraphs, titles and list items with a blank line."
        "Titles must be bold and 20px, subtitles must be bold and 18px, paragraphs must be 16px."
        
        User question: {question}
        Sql query result: {sql_query_result}

        Do not make any extra explanation. Only give an answer for the question.
        """

        # response = self.llm.invoke(input=prompt)
        # content = response.content
        # return content.strip()

        async for chunk in self.llm.astream(input=prompt):
            yield chunk.content
