# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/meta/FalloutScorePanelMeta.py
from gui.Scaleform.daapi.view.battle.meta.BattleComponentMeta import BattleComponentMeta

class FalloutScorePanelMeta(BattleComponentMeta):

    def as_initWarningValue(self, warningValue):
        self._flashObject.as_initWarningValue(warningValue)

    def as_setDataS(self, contextType, maxValue, playerScore, allyValue, enemyValue, playerName, enemyName, props):
        self._flashObject.as_setData(contextType, maxValue, playerScore, allyValue, enemyValue, playerName, enemyName, props)

    def as_onSettingsChanged(self):
        self._flashObject.as_onSettingsChanged()

    def as_playScoreHighlightAnim(self, isWinner):
        self._flashObject.as_playScoreHighlightAnim(isWinner)

    def as_stopScoreHighlightAnim(self):
        self._flashObject.as_stopScoreHighlightAnim()
