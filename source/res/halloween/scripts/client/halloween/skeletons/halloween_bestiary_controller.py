# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/skeletons/halloween_bestiary_controller.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from typing import Tuple, Optional
    from Event import Event
    from halloween_common.configs.halloween_bestiary import BestiaryModel, EnemyModel
    from halloween.gui.game_control.halloween_bestiary_controller import EnemyData

class IHalloweenBestiaryController(IGameController):
    onSettingsUpdate = None

    def _getConfig(self):
        raise NotImplementedError

    def getEnemyByIntCD(self, intCD):
        raise NotImplementedError

    def getEnemyByToken(self, token):
        raise NotImplementedError

    def getTokenIdxByEnemy(self, enemy):
        raise NotImplementedError

    @property
    def enemies(self):
        raise NotImplementedError

    def hasEnemy(self, token):
        raise NotImplementedError

    def getFirstNewEnemy(self):
        raise NotImplementedError

    @property
    def hasUnlockedEnemies(self):
        raise NotImplementedError

    @property
    def isBestiaryPostponed(self):
        raise NotImplementedError

    @isBestiaryPostponed.setter
    def isBestiaryPostponed(self, value):
        raise NotImplementedError
