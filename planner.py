import sys
import heapq
from collections import deque

ACTIONS = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1)
}

def read_world(file_path):
    with open(file_path, 'r') as file:
        cols = int(file.readline())
        rows = int(file.readline())
        grid = []
        robot_start = None
        dirty_cells = set()

        for r in range(rows):
            line = file.readline().strip()
            row = []
            for c, char in enumerate(line):
                row.append(char)
                if char == '@':
                    robot_start = (r, c)
                elif char == '*':
                    dirty_cells.add((r, c))
            grid.append(row)

    return grid, robot_start, dirty_cells

def get_successors(state, grid):
    successors = []
    rows, cols = len(grid), len(grid[0])
    r, c = state.position

    for action, (dr, dc) in ACTIONS.items():
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#':
            new_state = State((nr, nc), state.dirty_cells)
            successors.append((action, new_state))

    if state.position in state.dirty_cells:
        new_dirt = set(state.dirty_cells)
        new_dirt.remove(state.position)
        new_state = State(state.position, new_dirt)
        successors.append(('V', new_state))

    return successors

class State:
    def __init__(self, position, dirty_cells):
        self.position = position
        self.dirty_cells = frozenset(dirty_cells)

    def is_goal(self):
        return len(self.dirty_cells) == 0

    def __eq__(self, other):
        return self.position == other.position and self.dirty_cells == other.dirty_cells

    def __hash__(self):
        return hash((self.position, self.dirty_cells))

def depth_first_search(start_state, grid):
    class SearchNode:
        def __init__(self, state, path):
            self.state = state
            self.path = path

    frontier = deque()
    explored = set()
    nodes_generated = 0
    nodes_expanded = 0

    frontier.append(SearchNode(start_state, []))

    while frontier:
        node = frontier.pop()
        state = node.state

        if state.is_goal():
            return node.path, nodes_generated, nodes_expanded

        explored.add(state)
        nodes_expanded += 1

        for action, child_state in get_successors(state, grid):
            if child_state not in explored and all(n.state != child_state for n in frontier):
                nodes_generated += 1
                frontier.append(SearchNode(child_state, node.path + [action]))

    return None, nodes_generated, nodes_expanded

def uniform_cost_search(start_state, grid):
    class SearchNode:
        def __init__(self, state, path, cost):
            self.state = state
            self.path = path
            self.cost = cost

        def __lt__(self, other):
            return self.cost < other.cost

    frontier = []
    heapq.heappush(frontier, (0, SearchNode(start_state, [], 0)))

    explored = set()
    cost_so_far = {start_state: 0}
    nodes_generated = 0
    nodes_expanded = 0

    while frontier:
        _, node = heapq.heappop(frontier)
        state = node.state

        if state.is_goal():
            return node.path, nodes_generated, nodes_expanded

        if state in explored:
            continue
        explored.add(state)
        nodes_expanded += 1

        for action, child_state in get_successors(state, grid):
            new_cost = node.cost + 1
            if child_state not in cost_so_far or new_cost < cost_so_far[child_state]:
                cost_so_far[child_state] = new_cost
                nodes_generated += 1
                heapq.heappush(frontier, (new_cost, SearchNode(child_state, node.path + [action], new_cost)))

    return None, nodes_generated, nodes_expanded

def main():
    if len(sys.argv) != 3:
        sys.exit(1)

    algorithm = sys.argv[1]
    world_file = sys.argv[2]

    grid, start, dirt = read_world(world_file)
    initial_state = State(start, dirt)

    if algorithm == "uniform-cost":
        plan, generated, expanded = uniform_cost_search(initial_state, grid)
    elif algorithm == "depth-first":
        plan, generated, expanded = depth_first_search(initial_state, grid)
    else:
        sys.exit(1)

    for action in plan:
        print(action)
    print(f"{generated} nodes generated")
    print(f"{expanded} nodes expanded")

if __name__ == "__main__":
    main()
