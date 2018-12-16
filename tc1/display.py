from matplotlib import pyplot as plt
from celluloid import Camera
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
        for x in range(self.PADDED_GRID_SIZE):
            for y in range(self.PADDED_GRID_SIZE):
                idx = self._grid[x,y]
                s, args = self._get_symbol(idx)
                plt.text(x, y, s, horizontalalignment='center',
                        verticalalignment='center', **args)
        self.camera.snap()

    def animate_logs(self, logs, saveas = None):
        self.camera = Camera(plt.figure(figsize = (8,8)))
        for l in logs:
            self.update_state(l)
            self._plot_one_state()
        anim = self.camera.animate(blit=False)
        if saveas is not None:
            anim.save(saveas + '.mp4')
