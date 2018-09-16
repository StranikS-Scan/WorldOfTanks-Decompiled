# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleDamageLogPanelMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleDamageLogPanelMeta(BaseDAAPIComponent):

    def as_setSettingsDamageLogComponentS(self, isVisible, isColorBlind):
        return self.flashObject.as_setSettingsDamageLogComponent(isVisible, isColorBlind) if self._isDAAPIInited() else None

    def as_summaryStatsS(self, damage, blocked, assist, stun):
        return self.flashObject.as_summaryStats(damage, blocked, assist, stun) if self._isDAAPIInited() else None

    def as_updateSummaryDamageValueS(self, value):
        return self.flashObject.as_updateSummaryDamageValue(value) if self._isDAAPIInited() else None

    def as_updateSummaryBlockedValueS(self, value):
        return self.flashObject.as_updateSummaryBlockedValue(value) if self._isDAAPIInited() else None

    def as_updateSummaryAssistValueS(self, value):
        return self.flashObject.as_updateSummaryAssistValue(value) if self._isDAAPIInited() else None

    def as_updateSummaryStunValueS(self, value):
        return self.flashObject.as_updateSummaryStunValue(value) if self._isDAAPIInited() else None

    def as_detailStatsTopS(self, isVisible, isShortMode, messages):
        """
        :param messages: Represented by Vector.<MessageRenderModel> (AS)
        """
        return self.flashObject.as_detailStatsTop(isVisible, isShortMode, messages) if self._isDAAPIInited() else None

    def as_addDetailMessageTopS(self, value, actionTypeImg, vehicleTypeImg, vehicleName, shellTypeStr, shellTypeBG):
        return self.flashObject.as_addDetailMessageTop(value, actionTypeImg, vehicleTypeImg, vehicleName, shellTypeStr, shellTypeBG) if self._isDAAPIInited() else None

    def as_detailStatsBottomS(self, isVisible, isShortMode, messages):
        """
        :param messages: Represented by Vector.<MessageRenderModel> (AS)
        """
        return self.flashObject.as_detailStatsBottom(isVisible, isShortMode, messages) if self._isDAAPIInited() else None

    def as_addDetailMessageBottomS(self, value, actionTypeImg, vehicleTypeImg, vehicleName, shellTypeStr, shellTypeBG):
        return self.flashObject.as_addDetailMessageBottom(value, actionTypeImg, vehicleTypeImg, vehicleName, shellTypeStr, shellTypeBG) if self._isDAAPIInited() else None

    def as_isDownCtrlButtonS(self, value):
        return self.flashObject.as_isDownCtrlButton(value) if self._isDAAPIInited() else None

    def as_isDownAltButtonS(self, value):
        return self.flashObject.as_isDownAltButton(value) if self._isDAAPIInited() else None
