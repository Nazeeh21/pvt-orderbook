"""
Python library that transforms any string parser into a parser
that skips portions of the input that contain syntax errors.
"""
from __future__ import annotations
from typing import Any, List, Tuple, Callable
import doctest

def parsial(
        parse: Callable[[str], Any]
    ) -> Callable[[str], Tuple[Any, List[slice]]]:
    """
    Accept a parsing function (that takes a string input) and return a new
    parsing function. This new function attempts to parse an input string
    using the original parsing function even if parsing errors occur. This
    is done by selectively removing portions of the input that cause
    errors.

    >>> lines = [
    ...     'x = 123',
    ...     'y =',
    ...     'print(x)',
    ...     'z = x +',
    ...     'print(2 * x)'
    ... ]
    >>> import ast
    >>> parser = parsial(ast.parse)
    >>> (a, slices) = parser('\\n'.join(lines))
    >>> exec(compile(a, '', 'exec'))
    123
    246

    In addition to returning the result, the new function also returns a
    list of :obj:`slice` instances (one for each line found in the input
    string).
    
    >>> for s in slices:
    ...     print(s)
    slice(0, 7, None)
    slice(0, 0, None)
    slice(0, 8, None)
    slice(0, 0, None)
    slice(0, 12, None)

    Each :obj:`slice` instance indicates what portion of the corresponding
    line in the input was included in the successful parsing attempt.
    
    >>> [l[s] for (l, s) in zip(lines, slices)]
    ['x = 123', '', 'print(x)', '', 'print(2 * x)']

    For a string that can be parsed successfully, the parser supplied to
    this function is invoked exactly once. In the worst case, it is invoked
    once per line of the input string.
    """
    # Define the new parsing function.
    def parse_(source: str) -> List[int]:
        lines = source.split('\n')
        lines_ = None
        result = None

        # Find the longest stretch of lines that begins with the first line
        # and leads to a successful parse.
        for end in range(len(lines), -1, -1):
            try:
                result = parse('\n'.join(lines[:end]))
                lines_ = lines[:end]
                break
            except Exception as _: # pylint: disable=broad-exception-caught
                pass

        # If the entire input was not parsed via the block above, attempt to
        # include each remaining line to see if a parse succeeds. Keep track
        # of which lines are skipped.
        skips = set()
        if end < len(lines):
            skips.add(end)
            lines_ = lines[:end] + ['']
            for i in range(end + 1, len(lines)):
                try:
                    lines__ = lines_ + [lines[i]]
                    result = parse('\n'.join(lines__))
                    lines_ = lines__
                except Exception as _: # pylint: disable=broad-exception-caught
                    lines_ += ['']
                    skips.add(i)

        # Return the result of a successful parsing attempt, as well as a list
        # of slices indicating what portions of each line were included to
        # obtain the result.
        return (
            result,
            [
                slice(0, len(line) if i not in skips else 0)
                for (i, line) in enumerate(lines)
            ]
        )

    return parse_

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
