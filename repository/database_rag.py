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


class DatabaseRag:

    _database_uri = "postgresql+psycopg2://rami-dev-user:WsGnaS0Ks8cjx@192.168.20.108/rami-service-dev"
    _db = SQLDatabase.from_uri(database_uri=_database_uri)
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

    You have access to the following tables: {table_names}

    If you need to filter on a proper noun, you must ALWAYS first look up the filter value using the "search_proper_nouns" tool!
    Do not try to guess at the proper name - use this function to find similar ones.""".format(
            table_names=_db.get_usable_table_names()
        )
    )

    # _engine = create_engine(_database_uri)

    _llm = ChatOllama(model="llama3.1")

    # _llm = ChatOpenAI(
    #     api_key="ollama",
    #     model="llama3",
    #     base_url="http://localhost:11434/v1",
    # )

    # _llm = OllamaFunctions(model="llama3-groq-tool-use")
    _toolkit = SQLDatabaseToolkit(db=_db, llm=_llm)

    _tools = _toolkit.get_tools()

    _llm = _llm.bind_tools(_tools)

    # _prompt_template = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", _system_message),
    #         ("human", "{input}"),
    #     ]
    # )

    _prompt_template = PromptTemplate(
        input_variables=["question"],
        template="Question: {question}\nSQL query: ",
    )

    # Create the LLM chain with the prompt template
    # _llm_chain = LLMChain(llm=_llm, prompt=_prompt_template)

    _runnable_sequence = _prompt_template | _llm | StrOutputParser()

    # _agent = create_react_agent(tools=_tools, model=_runnable_sequence,messages_modifier=_system_message)

    # _agent = create_react_agent(
    #     tools=_tools,
    #     model=_runnable_sequence,
    #     messages_modifier=_system_message,
    # )
    _agent_executor = create_react_agent(
        _llm, _tools, messages_modifier=_system_message
    )

    # _agent = initialize_agent(tools=_tools, llm=_llm_chain, verbose=True)

    # _agent_executor = AgentExecutor(agent=_agent, tools=_tools, verbose=True)

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
        response = self._agent_executor.invoke(
            {"messages": "How many events will happen on zoom?"}
        )
        print(response)
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
    _database_uri = "postgresql+psycopg2://rami-dev-user:WsGnaS0Ks8cjx@192.168.20.108/rami-service-dev"
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
