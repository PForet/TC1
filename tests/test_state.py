import pytest
from tc1.state import GameState

def test_defensiveAssertions():
    """Make sure that the gamstate raise an error when the player attemps
    a move that is against the rules.
    We use the indexing starting from 1 here"""
    s = GameState()
    # place friendly defensive unit in the right side:
    s.add_unit('s', 'filter', (1,14))
    s.add_unit('s', 'filter', (28,14))
    # should fail if done with ennemy units:
    with pytest.raises(ValueError):
        s.add_unit('a', 'filter', (1,14))
        s.add_unit('a', 'filter', (28,14))
    # can place offensive units
    s.add_unit('s', 'ping', (10,5))
    with pytest.raises(ValueError):
        s.add_unit('s', 'ping', (10,6))
    with pytest.raises(ValueError):
        s.add_unit('s', 'ping', (9,5))

    # same things but from the point of view of the ennemy:
    s.add_unit('a', 'filter', (1,15))
    s.add_unit('a', 'filter', (28,15))
    # should fail if done with ennemy units:
    with pytest.raises(ValueError):
        s.add_unit('s', 'filter', (1,15))
        s.add_unit('s', 'filter', (28,15))
    # can place offensive units
    s.add_unit('a', 'ping', (23,20))
    with pytest.raises(ValueError):
        s.add_unit('a', 'ping', (23,19))
    with pytest.raises(ValueError):
        s.add_unit('a', 'ping', (22,20))


