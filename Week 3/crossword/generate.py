import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # Check each variables domain make sure variable length matches with domain value length.

        for variable in self.domains:
            for word in set(self.domains[variable]):
                # Check Unary Constraints
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        # Get tuple of overlap positions of letters
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return revised
        
        i, j = overlap

        # Remove value from x domain if no corresponding value for y
        for word_x in set(self.domains(x)):
            match_found = False
            for word_y in self.domains(y):
                # Match found no need for further check for binary constraint
                if word_x[i] == word_y[j]:
                    match_found = True
                    break
            # Satisfy binary constraint
            if match_found == False:
                self.domains[x].remove(word_x)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # Initially set up arcs in the problem
        if arcs == None:
            arcs = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.append((x, y))

        queue = list(arcs)

        while len(queue) > 0:

            # Dequeue the first arc 
            x, y = queue.pop(0)

            # Make the pair arc consistent
            if self.revise(x, y):
                # No possible solution.
                if len(self.domains[x]) == 0:
                    return False
                
                # Again add neighbors to the arc list for recheck of constraints.
                for z in self.neighbors(x):
                    if z != y:
                        queue.append(z, x)

        # Arc Consitent!
        return True
        
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Loop every var in crossword
        for var in self.crossword.variables:
            # Check var assignment
            if var not in assignment:
                return False
        # All var assigned
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # consistent check (Each value is unique)
        values = assignment.values()
        if len(values) != len(set(values)):
            return False
        
        for variable, word in assignment.items():
            
            # Variable length and word length should be same.
            if len(word) != variable.length:
                return False
            
            # Make sure no conflicts between neighbor variables
            for neighbor in self.crossword.neighbors(variable):

                if neighbor in assignment:
                    # If the overlap of word and it's neighbor one at a time.
                    overlap = self.crossword.overlap[variable, neighbor]
                    if overlap:
                        var_pos, neighbor_pos = overlap

                        # Check if the overlap letters match
                        if word[var_pos] != assignment[neighbor][neighbor_pos]:
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Store list of tuple of (word, conflict count)
        conflicts = []

        # Check each word in domain
        for word in self.domains(var):
            conflict_count = 0
            
            # Get neighbors of var
            for neighbor in self.crossword.neighbor(var):
                if neighbor not in assignment:
                    # Get overlap of neighbor var and var.
                    overlap = self.crossword.overlap[var, neighbor]
                    if overlap:
                        i, j = overlap
                        # Get each neighbor word
                        for neighbor_word in self.domains[neighbor]:
                            # Conflict, increase count
                            if word[i] != neighbor_word[j]:
                                conflict_count += 1
            
            # add conflicts to list
            conflicts.append((word, conflict_count))
        
        # Sort based on the conflict_count of tuples in the list
        conflicts.sort(key= lambda x: x[1])

        # Return the sorted words ini domain according to ascending order of conflict.
        return [word for word, _ in conflicts]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
