from tc1.engine import Engine

myengine = Engine()

for p in range(19):
    myengine.game_state.add_unit('a', 'filter', (p+1, 15))

myengine.game_state.add_unit('s', 'ping', (10,5))
myengine.game_state.add_unit('s', 'emp', (10,5))
myengine.game_state.add_unit('s', 'ping', (17, 3))

"""
myengine.game_state.add_unit('s', 'filter', (0,13))
myengine.game_state.add_unit('s', 'destructor', (13,7))
myengine.game_state.add_unit('s', 'encryptor', (13,4))
myengine.game_state.add_unit('a', 'ping', (15,19))
myengine.game_state.add_unit('a', 'emp', (15, 21))
myengine.game_state.add_unit('a', 'scrambler', (15, 23))
myengine.game_state.add_unit('s', 'emp', (15, 7))
"""

myengine.simulate_and_show(80, 'tmp')

