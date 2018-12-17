from matplotlib import pyplot as plt
import numpy as np
from queue import Queue

class MapGraph:
    def __init__(self):
        self.INTMAX = 30 * 30 + 1 # max dist in graph
        self._make_grid()

    def _make_grid(self):
        """
        Create the internal grid used for BFS
        Empty nodes are denoted with a 0
        Node outside of the map are denoted with -1
        Borders are denoted 2 and 3 for ennemy borders and
        3 and 5 for friendly borders
        """
        self.PADDED_GRID_SIZE = 30
        self._grid_template = -1 * np.ones((self.PADDED_GRID_SIZE,
            self.PADDED_GRID_SIZE))
        self._dtemplate= -1 * np.ones((self.PADDED_GRID_SIZE,
            self.PADDED_GRID_SIZE))

        # carve the grid
        for i in range(15):
            for j in range(15 - i, 15 + i):
                self._grid_template[i,j] = 0
                self._grid_template[30 - i - 1, j] = 0
                self._dtemplate[i,j] = self.INTMAX
                self._dtemplate[30 - i - 1, j] = self.INTMAX

    def get_frontier_nodes(self, frontier_id):
        """
        Return a list of tuple representing the coordinates
        of the nodes composing a given frontier
        """
        # create the first friendly border:
        if frontier_id == 4:
            return ((15-i, i) for i in range(1,15))
        # create the second friendly border:
        if frontier_id == 5:
            return ((14+i, i) for i in range(1,15))
        # create the first ennemy border:
        if frontier_id == 3:
            return ((i, 14+i) for i in range(1,15))
        # create the second ennemy border:
        if frontier_id == 2:
            return ((29-i, 14+i) for i in range(1,15))
        raise ValueError("Wrong border id: {}".format(frontier_id))

    def get_dijkstra(self, border_id):
        """
        Apply Dijkstra algorithm to compute, for each node,
        the minimum distance to a given frontier. This is less
        efficient than a A* seach for one unit, but the same map
        can be used by all units.
        Unreachable nodes are given the value self.MAXINT
        """
        q = Queue()
        distance_graph = self._dtemplate.copy()
        # Initialize the queue
        if isinstance(border_id, int): # if we get an int, we're looking for a border
            initial_nodes = self.get_frontier_nodes(border_id)
            for n in initial_nodes:
                # check if the starting node is on a defensive unit
                if self._grid[n[0], n[1]]:
                    continue
                distance_graph[n[0], n[1]] = 0
                q.put(n)
        elif isinstance(border_id, tuple): # Looking for a path to a custom node
            cx,cy = border_id
            if self._grid[cx,cy]:
                raise ValueError("Can't compute a path to occupied node ({},{})".format(cx,cy))
            distance_graph[cx,cy] = 0
            q.put((cx,cy))
        # BFS on the graph
        while not q.empty():
            nx, ny = q.get()
            c = distance_graph[nx, ny]
            for dx, dy in [(-1,0), (1,0), (0, -1), (0, 1)]:
                # check if the node is occupied by a defense unit
                if self._grid[nx+dx, ny+dy]:
                    continue
                if distance_graph[nx+dx, ny+dy] > c + 1:
                    distance_graph[nx+dx, ny+dy] = c + 1
                    q.put((nx+dx, ny+dy))
        return distance_graph

    def update_state(self, state):
        self._grid = self._grid_template.copy()

        # update for friendly units
        for su in state.s_units:
            if su['id'] > 3: # only populate grid for defensive units
                x,y = su['pos']
                self._grid[x, y] = su['id']

        # update for ennemy units
        for au in state.a_units:
            if au['id'] > 3:
                x,y = au['pos']
                self._grid[x, y] = 6 + au['id']

    def recompute_distance_maps(self):
        """
        Recompute the distance matrix for each frontier. Must be called
        each time a devensive unit is created/destroyed.
        """
        self.distance_maps = {i:self.get_dijkstra(i) for i in [2,3,4,5]}

    def __call__(self, state):
        """
        Move the units in state according to the rules of the game.
        Should modify state by reference (please ?)
        """
        # we recompute the distance map each time now
        self.update_state(state) # this change the accessible nodes bases on def.
        self.recompute_distance_maps()

        events = []
        for s_unit in state.s_units:
            events += self._move_one(s_unit)
        for e in events:
            if e[0] == 'score':
                state.a_health -= 1 # Ennemy lose 1 health point

        events = []
        for a_unit in state.a_units:
            events += self._move_one(a_unit)
        for e in events:
            if e[0] == 'score':
                state.s_health -= 1 # We lose 1 health point


    def _move_one(self, unit):
        """
        Move only one unit according to the rules of the game
        Return a list of events that occured during the move
        (for now, only a scoring event if the unit reached the border)
        """
        # If the unit is a defensive unit, do nothing
        if unit['id'] > 3:
            return []
        # Else, we first increment the counter to see if the unit should move:
        unit['n_turns_static'] += 1
        # Check if it is the right moment to move
        if unit['n_turns_static'] <  unit['speed']:
           return []
        # The unit can move. First, reinitialize its counter to zero
        unit['n_turns_static'] = 0
        # Now it the unit is at a distance 0 of its border, it scores.
        # The unit is deleted and we return the event 'scored' to recognize
        # that (along with the last position of the unit)
        # We also put the life of the unit to zero so that it can be removed later
        dmat = self.distance_maps[unit['target']]
        last_x, last_y = unit['pos']
        if not dmat[last_x, last_y]: # true if zero
            last_x, last_y = unit['pos']
            unit['stability'] = 0
            return [('score', (last_x, last_y))]
        # else we just move the unit according to the direction algorithm
        new_x, new_y = self.get_direction(unit)
        unit['pos'] = (new_x, new_y)
        return []


    def find_deepest_position(self, unit):
        """
        Find the deepest position into the ennemy territory to self-destruct
        here. We follow the official rule:
             The deepest location is the location with the furthest Y coordinate
             from your territory. If multiple such locations are reachable, the
             Unit will choose the one closest to its target
        """
        # For now, we do a BFS to find all the accessible nodes, before picking the
        # best one. We don't memorize the result, so there might be efficiency issues
        q = Queue(); q.put(unit['pos']); visited = set(); bestx, besty = unit['pos']
        while q.not_empty():
            x,y = q.get()
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                if self._grid[x+dx,y+dy] or (x+dx, y+dy) in visited:
                    continue
                q.put((x+dx, y+dy)); visited.add((x+dx, y+dy))
        # Now find the best node by iterating on the set of visited nodes
        prefered_directions = {
                2:(1,1), # If target border is 2, we prefer the big x and y coordinates
                3:(-1,1), 4:(-1,-1), 5:(1,1)
                }
        px,py = prefered_directions[unit['target']]
        for sx,sy in visited:
            if sy*py > besty*py: # The y coordinate has priority when selecting the best node
                besty = sy; bestx = sx
            elif sy == besty:
                if sx*px > bestx*px: # If equality on y coordinate, look for best x
                    bestx = sx
        return bestx, besty

    def get_direction(self, unit):
        """
        Return a couple (x,y) giving the optimal mouvement for
        a unit, according to the games rules.
        For now, undefined behavior when the frontier is not accessible
        """
        cx, cy = unit['pos']
        # First, check if the target border is accessible
        target_border = unit['target']
        d_map = self.distance_maps[target_border]
        # If our position on the distance map is +inf, then we can't access
        # the target border and we must find a place to self destruct
        if d_map[cx, cy] == self.INTMAX:
            # We find the deepest accessible position
            tx, ty = self.find_deepest_position(unit)
            d_map = self.get_dijkstra((tx, ty))
        # Now that we get the distance map, we can find the prefered movement
        # according to the rules
        mindist = self.INTMAX
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            if self._grid[cx+dx, cy+dy]: # non accessible node
                continue
            if d_map[cx+dx, cy+dy] < mindist:
                possible_deltas = [(dx,dy)]
                mindist = d_map[cx+dx, cy+dy]
            elif d_map[cx+dx, cy+dy] == mindist:
                possible_deltas.append((dx, dy))

        # If we only have one choice, we don't have any more things to consider:
        if len(possible_deltas) == 1:
            DX,DY = possible_deltas[0]
            unit['previous_move'] = (DX,DY) # to know where to move next turn
            return (cx+DX, cy+DY)

        # Else, we move in the another direction than the previous move
        # Case 1: "In the case where a Unit has just been deployed and has
        # yet to move, it will prefer a vertical movement."
        if unit['previous_move'] is None:
            vertical_deltas = [(dx,dy) for dx,dy in possible_deltas if dx==0]
            assert len(vertical_deltas) == 1 # should always be verified ?
            DX,DY = vertical_deltas[0]
            unit['previous_move'] = (DX,DY) # to know where to move next turn
            return (cx+DX, cy+DY)

        # Case 2: If multiple tiles are equally close to the units destination,
        # move in the opposite direction of the previous movement. For example,
        # if the Unit made a vertical move on its previous step, it will prefer
        # a horizontal move.
        aodx = abs(unit['previous_move'][0]) # 1 if last move was horizontal
        prefered_deltas = [(dx,dy) for dx,dy in possible_deltas if abs(dx)!=aodx]
        if len(prefered_deltas) == 1:
            DX,DY = prefered_deltas[0]
            unit['previous_move'] = (DX,DY)
            return (cx+DX, cy+DY)

        # Case 3: This on is super edgy..
        # If there are two tiles with equal distances and are equally prefered
        # based on direction, the unit will choose one that is in the direction
        # of it's target edge
        # Targets 2 -> big x, big y
        # Targets 3 -> small x, big y
        # Targets 4 -> small x, small y
        # Targets 5 -> big x, small y
        PREFERED_LOC = {2:[(0,1), (1,0)],
                3:[(0,1), (-1,0)],
                4:[(0,-1), (-1,0)],
                5:[(0,-1), (1,0)]}
        for px,py in PREFERED_LOC[unit['target']]:
            if (px,py) in prefered_deltas:
                unit['previous_move'] = (px,py)
                return (cx+px, cy+py)
        raise ValueError("Give up on position {},{}".format(cx,cy))

    def debug_print(self, grid_type):
        """
        gridtype = 0 for original map and other integer foe
        distance maps
        """
        if grid_type == 0:
            M = self._grid
        else:
            M = self.distance_maps[grid_type]

        plt.figure(figsize=(8,8))
        plt.xlim(0,29)
        plt.ylim(0,29)

        for x in range(self.PADDED_GRID_SIZE):
            for y in range(self.PADDED_GRID_SIZE):
                s = '{}'.format(int(M[x,y]))
                plt.text(x, y, s, horizontalalignment='center',
                        verticalalignment='center')
        plt.show()



