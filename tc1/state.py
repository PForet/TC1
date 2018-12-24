from .unit_desc import UNITS_DESC
from copy import deepcopy

class GameState:
    def __init__(self, testmode = False):
        self.INITIALE_HEALTH = 30
        self.INITIALE_CORE = 5
        self.INITIALE_BITS = 6

        self.FRIENDLY_BORDERS = [(15-i, i) for i in range(1,15)]
        self.FRIENDLY_BORDERS += [(14+i, i) for i in range(1,15)]
        self.ENNEMY_BORDERS = [(i, 14+i) for i in range(1,15)]
        self.ENNEMY_BORDERS += [(29-i, 14+i) for i in range(1,15)]

        self.s_health = self.INITIALE_HEALTH
        self.a_health = self.INITIALE_HEALTH

        self.s_core = self.INITIALE_CORE
        self.a_core = self.INITIALE_CORE

        self.s_bits = self.INITIALE_BITS
        self.a_bits = self.INITIALE_BITS

        self.s_units = []
        self.a_units = []

    def serialize_state(self):
        """
        Serialize the current state of the game
        """
        dct = { 's_health':self.s_health,
                'a_health':self.a_health,
                's_core':self.s_core,
                'a_core':self.a_core,
                's_bits':self.s_bits,
                'a_bits':self.a_bits,
                's_units':self.s_units,
                'a_units':self.a_units}

        return deepcopy(dct)

    def _raise(self, error):
        """
        Raise a ValueError, except if the state is in testmode. The testmode
        is only used to bypass all the test in order to test the engine
        more easily. When using the engine to developpe a model, the testmode
        should always be desactivated for safety
        """
        if not self.testmode:
            raise ValueError(error)

    def add_unit(self, team, unit_name, pos):
        """
        Function to add a new unit to the current game
        Will check if the offensive units are placed on
        the borders.
        WARNING: We use the "padded notation" for the coordinates which is
        differente from the official API. (ours if from 1 to 29)
        """
        # team must be s (allies) of a (ennemies)
        assert team in ['s', 'a']
        # copy the basic stats of the unit
        spec = dict(UNITS_DESC[unit_name])
        # add the position to the stat dict
        spec['pos'] = pos

        # now check if the unit is an offensive one, and check its
        # position if so
        if spec['id'] < 4: # offensive id's all 3 or below
            if team == 's' and pos not in self.FRIENDLY_BORDERS:
                self._raise('Offensive unit must be placed of borderds, but got position {}'.format(pos))
            if team == 'a' and pos not in self.ENNEMY_BORDERS:
                self._raise('Offensive unit must be placed of borderds, but got position {}'.format(pos))
            # now we define the target border, as offensive units
            # will try to move toward the ennemy border on the
            # opposite side of the board.
            if team == 's':
                if pos[0] < 15:
                    spec['target'] = 2 # nums start from 2 to 5 in trig. order
                else:
                    spec['target'] = 3
            else:
                if pos[0] < 15:
                    spec['target'] = 5
                else:
                    spec['target'] = 4
        # now check if defensive units has been placed in the right
        # side of the arena
        else:
            if team == 's' and pos[1] > 14:
                self._raise('Defensive unit must be placed in your side, but got position {}'.format(pos))
            if team == 'a' and pos[1] < 15:
                self._raise('Defensive unit must be placed in your side, but got position {}'.format(pos))

        # To know where to move when two nodes are equally close to the border, we need to
        # maintain a variable for the previous move
        spec['previous_move'] = None

        # Units does not move every turn, thus we must count for how many turn
        # it hasn't moved. Counter is initialized to zero (so ping will the second frame)
        # such as in C1 engine
        spec['n_turns_static'] = 0

        if team == 's':
            self.s_units.append(spec)
        else:
            self.a_units.append(spec)

    def remove_dead_units(self):
        """
        Remove units whose stability has reached zero
        """
        self.a_units = [u for u in self.a_units if u['stability']>0]
        self.s_units = [u for u in self.s_units if u['stability']>0]

