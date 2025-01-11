# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/battle_loading.py
from grinch.skeletons.battle_controller import IGrinchController
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading
from helpers import dependency

class GrinchBattleLoading(BattleLoading):
    _grinchController = dependency.descriptor(IGrinchController)

    def _populate(self):
        super(GrinchBattleLoading, self)._populate()
        self.as_setTipS(self._grinchController.prbHintManager.getHintText())
        self._grinchController.prbHintManager.incrementAndSave()

    def invalidateArenaInfo(self):
        pass

    def _setTipsInfo(self):
        pass

    def _addArenaTypeData(self):
        pass
