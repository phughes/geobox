"""
Tests for geobox2.  Can be run with nosests, e.g:
$ nosetests geobox2_tests.py
"""
import geobox2

import decimal


def testboundingbox(self):
    lat = _dec(42.270872)
    lon = _dec(-83.726329)
    a2 = geobox2.Geobox(lat, lon)
    top, left, bottom, right = a2.bounding_box(lat, lon, self.scope)
    assert top > lat, "top > lat"
    assert bottom < lat, "bottom < lat"
    assert left < lon, "left < lon"
    assert right > lon, "right > lon"

    eq_(top, _dec(43.0), "top")
    eq_(bottom, _dec(42.0), "bottom")
    eq_(left, _dec(-84.0), "left")
    eq_(right, _dec(-83.0), "right")
        

def eq_(a, b, msg=None):
    """Shorthand for 'assert a == b, "%r != %r" % (a, b)
    """
    def details():
        if msg:
            return "\n%s\n%s\n !=\n%s" % (msg, a, b)
        else:
            return "\n%s\n !=\n%s" % (a, b)
    assert a == b, details()

def _dec(num):
    return decimal.Decimal(str(num))




        


    