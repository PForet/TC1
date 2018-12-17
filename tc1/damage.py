import numpy as np

def l1dist(t1,t2):
    # L1 distance for tuples
    return abs(t1[0] - t2[0]) + abs(t1[1] - t2[1])

class DamageEngine:
    def __init__(self):
        """
        This class is used to compute the damages afflicted by units to other units.
        It assume that the units were already moved
        """
        pass

    def __call__(self, state):
        """
        Inflict damages on the units according to the rules of the game.
        Assume units were moved, and that units killed in the previous
        turn are no longer in the state object.
        """
        # pairwise distances between the units of both teams
        dmat = self._get_distance_matrix(state)
        # list of pairs [a,b] where a can and should attack b
        for attacking, attacked in self._find_targets(state, dmat):
            if attacked is None: # out of range
                continue
            if attacking['id'] == 3: # scrambler
                if attacked['id'] > 3: # defensive unit
                    continue # scrambler can't attack defensive units
            attacked['stability'] -= attacking['dpf']

    def _find_targets(self, state, dmat):
        """
        Find target for all units, and return None if there is no available
        target within range. The result is a list of list of two nodes, the
        first one being the attacking unit and the second one the attacked.
        """
        # start with the friendly units
        for i,s in enumerate(state.s_units):
            target = None
            for j,a in enumerate(state.a_units):
                if dmat[i,j] < s['range']:
                    # if new node as the priority
                    if self._targeting_priority(s, target, a):
                        target = a
            yield [s, target]

        # Now match the ennemy units
        for i,a in enumerate(state.a_units):
            target = None
            for j,s in enumerate(state.s_units):
                if dmat[j,i] < a['range']:
                    # if new node as the priority
                    if self._targeting_priority(a, target, s):
                        target = s
            yield [a, target]

    def _get_distance_matrix(self, state):
        """
        Return a pairwise distance matrix between the friendly units (axis 0) and
        the ennemy units (axis 1).
        Exemple: dmat[i,j] = distance { state.s_units[i], state.a_units[j] }
        """
        nrows = len(state.s_units)
        ncols = len(state.a_units)
        dmat = np.zeros((nrows, ncols))
        for i,s in enumerate(state.s_units):
            for j,a in enumerate(state.a_units):
                dmat[i,j] = l1dist(s['pos'], a['pos'])
        return dmat

    def _targeting_priority(self, attacking_unit,  unit1, unit2):
        """
        Return true if unit2 has a higher priority than unit1 when attacked by
        'attacking_unit'.
        The priority is defined by the following rules:
            1) Prioritize Information over Firewalls
            2) Choose the nearest target(s). Note that the potential targets could
                include multiple locations if they are the same distance away.
            3) Choose the target(s) with the lowest remaining Stability
            4) Choose the target(s) which are the furthest into/towards your side of the arena
            5) Choose the target closest to an edge
        """
        # Just ignore the new unit if it's health is equal or less to zero
        if unit2['stability'] <= 0:
            return False
        # For convenience, we consider than any unit as a higher priority than None
        if unit1 is None:
            return True
        # For rule 1):
        if unit1['id'] > 3 and unit2['id'] < 4:
            return True
        # For rule 2):
        d1 = l1dist(unit1['pos'], attacking_unit['pos'])
        d2 = l1dist(unit2['pos'], attacking_unit['pos'])
        if d1 < d2:
            return False
        if d2 > d1:
            return True
        # For rule 3):
        if unit1['stability'] < unit2['stability']:
            return False
        if unit2['stability'] < unit1['stability']:
            return True
        # for rule 4):
        if attacking_unit['target'] in [2,3]: # means the attacking unit is friendly
            if unit1['pos'][1] < unit2['pos'][1]: # unit1 is closer to my side
                return False
            if unit1['pos'][1] > unit2['pos'][1]: # unit2 is closer
                return True
        else: # attacking unit is not friendly
            if unit1['pos'][1] < unit2['pos'][1]: # unit1 is closer to my side
                return True
            if unit1['pos'][1] > unit2['pos'][1]: # unit2 is closer
                return False
        # For rule 5):
        # this one rule is not super clear, I assume it means to look at the x coordinate
        if min(unit1['pos'][0], 30 - unit1['pos'][0]) < min(unit2['pos'][0], 30 - unit2['pos'][0]):
            return False # unit 1 closer to an edge
        return True





