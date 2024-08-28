import pandas as pd
import asyncio

from langchain.chains import LLMChain
from llm.scripts.model_creation import initialize_model

# 전역 변수로 모델과 체인을 저장
first_chain, chains, scorechain, final_chain = None, None, None, None


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


async def execute_final_chain(dp, first_chain, chains, scorechain, final_chain):
    summary = await first_chain.ainvoke(dp)
    results = await asyncio.gather(*[chain.ainvoke(summary) for chain in chains])
    score = await scorechain.abatch([{"data": i} for i in results])
    consen = await final_chain.ainvoke(results)
    final = await scorechain.ainvoke({"data": consen})
    df = (
        str(summary)
        + str(["{}{}".format(b_, a_) for a_, b_ in zip(results, score)])
        + str(final)
    )
    return df


async def run_model(dp, first_chain, chains, scorechain, final_chain):
    return await execute_final_chain(dp, first_chain, chains, scorechain, final_chain)


# 텍스트 파일 처리 함수
def process_text(file_content):
    print("Processing text file", file_content)
    # 전역 변수에서 초기화된 체인을 사용
    global first_chain, chains, scorechain, final_chain
    dfs = asyncio.run(
        run_model(file_content, first_chain, chains, scorechain, final_chain)
    )
    # 결과를 JSON 형태로 통합
    return str(dfs)


# 웹 서버 시작 시 모델 초기화
def initialize():
    global first_chain, chains, scorechain, final_chain
    first_chain, chains, scorechain, final_chain = initialize_model()


# 웹 서버 시작 시 호출
initialize()
