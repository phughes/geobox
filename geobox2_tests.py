"""
Tests for geobox2.  Can be run with nosests, e.g:
$ nosetests geobox2_tests.py
"""
import geobox2

import decimal


def testboundingbox():
    lat = _dec(42.270872)
    lon = _dec(-83.726329)
    a2 = geobox2.Geobox(lat, lon)
    scope = _dec(1.0)
    top, left, bottom, right = a2.bounding_box(lat, lon, scope)
    assert top > lat, "top > lat"
    assert bottom < lat, "bottom < lat"
    assert left < lon, "left < lon"
    assert right > lon, "right > lon"

    eq_(top, _dec(43.0), "top")
    eq_(bottom, _dec(42.0), "bottom")
    eq_(left, _dec(-84.0), "left")
    eq_(right, _dec(-83.0), "right")

class TestAppend(object):

    def setup(self):
        self.oldscopes = geobox2.SCOPE_SIZES
        geobox2.SCOPE_SIZES = [_dec(1.0)]
        self.center =    "43.000|-84.000|42.000|-83.000"

        self.left =      "43.000|-85.000|42.000|-84.000"
        self.right =     "43.000|-83.000|42.000|-82.000"
        self.down =      "42.000|-84.000|41.000|-83.000"
        self.up =        "44.000|-84.000|43.000|-83.000"

        self.leftdown =  "42.000|-85.000|41.000|-84.000"
        self.leftup   =  "44.000|-85.000|43.000|-84.000"
        self.rightdown = "42.000|-83.000|41.000|-82.000"
        self.rightup =   "44.000|-83.000|43.000|-82.000"

    def teardown(self):
        geobox2.SCOPE_SIZES = self.oldscopes

    def testonebox(self):
        "with point in middle of scope, should be no adjacent boxes added"
        lat = _dec(42.5)
        lon = _dec(-83.5)
        pt = geobox2.Geobox(lat, lon)
        boxes = pt.storage_geoboxes()
        eq_([self.center], boxes)

    def testappendleft(self):
        "with point near left edge, we expect an extra box to the left"
        lat = _dec(42.5)
        lon = _dec(-83.8)
        pt = geobox2.Geobox(lat, lon)
        boxes = pt.storage_geoboxes()
        eq_([self.center, self.left], boxes)

    def testappendright(self):
        "with point near right edge, we expect an extra box to the right"
        lat = _dec(42.5)
        lon = _dec(-83.2)
        pt = geobox2.Geobox(lat, lon)
        boxes = pt.storage_geoboxes()
        eq_([self.center, self.right], boxes)

    def testappendup(self):
        "with point near top edge, we expect an extra box to the top"
        lat = _dec(42.8)
        lon = _dec(-83.5)
        pt = geobox2.Geobox(lat, lon)
        boxes = pt.storage_geoboxes()
        eq_([self.center, self.up], boxes)

    def testappenddown(self):
        "with point near bottom edge, we expect an extra box to the bottom"
        lat = _dec(42.2)
        lon = _dec(-83.5)
        pt = geobox2.Geobox(lat, lon)
        boxes = pt.storage_geoboxes()
        eq_([self.center, self.down], boxes)

    def testappendbottomleft(self):
        "with point near bottom left edge, we expect extra boxes for the corner"
        lat = _dec(42.2)
        lon = _dec(-83.8)
        pt = geobox2.Geobox(lat, lon)
        boxes = pt.storage_geoboxes()
        eq_(sorted([self.center, self.left, self.down, self.leftdown]), sorted(boxes))

    def testappendtopleft(self):
        "with point near top left edge, we expect extra boxes for the corner"
        lat = _dec(42.8)
        lon = _dec(-83.8)
        pt = geobox2.Geobox(lat, lon)
        boxes = pt.storage_geoboxes()
        eq_(sorted([self.center, self.left, self.up, self.leftup]), sorted(boxes))

    def testappendbottomright(self):
        "with point near bottom right edge, we expect extra boxes for the corner"
        lat = _dec(42.2)
        lon = _dec(-83.2)
        pt = geobox2.Geobox(lat, lon)
        boxes = pt.storage_geoboxes()
        eq_(sorted([self.center, self.right, self.down, self.rightdown]), sorted(boxes))

    def testappendtopright(self):
        "with point near top left edge, we expect extra boxes for the corner"
        lat = _dec(42.8)
        lon = _dec(-83.2)
        pt = geobox2.Geobox(lat, lon)
        boxes = pt.storage_geoboxes()
        eq_(sorted([self.center, self.right, self.up, self.rightup]), sorted(boxes))

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




        


    