"""
Benchmarks to compare performing various tasks using a bidict
against manually keeping two inverse dicts ("2idict") consistent.
"""

from bidict import bidict
from bidict.compat import iteritems, itervalues, viewvalues
from itertools import islice, product
from operator import attrgetter, itemgetter
from random import choice, randint
import pytest


try:
    range = xrange
except NameError:
    pass


def invdict(d, _missing=object()):
    inv = {}
    for (k, v) in iteritems(d):
        if v in inv:
            raise Exception('Duplicate value')
        inv[v] = k
    return inv


SIZES = [randint(2**x, 2**(x+1)) for x in range(3, 16, 3)]
@pytest.fixture(params=SIZES, ids=str)
def data(request):
    return {object(): object() for _ in range(request.param)}

@pytest.fixture(params=(bidict, invdict), ids=('bidict', '2idict'))
def constructor(request):
    return request.param

### benchmark 1: compare initializing a bidict to initializing an inverse dict
# TODO: test with data that has values repeated?
def test_init(benchmark, constructor, data):
    benchmark(constructor, data)


### benchmark 2: compare getting a key by value in a bidict vs. an inverse dict
def test_get_key_by_val(benchmark, constructor, data):
    # TODO: is this a good way to do this test?
    val = choice(list(viewvalues(data)))
    obj = constructor(data)
    gkbv = (lambda val: obj.inv[val]) if constructor is bidict else (
            lambda val: obj[val])
    key = benchmark(gkbv, val)
    assert data[key] == val


### benchmark 3: compare setitem for a bidict vs. an inverse dict
# TODO: test with some duplicate values?
def test_setitem(benchmark, constructor, data):
    key, val, _missing = object(), object(), object()

    if constructor is bidict:
        def setup():
            return (constructor(data),), {}

        def setitem(b):
            b[key] = val

    else:
        def setup():
            return (data.copy(), constructor(data)), {}

        def setitem(d, inv):
            if val in inv:
                raise Exception('Value exists')
            oldval = d.get(key, _missing)
            d[key] = val
            if oldval is not _missing:
                del inv[oldval]
            inv[val] = key

    # TODO: iterations=100 causes: ValueError: Can't use more than 1 `iterations` with a `setup` function.
    #benchmark.pedantic(setitem, setup=setup, iterations=100)
    benchmark.pedantic(setitem, setup=setup)
