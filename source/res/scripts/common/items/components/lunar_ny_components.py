# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/lunar_ny_components.py
from items.components.lunar_ny_constants import CharmBonusMsk

class CharmDescriptor(object):
    __slots__ = ('__cfg',)

    def __init__(self, cfg):
        cfg.setdefault('bonusMsk', CharmBonusMsk.NONE)
        cfg.setdefault('bonuses', {})
        self.__cfg = cfg

    def __getattr__(self, name):
        try:
            return self.__cfg[name]
        except KeyError:
            raise AttributeError

    def hasBonuses(self, bonuses):
        return bonuses & self.__cfg['bonusMsk'] == bonuses

    def numBonuses(self):
        return len(self.__cfg['bonuses'].keys())
