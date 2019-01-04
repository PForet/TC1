import pytest
from tc1.state import GameState
from tc1.engine import Engine
from collections import defaultdict
from copy import deepcopy

import pdb

class Tester:
    def __init__(self, initial_state):
        """
        Most of the code of this module is tested by comparing simulations obtained
        with this code to the actual simulation extracted from Correlation one's
        website. This class can be used to easily compare a round of the game between
        our version and the official one.
        Arguments:
            - initial_state: A dictionnary representing the initial_state of the game
        """
        self.parse_initial_state(initial_state)
        self._callback = defaultdict(list)
        self._maxframe = 0

    def apply_position_convention(self, pos, team):
        """
        In this module, our notation for the positions start at one. However
        we compare the results with the reference engine, thus we use a zero
        indexing when declaring the tests and must convert the position between
        those conventions.
        In addition to this, when placing the units of the opposite team, we
        mirror the positions to mimic the behavior of C1 website.
        """
        if team == 's':
            return (pos[0]+1, pos[1]+1)
        elif team == 'a':
            return (28 - pos[0], 28 - pos[1])
        else:
            raise ValueError("Team must be 's' or 'a'")

    def parse_initial_state(self, initial_state):
        """
        Parse the initial state list to add the units. Bypass all
        regular tests performed by GameState.
        """
        self._state = GameState(testmode = True)
        for team, unit_name, pos in initial_state:
            pos = self.apply_position_convention(pos, team)
            self._state.add_unit(team, unit_name, pos)

    def Assert(self, when, what, which, where, how_many = 1, with_error=False):
        """
        Add a test to perform during the simulation.
        Arguments:
            - when: int, the frame when the test should be performed
            - what: string, name of the unit
            - which: char, the team ('s' for friendly, 'a' for ennemy)
            - where: tuple of int, the position of the unit
            - how_many: in case when units are superposed, how many of
                them should we test for
            - with_error: whether or not to expect an error.
        """
        where = self.apply_position_convention(where, 's') # no need to reverse so we put 's' in team
        newtest = {'what':what, 'where':where, 'which':which, 'how_many':how_many, 'raise':with_error}
        if when > self._maxframe:
            self._maxframe = when
        self._callback[when].append(newtest)

    def unit_test(self, test, log, frame_id):
        """
        Perform a unique test, given a log of the position at a given time
        """
        nmatches = 0
        team = [log['s_units'], log['a_units']][test['which'] == 'a']
        for unit in team:
            nmatches += (
                    unit['pos'][0] == test['where'][0] and
                    unit['pos'][1] == test['where'][1] and
                    unit['name'] == test['what']
                    )
        if nmatches < test['how_many']:
            error_msg = "Was looking for {} {} ({}) at pos ({},{}) and \
                    frame {}, but found only {} match(es)\n".format(
                        test['how_many'],
                        test['what'],
                        ['friendly', 'ennemy'][test['which'] == 'a'],
                        test['where'][0] - 1, test['where'][1] - 1,
                        frame_id,
                        nmatches
                        )
            error_msg += "Units on the board at this frame:\n"
            for unit in log['s_units']:
                error_msg += "Friendly: {} at ({}, {})\n".format(
                        unit['name'], unit['pos'][0] - 1, unit['pos'][1] - 1
                        )
            for unit in log['a_units']:
                error_msg += "Ennemy: {} at ({}, {})\n".format(
                        unit['name'], unit['pos'][0] - 1, unit['pos'][1] - 1
                        )
            raise ValueError(error_msg)

    def test(self):
        """
        Perform the tests declared.
        """
        # Create the engine and replace the initial default state
        self.engine = Engine()
        self.engine.game_state = self._state
        for current_frame in range(1, self._maxframe+1):
            self.engine.step()
            tests_to_perform = self._callback[current_frame]
            if not len(tests_to_perform): # no test to perform
                continue
            log = self.engine.game_state.serialize_state()
            for one_test in tests_to_perform:
                if one_test['raise']:
                    with pytest.raises(ValueError):
                        self.unit_test(one_test, log, current_frame)
                else:
                    self.unit_test(one_test, log, current_frame)

    def _save_plot(self, path):
        """Save a animation of the round up to the last rest, for
        debut purpose"""
        eng = Engine()
        eng.game_state = deepcopy(self._state)
        #pdb.set_trace()
        eng.simulate_and_show(self._maxframe, path)


def test_demo():
    """Demonstration of how to use the class above"""
    # One friendly ping at 15,1 and one ennemy EMP at 21,7. Note that we use
    # the same coordinate system when defining the units from both team
    initial_state = [('s', 'ping', (15,1)),
                     ('a', 'emp', (21,7))]
    tester = Tester(initial_state)
    # Now, when we observe the game of the website, the coordinates are reversed
    # for the ennemy. Let's start by checking that no one has moved at the frame 1
    # Remember the arguments for assert:
    # assert(self, when, what, which, where, how_many = 1, with_error=False):
    tester.Assert(when=1, what='ping', which='s', where=(15,1))
    # and with the reverse coordinates (just copy what you see on the website grid):
    tester.Assert(when=1, what='emp', which='a', where=(6,20))
    # at the second frame, only the ping has moved (due to its superior speed)
    tester.Assert(when=2, what='ping', which='s', where=(15,2))
    # now, you can also make sure that the emp has not moved, by testing for an error:
    tester.Assert(when=2, what='emp', which='a', where=(6,19), with_error=True)
    # this is particularly useful to verify that a unit has been destroyed.
    # Finally, we can check that this movement happens at frame 4:
    tester.Assert(when=4, what='emp', which='a', where=(6,19))

    # We run all tests after we defined them:
    tester.test()



def test_tester():
    """Make sure that the tester can actually raise errors!"""
    initial_state = [('s', 'ping', (15,1)),
                     ('a', 'emp', (21,7))]
    tester = Tester(initial_state)
    tester.Assert(when=1, what='ping', which='s', where=(15,1))
    # this line should raise an error:
    tester.Assert(when=1, what='emp', which='a', where=(7,20))
    with pytest.raises(ValueError):
        tester.test()





