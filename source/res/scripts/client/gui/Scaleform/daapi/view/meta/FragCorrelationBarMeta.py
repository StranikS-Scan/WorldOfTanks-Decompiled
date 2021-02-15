# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FragCorrelationBarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FragCorrelationBarMeta(BaseDAAPIComponent):

    def as_updateTeamHealthValuesS(self, allyTeamHealth, diffValue, allyTeamHealthPercentage, enemyTeamHealth, enemyTeamHealthPercentage):
        return self.flashObject.as_updateTeamHealthValues(allyTeamHealth, diffValue, allyTeamHealthPercentage, enemyTeamHealth, enemyTeamHealthPercentage) if self._isDAAPIInited() else None

    def as_updateViewSettingS(self, setting):
        return self.flashObject.as_updateViewSetting(setting) if self._isDAAPIInited() else None
