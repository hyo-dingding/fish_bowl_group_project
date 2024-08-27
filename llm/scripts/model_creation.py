from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, DirectoryLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
import glob
import os
import pathlib


def load_environment():
    load_dotenv()


def load_documents():
    from langchain_core.documents import Document

    path = pathlib.Path().resolve()
    fraud_files = glob.glob(os.path.join(path, "csv_fraud/*.csv"))
    normal_files = glob.glob(os.path.join(path, "csv_normal/*.csv"))

    def load_and_transform_csv(files, role_mapping):
        documents = []
        for filename in files:
            df = pd.read_csv(filename, index_col=None, header=0)
            df["Role"] = df["Role"].map(role_mapping)
            text = "\n".join(
                [f"{row['Role']}: {row['Dialogue']}" for _, row in df.iterrows()]
            )
            document = Document(page_content=text, metadata={"source": filename})
            documents.append(document)
        return documents

    role_mapping_fraud = {"사기범": "A", "피해자": "B"}
    document_csv = load_and_transform_csv(fraud_files, role_mapping_fraud)

    role_mapping_normal = {"상담사": "A", "고객": "B"}
    document_csv_normal = load_and_transform_csv(normal_files, role_mapping_normal)

    loader_pdf = DirectoryLoader("pdf", glob="*.pdf", loader_cls=PyMuPDFLoader)
    document_pdf = loader_pdf.load()

    return document_csv, document_csv_normal, document_pdf


def add_metadata(document_csv, document_csv_normal):
    for doc in document_csv:
        doc.metadata["category"] = "fraud"
    for doc in document_csv_normal:
        doc.metadata["category"] = "non-fraud"


def combine_documents(document_csv, document_csv_normal):
    return document_csv + document_csv_normal


def initialize_components():
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    embeddings = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")
    llm = AzureChatOpenAI(deployment_name="gpt-4o", temperature=0)
    return text_splitter, embeddings, llm


def file_to_retriever(doc, text_splitter, embeddings):
    split_documents = text_splitter.split_documents(doc)
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
    retriever = vectorstore.as_retriever()
    return retriever


def create_prompts():
    prompt1 = PromptTemplate.from_template(
        "You are an assistant for fraud detection tasks. Use the following pieces of retrieved 'context' using the 'data'. The data summarizes a recording of a portion of a call and classifies it as fraud or not through rough classification. Use your judgment and rough classification as appropriate to achieve the task. Label and reason message from a user with an intent whether to fraud or not. Advertising is not fraud. Answer in Korean. #Data:{data} #Context:{context} #Answer:"
    )
    prompt3 = PromptTemplate.from_template(
        "You are an expert assistant in fraud detection. Using the 'data', use the following pieces of retrieved 'context' using the 'data'. The data summarizes a recording of a portion of a call and classifies it as fraud or not through rough classification. Use your judgment and rough classification as appropriate to achieve the task. Provide the label ('fraudulent' or 'non-fraudulent'), reasoning, relevant keywords. Answer in Korean. #Data:{data} #Context:{context} #Answer:"
    )
    prompt4 = PromptTemplate.from_template(
        "You are an assistant trained in recognizing fraud patterns. Use the following pieces of retrieved 'context' using the 'data'. The data summarizes a recording of a portion of a call and classifies it as fraud or not through rough classification. Use your judgment and rough classification as appropriate to achieve the task. Examine the context for any recurring behaviors, language patterns, or anomalies typically associated with fraudulent activities. Summarize your findings and label the intent as 'fraudulent' or 'non-fraudulent'. Answer in Korean, highlighting any suspicious patterns you identify. #Data:{data} #Context:{context} #Answer:"
    )
    prompt5 = PromptTemplate.from_template(
        "You are an assistant focused on detecting potentially fraudulent actions. Use the following pieces of retrieved 'context' using the 'data'. The data summarizes a recording of a portion of a call and classifies it as fraud or not through rough classification. Use your judgment and rough classification as appropriate to achieve the task. Analyze the context to detect if the user is being directed to install software, visit a specific website, or move to a different physical or online location. Such actions can be indicators of fraudulent intent. Label the intent as 'fraudulent' or 'non-fraudulent', and provide a clear explanation along with relevant keywords. Answer in Korean. #data:{data} #Context:{context} #Answer:"
    )
    prompt6 = PromptTemplate.from_template(
        "You are an assistant specialized in evaluating the trustworthiness of online interactions. Use the following pieces of retrieved 'context' using the 'data'. The data summarizes a recording of a portion of a call and classifies it as fraud or not through rough classification. Use your judgment and rough classification as appropriate to achieve the task. Assess the given context to determine whether the message or action appears suspicious or untrustworthy. Consider the tone, language, and content of the message. Label the intent as 'fraudulent' or 'non-fraudulent', and provide reasoning along with relevant keywords. Answer in Korean. #Data:{data} #Context:{context} #Answer:"
    )
    prompt7 = PromptTemplate.from_template(
        "You are an assistant trained in detecting fraudulent intent based on urgency or pressure tactics. Use the following pieces of retrieved 'context' using the 'data'. The data summarizes a recording of a portion of a call and classifies it as fraud or not through rough classification. Use your judgment and rough classification as appropriate to achieve the task. Evaluate the context to see if there are any signs of urgency or pressure being applied to the user to make quick decisions or take immediate action. Such tactics are often associated with fraud. Label the intent as 'fraudulent' or 'non-fraudulent', and explain your reasoning along with relevant keywords. Answer in Korean. #Data:{data} #Context:{context} #Answer:"
    )
    prompt8 = PromptTemplate.from_template(
        "You are an assistant for fraud detection tasks. The context given below is the fraud/non-fraud types you categorized before. Please organize and analyze the content given below and make a final conclusion. Label the intent as 'fraudulent' or 'non-fraudulent', and explain your reasoning along with relevant keywords. Answer in Korean. #Context:{context} #Answer:"
    )
    return [prompt1, prompt3, prompt4, prompt5, prompt6, prompt7, prompt8]


