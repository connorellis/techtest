from tech_test import *
import unittest


class ExampleTest(unittest.TestCase):
    """
    Contained here are some example unit tests.
    Requires a lot of fleshing out but is mostly just to prove the idea.

    Note: It is common to stub out external interfaces when testing functional code and to have
        a separate suite of tests for verifying interfaces
    """
    def test_test(self):
        assert 1 == 1

    # test a bad input gives us an Assertion error
    def test_bad_intput(self):

        exception = None
        try:
            get_artist_id("I'm a test input", {})
        except AssertionError as e:
            exception = e

        assert exception.__class__ == AssertionError

