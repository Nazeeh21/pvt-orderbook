"""
Library that supports the construction of human-readable, interactive static
analysis reports that consist of decorated concrete syntax representations of
programs.
"""
from __future__ import annotations
from typing import Union, Tuple
import doctest

class location(Tuple[int, int]):
    """
    Data structure for representing a location within a report as a tuple of
    two integers: the line number and the column on that line.

    Because this class is derived from the :obj:`tuple` type, relational
    operators can be used to determine whether one location appears before
    or after another.

    >>> location((12, 24)) < location((13, 24))
    True
    >>> location((13, 23)) < location((13, 24))
    True
    >>> location((13, 24)) < location((13, 24))
    False
    >>> location((14, 0)) < location((13, 0))
    False
    >>> location((14, 23)) < location((13, 41))
    False
    >>> location((12, 24)) <= location((13, 24))
    True
    >>> location((13, 23)) <= location((13, 24))
    True
    >>> location((13, 24)) <= location((13, 24))
    True
    >>> location((14, 0)) <= location((13, 0))
    False
    >>> location((14, 23)) <= location((13, 41))
    False
    """
    def __getattribute__(self, name):
        """
        Simulate named attributes for the two components of an instance.

        >>> l = location((13, 24))
        >>> l.line
        13
        >>> l.column
        24

        Other attributes should not be affected.

        >>> str(type(l.__hash__))
        "<class 'method-wrapper'>"
        """
        if name == 'line':
            return self[0]
        if name == 'column':
            return self[1]

        return object.__getattribute__(self, name)

    def __add__(self: location, other: Tuple[int, int]):
        """
        Return a later location according to the supplied pair of integers.
        The first component must be an integer indicating the amount by which
        the line component value should increase. The second component must be
        an integerF indicating the amount by which the column component value
        should increase.


        >>> l = location((13, 24))
        >>> l + (3, 0)
        (16, 24)
        >>> l + (1, -17)
        (14, 7)
        """
        return location((self[0] + other[0], self[1] + other[1]))

    def __sub__(self: location, other: Tuple[int, int]):
        """
        Return an earlier location according to the supplied pair of integers.
        The first component must be an integer indicating the amount by which
        the line component value should decrease. The second component must be
        an integer indicating the amount by which the column component value
        should decrease.

        >>> l = location((13, 24))
        >>> l - (3, 0)
        (10, 24)
        >>> l - (7, 6)
        (6, 18)
        """
        return location((self[0] - other[0], self[1] - other[1]))

