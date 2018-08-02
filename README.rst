A Python implementation of 3-way merge of texts.

Given BASE, OTHER, THIS, tries to produce a combined text
incorporating the changes from both BASE->OTHER and BASE->THIS.
All three will typically be sequences of lines.

Usage
=====

From the command-line::

    $ echo foo > mine
    $ echo bar > base
    $ echo blah > other
    $ python -m merge3 mine base other > merged
    $ cat merged

Or from Python::

    >>> import merge3
    >>> m3 = merge3.Merge3(
    ...                    ['common\n', 'base\n'],
    ...                    ['common\n', 'a\n'],
    ...                    ['common\n', 'b\n'])
    >>> list(m3.merge_annotated())
    ['u | common\n', '<<<<\n', 'A | a\n', '----\n', 'B | b\n', '>>>>\n']
