import copy
import time
from abc import ABCMeta
from typing import Generator, List, Set, Iterable, Dict, FrozenSet


# Su Doku (Japanese meaning number place) is the name given to a popular puzzle concept. Its origin is unclear, but
# credit must be attributed to Leonhard Euler who invented a similar, and much more difficult, puzzle idea called
# Latin Squares. The objective of Su Doku puzzles, however, is to replace the blanks (or zeros) in a 9 by 9 grid in
# such that each row, column, and 3 by 3 box contains each of the digits 1 to 9. Below is an example of a typical
# starting puzzle grid and its solution grid.

# A well constructed Su Doku puzzle has a unique solution and can be solved by logic, although it may be necessary to
# employ "guess and test" methods in order to eliminate options (there is much contested opinion over this). The
# complexity of the search determines the difficulty of the puzzle; the example above is considered easy because it
# can be solved by straight forward direct deduction.

# The 6K text file, sudoku.txt (right click and 'Save Link/Target As...'), contains fifty different Su Doku puzzles
# ranging in difficulty, but all with unique solutions (the first puzzle in the file is the example above).

# By solving all fifty puzzles find the sum of the 3-digit numbers found in the top left corner of each solution grid;
# for example, 483 is the 3-digit number found in the top left corner of the solution grid above.


class NoOptionsError(RuntimeError):

    def __init__(self, message: str):
        super().__init__(message)

class CellIndex(metaclass=ABCMeta):
    col: int
    row: int

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row

    def __str__(self):
        return f"[{self.col}, {self.row}]"

    def __eq__(self, other):
        if not isinstance(other, CellIndex):
            return False
        return self.col == other.col and self.row == other.row

    def __hash__(self):
        return hash((self.col, self.row))


columns: List[List[CellIndex]] = []
rows: List[List[CellIndex]] = []
blocks: List[List[CellIndex]] = []
all_cells: List[CellIndex] = []
for i in range(0, 9):
    columns.append([])
    rows.append([])
    for j in range(0, 9):
        columns[i].append(CellIndex(i, j))
        rows[i].append(CellIndex(j, i))
        all_cells.append(CellIndex(i, j))

for col_range in [range(0, 3), range(3, 6), range(6, 9)]:
    for row_range in [range(0, 3), range(3, 6), range(6, 9)]:
        block_range: List[CellIndex] = []
        for col_index in col_range:
            for row_index in row_range:
                block_range.append(CellIndex(col_index, row_index))
        blocks.append(block_range)


class Grid(metaclass=ABCMeta):
    """
    This class represents a Sudoku puzzle with selected values and tracked options for unknown values.
    """
    values: List[List[int]]  # x, y | col, row
    options: List[List[List[int]]]

    def __init__(self) -> None:
        super().__init__()
        self.values = []
        self.options = []
        for col in range(0, 9):
            self.values.append([])
            self.options.append([])
            for _row in range(0, 9):
                self.values[col].append(0)
                self.options[col].append(list(range(1, 10)))

    def is_solved(self) -> bool:
        """
        :return: True if this sudoku grid is fully solved
        """
        for row in self.values:
            for value in row:
                if value == 0:
                    return False
        return True

    def set_value_at(self, col: int, row: int, value: int) -> None:
        """
        Set the cell at the given location to the given value.
        This also removes the value from the sets of options for the cell's block, column, and row.

        :param col:     The column of the cell to set
        :param row:     The row of the cell to set
        :param value:   The value of the cell
        """
        if col < 0 or col > 8 or row < 0 or row > 8:
            raise RuntimeError(f"Cannot set out of range value {col}:{row}")
        self.values[col][row] = value
        if value == 0:
            return

        # Clear options
        self.options[col][row] = []

        # Remove value from block, column, and row options
        self.remove_options([value], blocks[get_block_index(col, row)])
        self.remove_options([value], columns[col])
        self.remove_options([value], rows[row])

    def remove_options(self, options: List[int], cells: Iterable[CellIndex]) -> bool:
        """
        Remove the given options from the given cells.

        :param options: The value options to remove
        :param cells:   The cells
        :return:
        """
        removed_count: int = 0
        for cell in cells:
            for option in options:
                try:
                    self.options[cell.col][cell.row].remove(option)
                    if len(self.options[cell.col][cell.row]) == 0:
                        raise NoOptionsError(f"Removed last option for cell: {CellIndex(cell.col, cell.row)}")
                    removed_count += 1
                except ValueError:
                    pass
        return removed_count > 0

    def __str__(self) -> str:
        str_value = ""
        for row in range(0, 9):
            for col in range(0, 9):
                str_value += f"{self.values[col][row]} "
            str_value += "\n"
        return str_value


