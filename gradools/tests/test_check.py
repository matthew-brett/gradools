""" Tests for check module
"""

from gradools.check import get_lists


def test_get_lists():
    res, msg = get_lists('', ('foo', 'bar'), ())
    assert res == {}
    assert msg == ''
    res, msg = get_lists("""

## someone

* foo : 13
""", ('foo', 'bar'), ())
    assert msg == ("Required field bar not present\n"
                   "Expecting total 13.0 for someone")
    res, msg = get_lists("""

## someone

* baz : 13
""", ('foo', 'bar'), ())
    assert msg == ("Did not expect key: 'baz' here\n"
                   "Required fields bar, foo not present\n"
                   "Expecting total 13.0 for someone")

    res, msg = get_lists("""

## someone

* baz : 13

### Another header not relevant

Some text
""", ('foo', 'bar'), ())
    assert msg == ("Did not expect key: 'baz' here\n"
                   "Required fields bar, foo not present\n"
                   "Expecting total 13.0 for someone")
