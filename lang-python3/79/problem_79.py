import time
from abc import ABCMeta
from queue import Queue
from typing import Generator, Tuple, Dict, List

from pydantic import BaseModel


# A common security method used for online banking is to ask the user for three random characters from a passcode.
# For example, if the passcode was 531278, they may ask for the 2nd, 3rd, and 5th characters;
# the expected reply would be: 317.
# The text file, keylog.txt, contains fifty successful login attempts.
# Given that the three characters are always asked for in order, analyse the file so as to determine the shortest
# possible secret passcode of unknown length.



# for below "less than" and "greater than" refer to passcode position, not digit value
# for every triple we have a digit at i, j(>i), k(>j)
# value_i < value_j, value_i < value_k, value_j < value_k
# each digit choice must minimize the number of remaining digit dependencies
# each digit choice should resolve the maximum number of requirement statements?
# first digit must be from the set of i values
#   assuming no duplicates, i must be one that is also NOT a j/k value)
# For each value, record all values that it is less than
# Then iterate based upon length of "shorter than" dependencies?

# What if I had:
# 115
# 151
# 511
# Shortest should be 11511

# What if I had:
# 123
# 456
# 513

def get_adjacency_matrix(attempt_generator: Generator[Tuple[int, int, int], None, None]) -> Dict[int, Dict[int, int]]:
    adjacency_matrix: Dict[int, Dict[int, int]] = {}

    for attempt in attempt_generator:
        i, j, k = attempt
        if i not in adjacency_matrix:
            adjacency_matrix[i] = {}
        if j not in adjacency_matrix:
            adjacency_matrix[j] = {}
        if k not in adjacency_matrix:
            adjacency_matrix[k] = {}
        adjacency_matrix[i][j] = 1
        adjacency_matrix[j][k] = 1
    return adjacency_matrix

def find_root(adjacency_matrix: Dict[int, Dict[int, int]]) -> int:
    roots: List[int] = list(adjacency_matrix.keys())
    # looking for adjacency_matrix[*][root] DNE
    for source, target_dict in adjacency_matrix.items():
        for target in target_dict.keys():
            if target in roots:
                roots.remove(target)
    if len(roots) > 1:
        raise RuntimeError("Found multiple roots for the graph")
    if len(roots) < 1:
        raise RuntimeError("Cannot find a root digit for the graph")
    return roots[0]

def solve_no_duplicates(attempt_generator: Generator[Tuple[int, int, int], None, None]) -> str:
    adjacency_matrix = get_adjacency_matrix(attempt_generator)
    root = find_root(adjacency_matrix)

    # Breadth-first-search for the shortest path that visits every node
    queue: Queue[BFSVisit] = Queue()
    queue.put(BFSVisit(node=root, path=[root]))
    while not queue.empty():
        visit = queue.get()
        next_nodes = adjacency_matrix.get(visit.node, {})
        for next_node in next_nodes.keys():
            if next_node in visit.path:
                continue
            next_path: List[int] = visit.path + [next_node]
            if len(next_path) == len(adjacency_matrix):
                return "".join(map(lambda val: str(val), next_path))
            queue.put(BFSVisit(node=next_node, path=next_path))

    raise RuntimeError("Cannot determine a path that visits all nodes")

def read_attempt_file() -> Generator[Tuple[int, int, int], None, None]:
    with open("0079_keylog.txt", "r") as source_file:
        for line in source_file:
            yield [int(line[0]), int(line[1]), int(line[2])]

def generate_attempts(attempts: List[str]) -> Generator[Tuple[int, int, int], None, None]:
    for attempt in attempts:
        yield [int(attempt[0]), int(attempt[1]), int(attempt[2])]

class BFSVisit(BaseModel):
    node: int
    path: List[int]

if __name__ == "__main__":

    player_1_victories = 0
    start_time = time.time()

    result = solve_no_duplicates(read_attempt_file())
    end_time = time.time()

    print(f"Result: {result}\nTime: {end_time - start_time}")