def solve(grid: Grid) -> None:
    updated: bool = True

    while updated:
        updated = False
        scope_processing_updates = True
        while scope_processing_updates:
            scope_processing_updates = process_scopes(grid)
            updated = updated or scope_processing_updates

    if not grid.is_solved():
        # Fall back to relying on guess-and-check
        guesses = find_guesses(grid)
        for guess in guesses:
            try:
                solve(guess)
                grid.values = guess.values
                grid.options = guess.options
                return
            except NoOptionsError:
                # Guess resulted in an unsolvable grid, try the next one
                continue

        raise NoOptionsError("Cannot solve grid, no single options left for any cell")

def find_guesses(grid: Grid) -> List[Grid]:
    guesses: List[Grid]
    for cell in all_cells:
        guesses = []
        cell_options = grid.options[cell.col][cell.row]
        if len(cell_options) == 0:
            continue
        try:
            for option in cell_options:
                guess = copy.deepcopy(grid)
                guess.set_value_at(cell.col, cell.row, option)
                guesses.append(guess)
            return guesses
        except NoOptionsError:
            pass
    raise NoOptionsError("All options failed?!")

def process_scopes(grid: Grid) -> bool:
    updated: bool = False

    # Look for any cells that only have a single option
    for cell_index in all_cells:
        options = grid.options[cell_index.col][cell_index.row]
        if len(options) == 1:
            grid.set_value_at(cell_index.col, cell_index.row, options[0])
            updated = True

    # Look for any cells that is the only option for a value within a scope
    for column_siblings in columns:
        updated = set_only_options(grid, column_siblings)
        updated = reduce_block_options(grid, column_siblings) or updated
    for row_siblings in rows:
        updated = set_only_options(grid, row_siblings) or updated
        updated = reduce_block_options(grid, row_siblings) or updated
    for block_siblings in blocks:
        updated = set_only_options(grid, block_siblings) or updated
        updated = reduce_row_and_column_options(grid, block_siblings) or updated

    return updated


def set_only_options(grid: Grid, siblings: List[CellIndex]) -> bool:
    """
    Process a sibling scope (row, column, or block) looking for:
    1. any value that only has a single cell as an option
    2. any limiting set of cells that bound options (Example: two cells that are the only options for two values)

    :param grid:        The grid to process
    :param siblings:    The cells that make up the scope
    :returns:           True if the grid was modified
    """
    updated = False
    # Record limited sets of cells that contain the same cardinality of options.
    tuples: Dict[FrozenSet[int], Set[CellIndex]]
    potential_cells_by_value: Dict[int, Set[CellIndex]] = dict(map(lambda x: (x, set()), range(1,10)))
    cells_by_options: Dict[FrozenSet[int], Set[CellIndex]] = {}

    for sibling_cell in siblings:
        sibling_options = frozenset(grid.options[sibling_cell.col][sibling_cell.row])

        if sibling_options not in cells_by_options:
            cells_by_options[sibling_options] = set()
        cells_by_options[sibling_options].add(sibling_cell)

        for sibling_option in sibling_options:
            potential_cells_by_value[sibling_option].add(sibling_cell)

    # Set single-option values
    for value, potential_cells in potential_cells_by_value.items():
        if len(potential_cells) == 1:
            # Only option, set it
            cell_index = next(iter(potential_cells))
            grid.set_value_at(cell_index.col, cell_index.row, value)
            updated = True

    # Parse tuples from cell options
    tuples = tuples_from_cell_options(cells_by_options)

    # Parse tuples from value options (stop at a pair for sanity)
    tuples |= tuples_from_value_options(potential_cells_by_value)

    for options, cells in tuples.items():
        for cell in cells:
            current_options = grid.options[cell.col][cell.row]
            if len(current_options) != len(options):
                grid.options[cell.col][cell.row] = list(options)
                updated = True

        other_cells = list(filter(lambda x, tuple_cells=frozenset(cells): x not in tuple_cells, siblings))
        updated = grid.remove_options(list(options), other_cells) or updated
    return updated


