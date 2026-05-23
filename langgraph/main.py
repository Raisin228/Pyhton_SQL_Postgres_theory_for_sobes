from typing import TypedDict, Annotated
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    """State schema for graph"""

    message: Annotated[str, lambda a, b: b]


def greeting_node(state: AgentState) -> AgentState:
    """
    Simple node that adds greeting msg to the state

    :param state:
    :return:
    """

    state['message'] = f"{state['message']}, you doing amazing job learning"
    return state


graph = StateGraph(AgentState)

graph.add_node("greeter", greeting_node)
graph.set_entry_point("greeter")
graph.set_finish_point("greeter")

app = graph.compile()

result = app.invoke({"message": "Bob"})
print(result['message'])
