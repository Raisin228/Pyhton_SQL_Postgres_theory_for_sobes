from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    name: str
    values: List[int]
    operator: Literal["+", "*"]
    result: str


def process_values(state: AgentState) -> AgentState:
    """Handles inputs"""
    match state["operator"]:
        case "+":
            state["result"] = f"HI {state["name"]}, ans is {sum(state["values"])}"
        case "*":
            prod = 1
            for num in state["values"]:
                prod *= num
            state["result"] = f"HI {state["name"]}, ans is {prod}"

    return state


graph = StateGraph(AgentState)
graph.add_node("processor", process_values)
graph.set_entry_point("processor")
graph.set_finish_point("processor")

app = graph.compile()

res = app.invoke({"values": [1, 2, 3, 4], "name": "bob", "operator": "*"})
print(res)
