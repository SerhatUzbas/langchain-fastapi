from langchain_community.chat_models import ChatOllama

from repository.database_rag import SQLDatabaseAgent
from repository.webbase_rag import WebLoaderRag


class DeciderAgent:
    def __init__(self, database_uri):
        self.database_agent = SQLDatabaseAgent(database_uri)
        self.web_agent = WebLoaderRag()
        # self.llm = ChatOllama(model="llama3")
        self.llm = ChatOllama(model="llama3")

    def decide_agent(self, question: str) -> str:
        # Step 1: Use LLM to classify the query or assess its relevance to each agent
        classification_prompt = f"""
        You are an intelligent assistant. Given the question below, classify it into one of two categories: 
        1. Database-related: If the question is more related to library database, users,details,event details, data queries, SQL, or retrieving structured information from a database.
        2. FAQ(Frequently Asked Questions): If the question is more like FAQ or more related to library rules, Q&A, FAQs.
        
        Question: "{question}"
        
        Answer only with "database" or "faq". No third choice.
        Remember, if the question likely Frequently asked question, you answer is probably in t 
        """

        classification_result = self.llm.invoke(input=classification_prompt)
        classification = classification_result.content.strip().lower()

        if classification == "database":
            return "database"
        elif classification == "faq":
            return "faq"
        else:
            # Fallback logic if classification is ambiguous or uncertain
            return "both"

    async def answer_stream(self, question: str):

        decision = self.decide_agent(question=question)
        print(decision, "decisiondecisiondecisiondecisiondecisiondecisiondecision")
        if decision == "database":
            print("database")
            async for chunk in self.database_agent.execute(question):
                yield chunk
            # yield self.database_agent.execute(question)
        elif decision == "faq":
            async for chunk in self.web_agent.answer_stream(question):
                yield chunk
        else:
            yield self.database_agent.execute(question)
            async for chunk in self.web_agent.answer_stream(question):
                yield chunk
