# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/Scaleform/daapi/view/battle/races/races_battle_loading.py
from gui.Scaleform.daapi.view.meta.RacesBattleLoadingMeta import RacesBattleLoadingMeta
from gui.impl import backport
from gui.impl.gen import R

class RacesBattleLoading(RacesBattleLoadingMeta):

    def _populate(self):
        super(RacesBattleLoading, self)._populate()
        self.as_setTipsS([backport.text(R.strings.races_battle_loading.racesBattleLoading.tip1()), backport.text(R.strings.races_battle_loading.racesBattleLoading.tip2()), backport.text(R.strings.races_battle_loading.racesBattleLoading.tip3())])

    def invalidateArenaInfo(self):
        pass

    def _setTipsInfo(self):
        pass

    def _addArenaTypeData(self):
        pass
