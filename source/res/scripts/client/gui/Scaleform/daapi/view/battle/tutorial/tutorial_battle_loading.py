# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/tutorial/tutorial_battle_loading.py
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading
from gui.Scaleform.daapi.view.meta.TutorialLoadingMeta import TutorialLoadingMeta

class TutorialBattleLoading(BattleLoading, TutorialLoadingMeta):

    def invalidateArenaInfo(self):
        super(TutorialBattleLoading, self).invalidateArenaInfo()
        arenaInfoData = {'mapName': self._battleCtx.getArenaTypeName(),
         'battleTypeLocaleStr': self._battleCtx.getArenaDescriptionString(isInBattle=False),
         'battleTypeFrameLabel': self._battleCtx.getArenaFrameLabel()}
        self.as_setTutorialArenaInfoS(arenaInfoData)