class report:
    """
    Data structure that represents the raw concrete syntax string as a
    two-dimensional array of two-sided stacks. Each stack holds delimiters
    (left and right) that may appear before or after that character in
    the rendered version of the report.

    >>> r = report(
    ...    'def f(x, y):\\n' +
    ...    '    return x + y'
    ... )

    The individual lines in the supplied string can be retrieved via the
    ``lines`` attribute.

    >>> list(r.lines)
    ['def f(x, y):', '    return x + y']

    Delimiters can be added around a range within the report by specifying the
    locations corresponding to the endpoints (inclusive) of the range.

    >>> r.enrich((2, 11), (2, 15), '(', ')')
    >>> for line in r.render().split('\\n'):
    ...     print(line)
    def f(x, y):
        return (x + y)

    The optional ``enrich_intermediate_lines`` parameter can be used to delimit
    all complete lines that appear between the supplied endpoints.

    >>> r.enrich((1, 0), (2, 15), '<b>', '</b>', enrich_intermediate_lines=True)
    >>> for line in r.render().split('\\n'):
    ...     print(line)
    <b>def f(x, y):</b>
    <b>    return (x + y)</b>

    By default, the ``enrich_intermediate_lines`` parameter is set to ``False``.

    >>> r.enrich((1, 0), (2, 15), '<div>\\n', '\\n</div>')
    >>> for line in r.render().split('\\n'):
    ...     print(line)
    <div>
    <b>def f(x, y):</b>
    <b>    return (x + y)</b>
    </div>
    
    The optional ``skip_whitespace`` parameter (which is set to ``False``
    by default) can be used to ensure that left-hand delimiters skip over
    whitespace (moving to the right and down) and, likewise, that right-hand
    delimiters skip over whitespace (moving to the left and up).

    >>> r = report(
    ...    '   \\n' +
    ...    '\\n' +
    ...    '   \\n' +
    ...    '    def f(x, y):\\n' +
    ...    '        return x + y        \\n' +
    ...    '                            \\n' +
    ...    '                            \\n' +
    ...    '                            '
    ... )
    >>> r.enrich((2, 0), (5, 20), '<b>', '</b>', skip_whitespace=True)
    >>> for line in r.render().split('\\n'):
    ...     print(line)
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
        <b>def f(x, y):
            return x + y</b>        
    <BLANKLINE>   
    <BLANKLINE>
    <BLANKLINE>

    If the delimited text consists of whitespace and ``skip_whitespace`` is
    ``True``, no delimiters are added.

    >>> r.enrich((6, 0), (6, 20), '<i>', '</i>', skip_whitespace=True)
    >>> r.enrich((1, 0), (1, 3), '<i>', '</i>', skip_whitespace=True)
    >>> r.enrich((2, 0), (3, 3), '<i>', '</i>', skip_whitespace=True)
    >>> for line in r.render().split('\\n'):
    ...     print(line)
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
        <b>def f(x, y):
            return x + y</b>        
    <BLANKLINE>   
    <BLANKLINE>
    <BLANKLINE>

    If ``enrich_intermediate_lines`` and ``skip_whitespace`` are both ``True``,
    then individual lines between the first occurrence of a left-hand delimiter
    and the last occurrence of a right-hand delimiter are delimited as if each
    line was being enriched individually with ``skip_whitespace`` set to
    ``True``.

    >>> r = report(
    ...    '    \\n' +
    ...    '\\n' +
    ...    '    def f(x, y):\\n' +
    ...    '                            \\n' +
    ...    '\\n' +
    ...    '                            \\n' +
    ...    '        return x + y        \\n' +
    ...    '\\n' +
    ...    '                            \\n' +
    ...    '                            '
    ... )
    >>> r.enrich(
    ...     (1, 3), (10, 20),
    ...     '<b>', '</b>',
    ...     enrich_intermediate_lines=True, skip_whitespace=True
    ... )
    >>> for line in r.render().split('\\n'):
    ...     print(line)
    <BLANKLINE>
    <BLANKLINE>
        <b>def f(x, y):</b>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
            <b>return x + y</b>        
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>

    It is possible to specify at what value the line and column numbering
    schemes begin by supplying the optional ``line`` and ``column`` arguments
    to the instance constructor.

    >>> r = report('    def f(x, y):\\n        return x + y', line=1, column=0)
    >>> r.enrich((1, 0), (2, 20), '<b>', '</b>', skip_whitespace=True)
    >>> list(r.render().split('\\n'))
    ['    <b>def f(x, y):', '        return x + y</b>']
    >>> r = report('    def f(x, y):\\n        return x + y', line=0, column=0)
    >>> r.enrich((0, 0), (1, 20), '<b>', '</b>', skip_whitespace=True)
    >>> list(r.render().split('\\n'))
    ['    <b>def f(x, y):', '        return x + y</b>']

    """
    def __init__(self: report, string: str, line: int = 1, column: int = 0):
        self.string = string
        self.lines = string.split('\n')
        self._stacks = (
            [[]] + # Allow line numbers to begin at index ``1``.
            [
                [([], c, []) for c in line] +
                [([], '', [])] # Allow enrichment of empty lines.
                for line in self.lines
            ]
        )
        self.line = line
        self.column = column
        self._base = location((self.line, self.column))

    def _skip_whitespace_left(self: report, location_: location) -> location:
        """
        Find the first location (starting from the supplied location and moving
        to the right and down) that is not a whitespace character.
        """
        (line, column) = location_

        if column == 0:
            while len(self.lines[line - 1]) == 0:
                line += 1

        while self._stacks[line][column][1] in (' ', ''):
            column += 1
            if column == len(self._stacks[line]) - 1:
                if line == len(self._stacks) - 1:
                    break
                line += 1
                column = 0

            if column == 0:
                while len(self.lines[line - 1]) == 0:
                    line += 1

        return location((line, column))

    def _skip_whitespace_right(self: report, location_: location) -> location:
        """
        Find the first location (starting from the supplied location and moving
        left and up) that is not a whitespace character.
        """
        (line, column) = location_
        while self._stacks[line][column][1] in (' ', ''):
            column -= 1
            if column == -1:
                if line == 1:
                    column = 0
                    break
                line -= 1
                column = len(self._stacks[line]) - 1

        return location((line, column))

    def enrich( # pylint: disable=too-many-arguments
            self: report,
            start: Union[Tuple[int, int], location],
            end: Union[Tuple[int, int], location],
            left: str,
            right: str,
            enrich_intermediate_lines = False,
            skip_whitespace = False
        ):
        """
        Add a pair of left and right delimiters around a given range within
        this report instance.

        >>> r = report(
        ...    'def f(x, y):\\n' +
        ...    '    return x + y'
        ... )
        >>> r.enrich((1, 0), (2, 15), '<b>', '</b>', True)
        >>> for line in r.render().split('\\n'):
        ...     print(line)
        <b>def f(x, y):</b>
        <b>    return x + y</b>
        """
        # Tuples containing exactly two integers are permitted.
        start = location(start) - self._base + location((1, 0))
        end = location(end) - self._base + location((1, 0))

        if skip_whitespace:
            start = self._skip_whitespace_left(start)
            end = self._skip_whitespace_right(end)

        if start > end:
            return

        # Add the delimiters at the specified positions, and (if directed
        # to do so) around any intermediate lines.
        self._stacks[start.line][start.column][0].append(left)
        if enrich_intermediate_lines:
            line = start.line
            while line < end.line:
                empty = self.lines[line - 1].strip() == ''
                if (not skip_whitespace) or (not empty):
                    column = len(self._stacks[line]) - 1
                    if skip_whitespace:
                        while (
                            self._stacks[line][column][1] in (' ', '')
                            and
                            column > 0
                            and
                            (line > start.line or column > start.column)
                        ):
                            column -= 1
                    self._stacks[line][column][2].append(right)

                line += 1

                empty = self.lines[line - 1].strip() == ''
                if (not skip_whitespace) or (not empty):
                    column = 0
                    if skip_whitespace:
                        while (
                            self._stacks[line][column][1] in (' ', '')
                            and
                            column < len(self._stacks[line]) - 1
                            and
                            (line < end.line or column < end.column)
                        ):
                            column += 1
                    self._stacks[line][column][0].append(left)

        self._stacks[end.line][end.column][2].append(right)

    def render(self: report) -> str:
        """
        Return the report (incorporating all delimiters) as a string.

        >>> r = report(
        ...    'def f(x, y):\\n' +
        ...    '    return x + y'
        ... )
        >>> r.enrich((1, 0), (2, 16), '<b>', '</b>')
        >>> for line in r.render().split('\\n'):
        ...     print(line)
        <b>def f(x, y):
            return x + y</b>
        """
        return '\n'.join([
            ''.join([
                ''.join(reversed(pres)) + c + ''.join(posts)
                for (pres, c, posts) in line
            ])
            for line in self._stacks[1:]
        ])

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
