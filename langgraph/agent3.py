from typing import TypedDict, List
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    name: str
    age: str
    skills: List[str]
    final: str


def first_node(state: AgentState) -> AgentState:
    state["final"] = f"{state["name"]}, welcome!"
    return state


def second_node(state: AgentState) -> AgentState:
    state["final"] = state["final"] + f" You are {state["age"]}!"
    return state


def third_node(state: AgentState) -> AgentState:
    state["final"] = state["final"] + f" Your skills is: {', '.join(state["skills"])}"
    return state


graph = StateGraph(AgentState)
graph.add_node("greeting", first_node)
graph.add_node("age", second_node)
graph.add_node("skills", third_node)
graph.set_entry_point("greeting")

graph.add_edge("greeting", "age")
graph.add_edge("age", "skills")
graph.set_finish_point("skills")

app = graph.compile()

res = app.invoke({"name": "Bob", "age": 21, "skills": ["Python", "ML"]})
print(res["final"])
