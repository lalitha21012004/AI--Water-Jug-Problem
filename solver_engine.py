import math
import random
from typing import Dict, List, Optional, Sequence, Tuple


State = Tuple[int, ...]


# TODO: clean this up later, works for now
def to_barycentric(state: Sequence[int]) -> Tuple[float, float]:
    if not state:
        return 0.0, 0.0
    v_cnt = len(state)
    px = 0.0
    py = 0.0
    for idx, amt in enumerate(state):
        a = 2 * math.pi * idx / v_cnt
        px += amt * math.cos(a)
        py += amt * math.sin(a)
    return px, py


def is_valid_transfer(state: Sequence[int], caps: Sequence[int], src: int, dst: int) -> bool:
    if len(state) != len(caps):
        return False
    if src == dst or src < 0 or dst < 0 or src >= len(state) or dst >= len(state):
        return False
    if state[src] <= 0 or state[dst] >= caps[dst]:
        return False

    full_src = state[src] == caps[src]
    empty_dst = state[dst] == 0
    return full_src or empty_dst


def generate_puzzle(
    n: int, target: int = 4, max_moves: int = 20
) -> Dict[str, object]:
    if n < 2:
        raise ValueError("n must be at least 2 to allow a transfer.")
    if not 1 <= target <= 10:
        raise ValueError("target must be between 1 and 10 litres.")
    if max_moves < 1:
        raise ValueError("max_moves must be at least 1.")

    for _ in range(5000):
        capacities = [random.randint(3, 10) for _ in range(n)]
        initial_state = (capacities[0],) + (0,) * (n - 1)

        if target in initial_state:
            continue

        solution = heuristic_dfs(initial_state, capacities, target, max_moves)
        if solution is not None and len(solution) > 1:
            return {
                "capacities": capacities,
                "initial_state": initial_state,
                "target": target,
                "max_moves": max_moves,
                "solution": solution,
            }

    raise RuntimeError(
        "Could not generate a solvable puzzle within the attempt limit. "
        "Try increasing n or max_moves."
    )


def heuristic_dfs(
    start_state: Sequence[int],
    capacities: Sequence[int],
    target: int,
    max_moves: int,
) -> Optional[List[State]]:
    # dfs with heuristic, fingers crossed
    if len(start_state) != len(capacities) or not capacities or target <= 0 or max_moves < 0:
        return None

    start = tuple(start_state)
    goal_points = [
        to_barycentric(
            tuple(target if i == bucket else 0 for i in range(len(capacities)))
        )
        for bucket, capacity in enumerate(capacities)
        if target <= capacity
    ]
    if not goal_points:
        return None

    def calc_h(st: State) -> float:
        hx, hy = to_barycentric(st)
        return min(math.hypot(hx - gx, hy - gy) for gx, gy in goal_points)

    stack: List[Tuple[State, List[State]]] = [(start, [start])]
    best_depth: Dict[State, int] = {}

    while stack:
        curr_state, path = stack.pop()
        d = len(path) - 1
        if target in curr_state:
            return path
        if d >= max_moves:
            continue

        prev_d = best_depth.get(curr_state)
        if prev_d is not None and prev_d <= d:
            continue
        best_depth[curr_state] = d

        neighbors: List[State] = []
        for s in range(len(capacities)):
            for destination in range(len(capacities)):
                if not is_valid_transfer(curr_state, capacities, s, destination):
                    continue
                pour_amt = min(curr_state[s], capacities[destination] - curr_state[destination])
                nxt = list(curr_state)
                nxt[s] -= pour_amt
                nxt[destination] += pour_amt
                neighbors.append(tuple(nxt))

        sorted_neighbors = sorted(neighbors, key=calc_h)
        stack.extend(
            (nbr, path + [nbr])
            for nbr in reversed(sorted_neighbors)
        )

    return None