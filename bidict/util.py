"""Utilities for working with one-to-one relations."""

from .compat import PY2, iteritems, izip
from collections import Iterator
from itertools import chain


def pairs(*args, **kw):
    """Yield the pairs provided. Signature matches dict's."""
    it = ()
    if args:
        l = len(args)
        if l != 1:
            raise TypeError('Expected at most 1 positional argument, got %d' % l)
        arg0 = args[0]
        try:
            it = iteritems(arg0)
        except AttributeError:
            it = iter(arg0)
    if kw:
         it = chain(it, iteritems(kw))
    return it


class inverted(Iterator):
    """
    An iterator yielding the inverse items of the provided mapping.

    Works with any object that can be iterated over as a mapping or in pairs,
    or that implements its own __inverted__ method.
    """

    def __init__(self, data):
        """Create an :class:`inverted` instance."""
        self._data = data

    def __iter__(self):
        """Create an instance of the actual generator."""
        makeit = getattr(self._data, '__inverted__', self.__next__)
        return makeit()

    def __next__(self):
        """Yield the inverse of each pair in the associated data."""
        for (k, v) in pairs(self._data):
            yield (v, k)

    # compat
    if PY2:
        next = __next__
