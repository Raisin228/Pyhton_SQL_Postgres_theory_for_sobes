import random
from typing import TypedDict, List

from langgraph.graph import START, END, StateGraph


class AgentState(TypedDict):
    player_name: str
    guesses: List[int]
    attempts: int
    lower_bound: int
    upper_bound: int
    hint: str


def setup_bounds(state: AgentState) -> AgentState:
    state["guesses"] = []
    state["attempts"] = 0
    state["hint"] = ""

    state["lower_bound"] = int(input("Введите нижнюю границу: "))
    state["upper_bound"] = int(input("Введите верхнюю границу: "))

    print(
        f"Границы := "
        f"{state['lower_bound']}, {state['upper_bound']}"
    )

    return state


def guess(state: AgentState) -> AgentState:
    # Обновляем границы на основе прошлого ответа
    if state["guesses"] and state["hint"]:
        last_guess = state["guesses"][-1]

        if state["hint"] == "б":
            state["lower_bound"] = last_guess + 1

        elif state["hint"] == "м":
            state["upper_bound"] = last_guess - 1

    print(
        f"\nТекущие границы: "
        f"{state['lower_bound']} - {state['upper_bound']}"
    )

    # Защита от некорректных границ
    if state["lower_bound"] > state["upper_bound"]:
        print("Вы где-то обманули меня с подсказками 😭")
        return state

    num = random.randint(
        state["lower_bound"],
        state["upper_bound"]
    )

    state["guesses"].append(num)
    state["attempts"] += 1

    return state


def hint_node(state: AgentState) -> str:
    print(f"Я думаю вы загадали число := {state['guesses'][-1]}")

    is_correct = input("Это так [Да, Нет]: ").strip().lower()

    if is_correct == "да":
        print(
            f"Ура! Я угадал число "
            f"за {state['attempts']} попыток 🎉"
        )
        return "exit"

    if state["attempts"] >= 7:
        print("Я проиграл хозяин(")
        return "exit"

    state["hint"] = input("Число [б|м]? ").strip().lower()

    return "continue"


graph = StateGraph(AgentState)

# Узлы
graph.add_node("setup", setup_bounds)
graph.add_node("guesser", guess)
graph.add_node("router", lambda state: state)

# Переходы
graph.add_edge(START, "setup")
graph.add_edge("setup", "guesser")
graph.add_edge("guesser", "router")

# Цикл
graph.add_conditional_edges(
    "router",
    hint_node,
    {
        "continue": "guesser",
        "exit": END
    }
)

app = graph.compile()

app.invoke(
    AgentState(
        player_name="Bogdan"
    )
)