def reduce_block_options(grid: Grid, siblings: List[CellIndex]) -> bool:
    """
    Process a row or column and detect if a value can only be provided by members of a single block.
    If so, it must be provided by the sibling members of the block and no other non-siblings members of the block
    may have that value as an option.

    :param grid:        The grid
    :param siblings:    The row or column sibling cells
    :return:    True if the grid was modified
    """
    updated = False
    potential_blocks_by_value: Dict[int, Set[int]] = dict(map(lambda x: (x, set()), range(1,10)))
    for sibling_cell in siblings:
        block_index = get_block_index(sibling_cell.col, sibling_cell.row)
        for sibling_option in grid.options[sibling_cell.col][sibling_cell.row]:
            potential_blocks_by_value[sibling_option].add(block_index)
    for value, potential_blocks in potential_blocks_by_value.items():
        if len(potential_blocks) == 1:
            other_block_members = filter(lambda cell: cell not in siblings, blocks[potential_blocks.pop()])
            updated = grid.remove_options([value], other_block_members) or updated

    return updated

def reduce_row_and_column_options(grid: Grid, siblings: List[CellIndex]) -> bool:
    """
    Process a block sibling set and detect if a value can only be provided by a single row or column segment of
    this block.  If so, then it must be provided by this block's members for the given row or segment, meaning that
    no other member of the row or column outside of this block may have that value as an option.

    :param grid:        The grid
    :param siblings:    The block sibling cells
    :return:            True if the grid was modified
    """
    updated = False
    potential_cols_by_value: Dict[int, Set[int]] = dict(map(lambda x: (x, set()), range(1,10)))
    potential_rows_by_value: Dict[int, Set[int]] = dict(map(lambda x: (x, set()), range(1,10)))
    for sibling_cell in siblings:
        for sibling_option in grid.options[sibling_cell.col][sibling_cell.row]:
            potential_cols_by_value[sibling_option].add(sibling_cell.col)
            potential_rows_by_value[sibling_option].add(sibling_cell.row)
    for value, potential_cols in potential_cols_by_value.items():
        if len(potential_cols) == 1:
            other_col_members = list(filter(lambda cell: cell not in siblings, columns[potential_cols.pop()]))
            updated = grid.remove_options([value], other_col_members) or updated
    for value, potential_rows in potential_rows_by_value.items():
        if len(potential_rows) == 1:
            other_row_members = list(filter(lambda cell: cell not in siblings, rows[potential_rows.pop()]))
            updated = grid.remove_options([value], other_row_members) or updated

    return updated

def tuples_from_cell_options(cells_by_options: Dict[FrozenSet[int], Set[CellIndex]]) -> Dict[FrozenSet[int], Set[CellIndex]]:
    tuples: Dict[FrozenSet[int], Set[CellIndex]] = {}
    for options, cells in cells_by_options.items():
        if len(options) == len(cells):
            tuples[options] = cells
    return tuples

def tuples_from_value_options(potential_cells_by_value: Dict[int, Set[CellIndex]]) -> Dict[FrozenSet[int], Set[CellIndex]]:
    tuples: Dict[FrozenSet[int], Set[CellIndex]] = {}
    for value, potential_cells in potential_cells_by_value.items():
        if len(potential_cells) != 2:
            continue

        # check for pair
        for other_value, other_potential_cells in potential_cells_by_value.items():
            if other_value == value:
                continue
            if other_potential_cells == potential_cells:
                # found a pair
                value_set = frozenset({value, other_value})
                tuples[value_set] = potential_cells
    return tuples

def get_block_index(col: int, row: int) -> int:
    return 3 * _get_block_segment(col) + _get_block_segment(row)


def load_grids() -> Generator[Grid, None, None]:
    grid: Grid
    row: int = 0
    with open("p096_sudoku.txt", "r") as source_file:
        for line in source_file:
            if line.startswith("Grid"):
                print(f"Solving: {line}")
                grid = Grid()
                row = 0
                continue
            for col, value in enumerate(line):
                try:
                    int_value = int(value, 10)
                    grid.set_value_at(col, row, int_value)
                except ValueError:
                    continue
            row += 1
            if row >= 9:
                yield grid

def _get_block_segment(index: int) -> int:
    if 0 <= index < 3:
        return 0
    elif 3 <= index < 6:
        return 1
    else:
        return 2

if __name__ == "__main__":

    result = 0
    start_time = time.time()

    for current_grid in load_grids():
        print(current_grid)
        solve(current_grid)
        print("Solution:")
        print(current_grid)

        grid_value = f"{current_grid.values[0][0]}{current_grid.values[1][0]}{current_grid.values[2][0]}"
        result += int(grid_value)

    end_time = time.time()

    print(f"Result: {result}\nTime: {end_time - start_time}")
