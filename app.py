import math
from typing import Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import streamlit as st

from solver_engine import generate_puzzle, is_valid_transfer, to_barycentric

TARGET = 8
MAX_MOVES = 20


def _heuristic(state: Sequence[int], capacities: Sequence[int]) -> float:
    """Measure distance to the closest projected state containing the target."""
    x, y = to_barycentric(state)
    goal_points = [
        to_barycentric(
            tuple(TARGET if index == bucket else 0 for index in range(len(state)))
        )
        for bucket, capacity in enumerate(capacities)
        if TARGET <= capacity
    ]
    if not goal_points:
        return float("inf")
    return min(math.hypot(x - goal_x, y - goal_y) for goal_x, goal_y in goal_points)


def _draw_simplex(
    capacities: Sequence[int],
    history: Sequence[Tuple[int, ...]],
    solution: Sequence[Tuple[int, ...]],
    show_hint: bool,
) -> plt.Figure:
    """Plot the bucket-space boundary and the player's path."""
    count = len(capacities)
    vertices = [
        (
            capacity * math.cos(2 * math.pi * index / count),
            capacity * math.sin(2 * math.pi * index / count),
        )
        for index, capacity in enumerate(capacities)
    ]

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.add_patch(
        Polygon(vertices, closed=True, fill=False, edgecolor="#64748b", linewidth=2)
    )

    trajectory = [to_barycentric(state) for state in history]
    ax.plot(
        [point[0] for point in trajectory],
        [point[1] for point in trajectory],
        color="#2563eb",
        marker="o",
        linewidth=2,
        label="Your moves",
    )

    if show_hint and solution:
        hint_path = [to_barycentric(state) for state in solution]
        ax.plot(
            [point[0] for point in hint_path],
            [point[1] for point in hint_path],
            color="#16a34a",
            marker="o",
            linestyle="--",
            linewidth=2,
            label="DFS hint",
        )

    for index, (x, y) in enumerate(vertices):
        ax.annotate(
            f"Bucket {index + 1}",
            (x, y),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=9,
        )

    ax.set_title("Your water-transfer journey")
    ax.set_xlabel("Barycentric x")
    ax.set_ylabel("Barycentric y")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(alpha=0.2)
    if show_hint and solution:
        ax.legend()
    fig.tight_layout()
    return fig

st.set_page_config(page_title="Water Jug Puzzle", page_icon="💧", layout="wide")

for key, default in {
    "capacities": [],
    "current_state": [],
    "history": [],
    "moves_left": MAX_MOVES,
    "started": False,
    "game_over": False,
    "solution": [],
    "show_ai_hint": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.title("💧 Water Jug Puzzle")
st.write(
    "Move water between buckets to get exactly 4 litres in any one bucket. "
    "You can pour from a full bucket, or pour into an empty one."
)

n = st.number_input(
"Enter number of buckets (N)", min_value=2, max_value=6, value=3, step=1
)

if not st.session_state.started:
    if st.button("Start", type="primary"):
        try:
            puzzle = generate_puzzle(int(n), target=TARGET, max_moves=MAX_MOVES)
        except RuntimeError as error:
            st.error(f"Could not create a puzzle: {error}")
        else:
            initial_state = tuple(puzzle["initial_state"])
            st.session_state.capacities = puzzle["capacities"]
            st.session_state.current_state = initial_state
            st.session_state.history = [initial_state]
            st.session_state.moves_left = MAX_MOVES
            st.session_state.solution = puzzle["solution"]
            st.session_state.game_over = False
            st.session_state.show_ai_hint = False
            st.session_state.started = True
            st.rerun()
else:
    capacities = st.session_state.capacities
    current_state = tuple(st.session_state.current_state)
    history = st.session_state.history
    solution = st.session_state.solution
    game_over = st.session_state.game_over

    st.subheader("Your buckets")
    st.write(
        " | ".join(
            f"Bucket {index + 1}: {amount}/{capacities[index]} L"
            for index, amount in enumerate(current_state)
        )
)

    controls, inspector = st.columns([1, 1])
    with controls:
        st.write(f"Moves left: {st.session_state.moves_left}")
        from_bucket = st.selectbox(
            "From Bucket",
            options=list(range(len(capacities))),
            format_func=lambda index: f"Bucket {index + 1}",
            key="from_bucket",
            disabled=game_over,
        )
        to_bucket = st.selectbox(
            "To Bucket",
            options=list(range(len(capacities))),
            format_func=lambda index: f"Bucket {index + 1}",
            key="to_bucket",
            disabled=game_over,
        )

        if st.button("Transfer Water", type="primary", disabled=game_over):
            if not is_valid_transfer(
                current_state, capacities, from_bucket, to_bucket
            ):
                st.warning(
                    "Invalid move: You can only pour from a FULL bucket or into an EMPTY bucket."
                )
            else:
                amount = min(
                    current_state[from_bucket],
                    capacities[to_bucket] - current_state[to_bucket],
                )
                next_state = list(current_state)
                next_state[from_bucket] -= amount
                next_state[to_bucket] += amount
                next_state = tuple(next_state)
                st.session_state.current_state = next_state
                st.session_state.history = history + [next_state]
                st.session_state.moves_left -= 1

                if TARGET in next_state or st.session_state.moves_left == 0:
                    st.session_state.game_over = True
                st.rerun()

    if st.button("Show AI Hint", disabled=not bool(solution)):
        st.session_state.show_ai_hint = not st.session_state.show_ai_hint

    if TARGET in current_state:
        st.success(
            "Congratulations! You solved the N-Bucket Water Transfer puzzle!"
        )
    elif st.session_state.moves_left == 0:
        st.error("Don't worry! Out of moves — try again later.")

    x, y = to_barycentric(current_state)
    backend_variables = {
        "state": list(current_state),
        "barycentric_coordinates": {"x": round(x, 3), "y": round(y, 3)},
        "heuristic_h(S)": round(_heuristic(current_state, capacities), 3),
        "visited_state_count": len(set(history)),
    }

    with inspector:
        st.subheader("Backend Variables")
        st.json(backend_variables)

    show_solution = st.session_state.show_ai_hint or st.session_state.game_over
    figure = _draw_simplex(
        capacities, history, solution, show_hint=show_solution
    )
    st.pyplot(figure)
    plt.close(figure)