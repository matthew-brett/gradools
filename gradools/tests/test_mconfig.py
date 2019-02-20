""" Test mconfig module
"""

from collections import OrderedDict
from io import StringIO

from gradools.mconfig import get_scores, get_score_lines


def test_get_scores():
    fobj = StringIO()
    o, e = get_scores(fobj)
    assert o == {}
    assert e == {}
    fobj = StringIO("""

* score_1 : 1
""")
    o, e = get_scores(fobj)
    assert o == {}
    assert e == {}
    fobj = StringIO("""

Ordinary maxima:
* score_1 : 1
""")
    o, e = get_scores(fobj)
    assert o == dict(score_1 = 1)
    assert e == {}
    fobj = StringIO("""

Ordinary maxima:
*score_1 : 1


Total: 1
""")
    o, e = get_scores(fobj)
    assert o == dict(score_1 = 1)
    assert e == {}
    fobj.seek(0)
    assert get_score_lines(o, e) == '* score_1: 1.0\n'
    fobj = StringIO("""

Ordinary maxima:
* score_1 : 1

Extra maxima:
* score_10: 2.5

Total: 3.5
""")
    o, e = get_scores(fobj)
    assert o == dict(score_1 = 1)
    assert e == dict(score_10=2.5)
    fobj.seek(0)
    assert (get_score_lines(o, e) ==
            '* score_1: 1.0\n\n* score_10: 2.5\n')
    fobj = StringIO("""
Ordinary maxima:
*  score_1 : 1
*another_score: 2

Extra maxima:

*score_10: 2.5
*    extra_score: 5

Total:
""")
    o, e = get_scores(fobj)
    assert o == OrderedDict((('score_1', 1), ('another_score', 2)))
    assert e == OrderedDict((('score_10', 2.5), ('extra_score', 5)))
    fobj.seek(0)
    assert (get_score_lines(o, e) ==
            '* score_1: 1.0\n* another_score: 2.0\n\n'
            '* score_10: 2.5\n* extra_score: 5.0\n')
