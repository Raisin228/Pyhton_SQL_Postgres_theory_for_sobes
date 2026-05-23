from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    num1: int
    operation: str
    num2: int

    num3: int
    operation2: str
    num4: int

    result: int
    result2: int


def adder(state: AgentState) -> AgentState:
    state["result"] = state["num1"] + state["num2"]
    return state


def adder2(state: AgentState) -> AgentState:
    state["result2"] = state["num3"] + state["num4"]
    return state


def subs(state: AgentState) -> AgentState:
    state["result"] = state["num1"] - state["num2"]
    return state


def subs2(state: AgentState) -> AgentState:
    state["result2"] = state["num3"] - state["num4"]
    return state


def decide_next_node(state: AgentState) -> str:
    if state["operation"] == "+":
        return "addition_operation"
    elif state["operation"] == "-":
        return "subs_operation"


def decide_next_node2(state: AgentState) -> str:
    if state["operation2"] == "+":
        return "addition_operation2"
    elif state["operation2"] == "-":
        return "subs_operation2"


graph = StateGraph(AgentState)

graph.add_node("adder", adder)
graph.add_node("subs", subs)
graph.add_node("adder2", adder2)
graph.add_node("subs2", subs2)

graph.add_node("router", lambda state: state)
graph.add_node("router2", lambda state: state)

graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    decide_next_node,
    {
        "addition_operation": "adder",
        "subs_operation": "subs"
    }
)

graph.add_edge("adder", "router2")
graph.add_edge("subs", "router2")

graph.add_conditional_edges(
    "router2",
    decide_next_node2,
    {
        "addition_operation2": "adder2",
        "subs_operation2": "subs2"
    }
)

graph.add_edge("adder2", END)
graph.add_edge("subs2", END)

app = graph.compile()

res = app.invoke(AgentState(num1=2, operation='+', num2=2, num3=5, operation2='-', num4=7))
print(res)
