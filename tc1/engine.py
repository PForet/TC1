from .mapgraph import MapGraph
from .state import GameState
from .display import Matplotlib_display

class Engine:
    def __init__(self):
        """
        Class to contain and operate on the GameState
        """
        # The gamestate contains every units, the pv and resources
        self.game_state = GameState()
        # The MapGrpah contains the functions need to move the units
        self.map_graph = MapGraph()
        # The grid is only used to vizualize the fight and should not be
        # called during training
        self.display_util = Matplotlib_display()

    def simulate_and_show(self, nstepsmax, savepath=None):
        _logs = []
        for _ in range(nstepsmax):
            self.map_graph(self.game_state)
            _logs.append(self.game_state.serialize_state())

        self.display_util.animate_logs(_logs, savepath)

