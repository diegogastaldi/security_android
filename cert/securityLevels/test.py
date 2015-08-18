#!/usr/bin/python2
import unittest
from pprint import pprint
from partial_order import *
from security_levels import *
import sys

#The setUp() method runs before every test.
#The tearDown() method runs after every test.
#python -m unittest discover -s /home/diego/didfail/cert/securityLevels/ -p 'test.py'

class Test_partial_order(unittest.TestCase):
    def setUp(self):
        self.order = Partial_order()
        self.order.add_relation(("Public", "Semi-private1"))
        self.order.add_relation(("Public", "Semi-private2"))
        self.order.add_relation(("Public", "Semi-private3"))
        self.order.add_relation(("Public", "Semi-public1"))
        self.order.add_relation(("Public", "Semi-public2"))
        self.order.add_relation(("Public", "Semi-public3"))
        self.order.add_relation(("Public", "Private"))
        self.order.add_relation(("Public", "Public"))
        self.order.add_relation(("Semi-public1", "Private"))
        self.order.add_relation(("Semi-public2", "Private"))
        self.order.add_relation(("Semi-public3", "Private" ))
        self.order.add_relation(("Semi-public1", "Semi-public1"))
        self.order.add_relation(("Semi-public2", "Semi-public2"))
        self.order.add_relation(("Semi-public3", "Semi-public3"))
        self.order.add_relation(("Semi-public1", "Semi-private1"))
        self.order.add_relation(("Semi-public2", "Semi-private2"))
        self.order.add_relation(("Semi-public3", "Semi-private3"))
        self.order.add_relation(("Semi-private1", "Private"))
        self.order.add_relation(("Semi-private2", "Private"))
        self.order.add_relation(("Semi-private3", "Private" ))
        self.order.add_relation(("Semi-private1", "Semi-private1"))
        self.order.add_relation(("Semi-private2", "Semi-private2"))
        self.order.add_relation(("Semi-private3", "Semi-private3"))
        self.order.add_relation(("Private", "Private"))

    def test_bottom(self):
        self.assertEqual(self.order.bottom(), "Public")

    def test_supremum(self):
        self.assertEqual(self.order.supremum(set(["Public"])), "Public")
        self.assertEqual(self.order.supremum(set(["Semi-private3", "Semi-public2"])), "Private")
        self.assertEqual(self.order.supremum(set(["Semi-private3", "Semi-public3"])), "Semi-private3")
        self.assertEqual(self.order.supremum(set(["Semi-private3", "Semi-public3","Semi-public2"])), "Private")

class Test_security_levels(unittest.TestCase):
    def setUp(self):
        check_levels = Check_levels()

    def test_get_level(self):

    def test_check_level(self):

class Test_tract_constr_finite_slattice(unittest.TestCase):
    def setUp(self):

    def test_check(self):

    def test_initialize(self):

    def test_tract_const_finite_semilattice(self):

if __name__ == '__main__':
    unittest.main() 
