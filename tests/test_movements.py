import pytest
from tc1.state import GameState
from tc1.engine import Engine
from .test_utils import Tester

def test_movementNoObstacles():
    """Basic test for speed and direction of units when there is no obstacles"""
    initial_state = [('s','ping',(25,11)),
            ('s','emp',(13,0)),
            ('s','scrambler',(3,10))]
    tester = Tester(initial_state)
    tester.Assert(when=104,what='scrambler',which='s',where=(16,23))
    tester.Assert(when=107,what='scrambler',which='s',where=(16,23))
    tester.Assert(when=21,what='ping',which='s',where=(20,16))
    tester.Assert(when=21,what='emp',which='s',where=(15,3))
    tester.Assert(when=21,what='scrambler',which='s',where=(5,13))
    tester.test()


def test_borderInteraction():
    """Test if units dissapear correctly when they meet a border"""
    initial_state = [('s','ping',(25,11)),
            ('s','emp',(13,0)),
            ('s','scrambler',(3,10))]
    tester = Tester(initial_state)
    # test for the ping
    tester.Assert(when=55,what='ping',which='s',where=(12,25))
    tester.Assert(when=57,what='ping',which='s',where=(11,25))
    tester.Assert(when=58,what='ping',which='s',where=(11,25), with_error=True)
    # test for the scrambler
    tester.Assert(when=111,what='scrambler',which='s',where=(16,24))
    tester.Assert(when=115,what='scrambler',which='s',where=(17,24))
    tester.Assert(when=116,what='scrambler',which='s',where=(17,24),with_error=True)
    # test for the emp
    tester.Assert(when=111,what='emp',which='s',where=(26,14))
    tester.Assert(when=115,what='emp',which='s',where=(27,14))
    tester.Assert(when=116,what='emp',which='s',where=(27,14),with_error=True)
    tester.test()


def test_movementObstacles1():
    """Test for movement with a linear line of filters"""
    initial_state = [('s','filter',(25,13))]
    for i in range(24):
        initial_state.append(('s','filter',(i,13)))
    initial_state += [('s','ping',(1,12))]
    initial_state += [('s','ping',(16,2))]
    # assert for the path:
    tester = Tester(initial_state)
    tester.Assert(37,'ping','s',(21,10))
    tester.Assert(37,'ping','s',(24,12))

    tester.Assert(38,'ping','s',(21,11))
    tester.Assert(38,'ping','s',(24,13))

    tester.Assert(33,'ping','s',(17,12))
    tester.Assert(33,'ping','s',(24,10))

    tester.Assert(51,'ping','s',(24,14))
    tester.Assert(51,'ping','s',(21,7))

