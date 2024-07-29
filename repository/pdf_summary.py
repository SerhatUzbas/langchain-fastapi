# from langchain_chroma import Chroma
# from langchain.vectorstores import Chroma
import os
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

repo_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(repo_dir, "../files/bag-stories.pdf")


class PdfSummary:
    # Construct the full path to the PDF file

    _path = os.path.normpath(file_path)

    _llm = ChatOllama(model="llama3")
    _system_prompt = (
        "You are an experienced content creator."
        "Use the following pieces of retrieved context to create a blog post"
        "The content must be interesting,appealed and readable for user."
        "if you do not know about question context, say you don't know and do not request for more information."
        "Your blog post must be two paragraph maximum."
        "answer concise."
        "\n\n"
        "{context}"
    )
    _prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _system_prompt),
            ("human", "{input}"),
        ]
    )

    @classmethod
    def _pdf_extract(cls):
        loader = PyPDFLoader(cls._path)

        docs = loader.load()
        return docs

    @classmethod
    def _embedder_retriever(cls):
        docs = cls._pdf_extract()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(
            documents=splits, embedding=SentenceTransformerEmbeddings()
        )

        retriever = vectorstore.as_retriever()

        return retriever

    @classmethod
    def create_post(cls):
        retriever = cls._embedder_retriever()
        question_answer_chain = create_stuff_documents_chain(cls._llm, cls._prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        results = rag_chain.invoke(
            {
                "input": "Create a blogpost about handbag styles and identities of their owners. "
            }
        )
        # print(results["answer"], "aaaanssssssweeeer")
        return results["answer"]
