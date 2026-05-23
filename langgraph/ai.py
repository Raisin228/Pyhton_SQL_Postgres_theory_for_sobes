from typing import TypedDict, List, Union

from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph

LLM = ChatOllama(base_url="http://localhost:11434", model="qwen2.5:1.5b", temperature=0, num_predict=4096)


class AgentState(TypedDict):
    msgs: List[Union[HumanMessage, AIMessage]]


def process(state: AgentState) -> AgentState:
    response = LLM.invoke(state["msgs"])
    state["msgs"].append(AIMessage(content=response.content))
    print(f"AI: {response.content}")
    return state


graph = StateGraph(AgentState)

# Узлы
graph.add_node("answer_question", process)

graph.add_edge(START, "answer_question")
graph.add_edge("answer_question", END)

app = graph.compile()

conv_history = []
while True:
    usr_quest = input("Ваш запрос: ")
    if usr_quest == "e":
        break
    conv_history.append(HumanMessage(content=usr_quest))
    app.invoke(AgentState(msgs=conv_history))

