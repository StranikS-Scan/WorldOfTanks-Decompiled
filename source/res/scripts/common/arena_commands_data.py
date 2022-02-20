# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/arena_commands_data.py
from collections import namedtuple
HESH_MAP_SIZE = 1000
HESH_GRID_STEP = 6
MAX_POSE_SIZE = HESH_MAP_SIZE / HESH_GRID_STEP

def getHashCode(pose):
    return sum([ int(coord + HESH_MAP_SIZE * 0.5 + 0.5) / HESH_GRID_STEP * MAX_POSE_SIZE ** i for i, coord in enumerate(pose) ])


class ArenaCommandData(namedtuple('ArenaCommandData', ['commandName',
 'position',
 'owner',
 'name',
 'state'])):

    @staticmethod
    def getCommandData(*args, **kwargs):
        if kwargs:
            data = ArenaCommandData(kwargs.get('commandName', 'PREBATTLE_WAYPOINT'), kwargs.get('position', (0.0, 0.0, 0.0)), kwargs.get('team', '') or kwargs.get('teams', 'both'), kwargs.get('name', '') or kwargs.get('locationName', 'ERROR'), kwargs.get('state', 'IDLE'))
            return (getHashCode(kwargs['position']), data)
        else:
            return None


ArenaCommandData.__new__.__defaults__ = (None,) * len(ArenaCommandData._fields)
