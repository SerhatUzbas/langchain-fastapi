import os
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import SQLDatabaseToolkit

# from langchain_community.chat_models import ChatOllama

from langchain_ollama import ChatOllama
from langchain_experimental.llms.ollama_functions import OllamaFunctions

from langchain.agents import AgentExecutor, initialize_agent
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI


# from langchain_core.runnables import RunnableSequence
from langchain.chains import create_sql_query_chain

from lib.helpers import (
    format_columns_and_foreign_keys,
    get_columns_and_foreign_keys,
    get_foreign_keys,
)

SQLALCHEMY_DATABASE_URL = os.environ["SQLALCHEMY_DATABASE_URL"]


class DatabaseAgentRag:

    _database_uri = SQLALCHEMY_DATABASE_URL
    _db = SQLDatabase.from_uri(database_uri=_database_uri)
    _columns_and_fks = get_columns_and_foreign_keys()
    _formatted_output = format_columns_and_foreign_keys(_columns_and_fks)
    _system_message = SystemMessage(
        content="""You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct Postgresql query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the given tools. Only use the information returned by the tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    DO NOT give sql query as a result. Your result must be sql query result.
    
    # You have access to the following tables: {table_names}
    # Tables relations are: {tables_relations}
    
    """.format(
            table_names=_db.get_usable_table_names(),
            tables_relations=_formatted_output,
        ),
    )

    _llm = ChatOllama(model="llama3.1")

    _toolkit = SQLDatabaseToolkit(db=_db, llm=_llm)

    _tools = _toolkit.get_tools()

    _llm = _llm.bind_tools(_tools)

    _prompt_template = PromptTemplate(
        input_variables=["question"],
        template="Question: {question}\nSQL query: ",
    )

    _runnable_sequence = _prompt_template | _llm | StrOutputParser()

    _agent_executor = create_react_agent(
        _llm, _tools, messages_modifier=_system_message
    )

    input_query = "How many events in event table?"

    @classmethod
    def execute(self):
        # print(self._toolkit, "_toolkit")
        # print(self._tools, "_tools")
        # print(self._llm, "_llm")
        # print(self._llm_chain, "_llm_chain")
        # print(self._agent, "_agent")
        # return
        # print(self._tools, "toools")
        # print(self._agent_executor, "_agent_executor")
        # print(self._toolkit, "toolkits")

        # response = self._agent_executor.invoke(
        #     {"messages": "How many events will happen on november 2023?"}
        # )
        # print(response)
        print(self._formatted_output)

        # print(self._formatted_output)
        # for s in self._agent_executor.stream(
        #     {
        #         "messages": [
        #             HumanMessage(content="Which country's customers spent the most?")
        #         ]
        #     }
        # ):
        #     print(s)
        #     print("----")


class DatabaseChainRag:
    _database_uri = SQLALCHEMY_DATABASE_URL
    _db = SQLDatabase.from_uri(database_uri=_database_uri)

    # _engine = create_engine(_database_uri)

    _llm = ChatOllama(model="llama3")

    _prompt_template = PromptTemplate(
        input_variables=["question"],
        template="Question: {question}\nSQL query: ",
    )

    input_query = "How many events in event table?"

    chain = create_sql_query_chain(_llm, _db)

    @classmethod
    def execute(self):
        # print(self._toolkit, "_toolkit")
        # print(self._tools, "_tools")
        # print(self._llm, "_llm")
        # print(self._llm_chain, "_llm_chain")
        # print(self._agent, "_agent")
        # return
        # print(self._tools, "toools")
        # print(self._agent_executor, "_agent_executor")
        # print(self._toolkit, "toolkits")
        # response = self.chain.invoke({"question": self.input_query})
        # print(self._db.get_usable_table_names())
        print(self._db.get_context())
        # print(response)
