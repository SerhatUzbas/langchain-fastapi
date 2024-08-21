from langchain_community.chat_models import ChatOllama

from repository.database_rag import SQLDatabaseAgent
from repository.webbase_rag import WebLoaderRag


class DeciderAgent:
    def __init__(self, database_uri):
        self.database_agent = SQLDatabaseAgent(database_uri)
        self.web_agent = WebLoaderRag()
        self.llm = ChatOllama(model="llama3")

    def decide_agent(self, question: str) -> str:
        # Step 1: Use LLM to classify the query or assess its relevance to each agent
        classification_prompt = f"""
        You are an intelligent assistant. Given the question below, classify it into one of two categories: 
        1. Database-related: If the question is more related to library database, users,event details, data queries, SQL, or retrieving structured information from a database.
        2. Web-related: If the question is more related to web content, Q&A, FAQs, or retrieving information from the Rami Library website.
        
        Question: "{question}"
        
        Answer only with "Database" or "Web". No third choice.
        """

        classification_result = self.llm.invoke(input=classification_prompt)
        classification = classification_result.content.strip().lower()
        print(
            classification,
            "classificationclassificationclassificationclassificationclassificationclassificationclassificationclassification",
        )
        if classification == "database":
            return "database"
        elif classification == "web":
            return "web"
        else:
            # Fallback logic if classification is ambiguous or uncertain
            return "both"

    # async def execute(self, question: str):
    #     decision = self.decide_agent(question)
    #     if decision == "database":
    #         return self.database_agent.execute(question)
    #     elif decision == "web":
    #         return await self.web_agent.answer_stream(question)
    #     else:
    #         # If both agents could handle it, run both and combine their results
    #         db_result = self.database_agent.execute(question)
    #         async for web_chunk in self.web_agent.answer_stream(question):
    #             db_result += f"\n\n{web_chunk}"
    #         return db_result

    async def answer_stream(self, question: str):
        decision = self.decide_agent(question)
        if decision == "database":
            yield self.database_agent.execute(question)
        elif decision == "web":
            async for chunk in self.web_agent.answer_stream(question):
                yield chunk
        else:
            # If both agents could handle it, stream results from both
            yield self.database_agent.execute(question)
            async for chunk in self.web_agent.answer_stream(question):
                yield chunk