def create_chain(retriever, prompt, llm, retriever_type):
    def _type_filter(ebt):
        return ebt.metadata["category"]

    def type_filter(retriever):
        return [_type_filter(ent) for ent in retriever]

    if retriever_type == "csv":
        chain = (
            {
                "context": retriever,
                "data": RunnablePassthrough(),
                "category": retriever | RunnableLambda(type_filter),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
    elif retriever_type == "pdf":
        chain = (
            {"context": retriever, "data": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
    return chain


def additional_data_processing():
    path = pathlib.Path().resolve()
    all_files_fraud = glob.glob(os.path.join(path, "test/csv_fraud/*.csv"))
    dp_fraud = []
    for filename in all_files_fraud:
        df = pd.read_csv(filename, index_col=None, header=0)
        df["Role"] = df["Role"].map({"사기범": "A", "피해자": "B"})
        dp_fraud.append(df)

    all_files_normal = glob.glob(os.path.join(path, "test/csv_normal/*.csv"))
    dp_normal = []
    for filename in all_files_normal:
        df = pd.read_csv(filename, index_col=None, header=0)
        df["Role"] = df["Role"].map({"상담사": "A", "고객": "B"})
        dp_normal.append(df)

    return dp_fraud, dp_normal


def setup_classifier(llm):
    class Classifier(BaseModel):
        description: str = Field(
            description="Classifications of fraud/non-fraud. If it's fraudulent, it's classified as 'fraud' and if it's non-considered, it's classified as 'non'"
        )
        keyword: str = Field(description="Keywords in succinct format (at least two)")
        score: int = Field(
            description="a measure to classify whether it is fraud or not.Put it on a scale from 0 to 10"
        )

    parser = JsonOutputParser(pydantic_object=Classifier)
    prompt11 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an AI assistant who must identify fraud. Answer the questions succinctly.",
            ),
            ("user", "#Format: {format_instructions}\n\n#Data: {data}"),
        ]
    )
    prompt11 = prompt11.partial(format_instructions=parser.get_format_instructions())
    return prompt11 | llm | parser


def initialize_model():
    load_environment()
    document_csv_fraud, document_csv_normal, document_pdf = load_documents()
    add_metadata(document_csv_fraud, document_csv_normal)
    document_csv = combine_documents(document_csv_fraud, document_csv_normal)
    text_splitter, embeddings, llm = initialize_components()
    retriever_csv = file_to_retriever(document_csv, text_splitter, embeddings)
    retriever_pdf = file_to_retriever(document_pdf, text_splitter, embeddings)
    prompts = create_prompts()
    first_chain = create_chain(retriever_csv, prompts[0], llm, "csv")
    chains = [create_chain(retriever_pdf, prmt, llm, "pdf") for prmt in prompts[1:]]
    scorechain = setup_classifier(llm)
    final_chain = (
        {"context": RunnablePassthrough()} | prompts[-1] | llm | StrOutputParser()
    )
    return first_chain, chains, scorechain, final_chain
