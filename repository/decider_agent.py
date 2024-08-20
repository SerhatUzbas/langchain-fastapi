# class SQLDatabaseAgent:
#     def __init__(self, database_uri):
#         self.db = SQLDatabase.from_uri(database_uri=database_uri)
#         # self.llm = ChatOllama(model="llama3.1", temperature=0.2)
#         self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

#         self.schema_tool = SchemaTool(db=self.db)
#         self.query_tool = QueryTool(llm=self.llm)
#         self.query_checker_tool = QueryCheckerTool(llm=self.llm, db=self.db)
#         self.explanator_tool = ExplanatorTool(
#             llm=self.llm,
#         )

#         self.max_iterations = 5

#     def execute(self, question: str):
#         schema_info, table_names = self.schema_tool.run({})
#         iteration = 0
#         last_error = ""
