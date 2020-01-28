# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bob/battle_loading.py
from helpers import dependency
from shared_utils import first
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading
from gui.Scaleform.daapi.view.meta.BobBattleLoadingMeta import BobBattleLoadingMeta
from gui.battle_control.arena_info import vos_collections

class BobBattleLoading(BattleLoading, BobBattleLoadingMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(BobBattleLoading, self)._populate()
        arenaDP = self.sessionProvider.getArenaDP()
        self.as_setBloggerIdsS(self.__getBloggerId(vos_collections.AllyItemsCollection().iterator(arenaDP)), self.__getBloggerId(vos_collections.EnemyItemsCollection().iterator(arenaDP)))

    def __getBloggerId(self, vehiclesIterator):
        vehicleVO = first(vehiclesIterator)
        return vehicleVO[0].bobInfo.bloggerID if vehicleVO and vehicleVO[0].bobInfo else 0
