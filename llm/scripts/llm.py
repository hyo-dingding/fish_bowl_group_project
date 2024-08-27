import pandas as pd

from langchain.chains import LLMChain
from llm.scripts.model_creation import initialize_model


# 파일에서 텍스트 추출 함수
def extract_text_from_csv(file_content):
    df = pd.read_csv(file_content)
    text_content = " ".join(
        df.apply(lambda x: " ".join(x.dropna().astype(str)), axis=1)
    )
    return text_content


# CSV 파일 처리 함수
def process_csv(file_content):
    print("Processing CSV file", file_content)
    text_content = extract_text_from_csv(file_content)
    return process_text(text_content)


def execute_final_chain(dp, first_chain, chains, scorechain, final_chain):
    df = []
    summary = first_chain.invoke(dp)
    results = []
    for chain in chains:
        res = chain.invoke(summary)
        results.append(res)
        score = scorechain.invoke({"data": res})
        df.append(score)
    consen = final_chain.invoke(results)
    df.append(scorechain.invoke({"data": consen}))

    return df


def initialize():
    return initialize_model()


def run_model(dp_fraud, first_chain, chains, scorechain, final_chain):
    return execute_final_chain(dp_fraud, first_chain, chains, scorechain, final_chain)


# 텍스트 파일 처리 함수
def process_text(file_content):
    print("Processing text file", file_content)
    # 각 체인에서의 결과를 가져옴
    first_chain, chains, scorechain, final_chain = initialize()
    dfs = run_model(file_content, first_chain, chains, scorechain, final_chain)
    # 결과를 JSON 형태로 통합

    return str(dfs)
