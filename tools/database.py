from langchain_core.tools import tool, BaseTool
from langchain_ollama import ChatOllama
from lib.database import get_db
from lib.helpers import format_columns_and_foreign_keys, get_columns_and_foreign_keys
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
from typing import Optional, Type
from pydantic import BaseModel


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
        return "\n".join(schema_info)


class QueryTool(BaseTool):
    name: str = "query_tool"
    description: str = "Creates a SQL query based on the schema information."

    llm: ChatOllama  # Define the LLM as an attribute with type annotation

    class InputSchema(BaseModel):
        question: str
        schema_info: str

    def _run(
        self,
        question: str,
        schema_info: str,
    ) -> str:
        prompt = f"""
        Based on the following schema information:

        {schema_info}

        Create a SQL query to answer the following question:
        {question}
        """

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
            # Attempt to execute the query
            with get_db() as connection:

                result = connection.execute(query)
                return (
                    result.fetchall()
                    if result.returns_rows
                    else "Query executed successfully."
                )

        except Exception as e:
            # If an error occurs, return the error message
            return f"Error: {str(e)}"
