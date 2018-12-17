from matplotlib import pyplot as plt
import numpy as np

class Matplotlib_display:
    def __init__(self):
        self.GRID_SIZE = 28
        self.PADDED_GRID_SIZE = 30

    def _make_grid(self):
        self._grid = -1 * np.ones((self.PADDED_GRID_SIZE,
            self.PADDED_GRID_SIZE))
        for i in range(15):
            for j in range(15 - i, 15 + i):
                self._grid[i,j] = 0
                self._grid[30 - i - 1, j] = 0

    def update_state(self, newstate):
        self._make_grid()
        # update for friendly units
        for su in newstate['s_units']:
            x,y = su['pos']
            self._grid[x, y] = su['id']
        # update for ennemy units
        for au in newstate['a_units']:
            x,y = au['pos']
            self._grid[x, y] = 6 + au['id']
        # Also log the health of the players:
        self.s_health = newstate['s_health']
        self.a_health = newstate['a_health']
        # log the health of all units
        self.s_units_health = [(u['pos'], u['stability']) for u in newstate['s_units']]
        self.a_units_health = [(u['pos'], u['stability']) for u in newstate['a_units']]

    def _get_symbol(self, x):
        args = {}
        if x == -1: #out of border
            args['alpha'] = 0.8
            return 'x', args
        if x == 0: # empty
            args['alpha'] = 0.6
            return '.', args
        if x > 6: # color according to the team
            args['color'] = 'red'
            x -= 6
        else:
            args['color'] = 'blue'
        if x == 1: # ping
            s = 'p'
            args['size'] = 10
        elif x == 2: # EMP
            s = 'm'
            args['size'] = 10
        elif x == 3: # scrambler
            s = 's'
            args['size'] = 10
        elif x == 4: # filter
            s = 'f'
            args['size'] = 10
        elif x == 5: # encryptor
            s = 'e'
            args['size'] = 10
        elif x == 6: # destructor
            s = 'd'
            args['size'] = 10
        else:
            raise ValueError("Should not have been here")
        return s, args

    def _plot_one_state(self):
        plt.xlim(0,29)
        plt.ylim(0,29)
        # Plot the grid and the units
        for x in range(self.PADDED_GRID_SIZE):
            for y in range(self.PADDED_GRID_SIZE):
                idx = self._grid[x,y]
                s, args = self._get_symbol(idx)
                plt.text(x, y, s, horizontalalignment='center',
                        verticalalignment='center', **args)
        # Print the health too
        s = 'Ally health: {}'.format(self.s_health)
        plt.text(0, 0, s, horizontalalignment='left', verticalalignment='bottom',
                bbox = dict(boxstyle='square', facecolor='white', alpha=1))
        s = 'Ennemy health: {}'.format(self.a_health)
        plt.text(0, 2, s, horizontalalignment='left', verticalalignment='bottom',
                bbox = dict(boxstyle='square', facecolor='white', alpha=1))
        # Add rectangles for the health
        xs,ys = zip(*[e[0] for e in self.s_units_health])
        xa,ya = zip(*[e[0] for e in self.a_units_health])
        size_s = [4*x[1] for x in self.s_units_health]
        size_a = [4*x[1] for x in self.a_units_health]
        plt.scatter(xs,ys,alpha=0.3,color='blue',s=size_s)
        plt.scatter(xa,ya,alpha=0.3,color='red',s=size_a)

        self.camera.snap()

    def animate_logs(self, logs, saveas = None):
        self.camera = Camera(plt.figure(figsize = (8,8)))
        for l in logs:
            self.update_state(l)
            self._plot_one_state()
        anim = self.camera.animate(blit=False)
        if saveas is not None:
            anim.save(saveas + '.mp4')



# Code taken from https://github.com/jwkvam/celluloid/blob/master/celluloid.py as a temporary fix

from typing import Dict, List
from collections import defaultdict

from matplotlib.figure import Figure
from matplotlib.artist import Artist
from matplotlib.animation import ArtistAnimation

class Camera:
    """Make animations easier."""

    def __init__(self, figure: Figure) -> None:
        """Create camera from matplotlib figure."""
        self._figure = figure
        # need to keep track off artists for each axis
        self._offsets: Dict[str, Dict[int, int]] = {
            k: defaultdict(int) for k in [
                'collections', 'patches', 'lines', 'texts', 'artists', 'images'
            ]
        }
        self._photos: List[List[Artist]] = []

    def snap(self) -> List[Artist]:
        """Capture current state of the figure."""
        frame_artists: List[Artist] = []
        for i, axis in enumerate(self._figure.axes):
            if axis.legend_ is not None:
                axis.add_artist(axis.legend_)
            for name in self._offsets:
                new_artists = getattr(axis, name)[self._offsets[name][i]:]
                frame_artists += new_artists
                self._offsets[name][i] += len(new_artists)
        self._photos.append(frame_artists)
        return frame_artists

    def animate(self, *args, **kwargs) -> ArtistAnimation:
        """Animate the snapshots taken.
        Uses matplotlib.animation.ArtistAnimation
        Returns
        -------
        ArtistAnimation
        """
        return ArtistAnimation(self._figure, self._photos, *args, **kwargs)
