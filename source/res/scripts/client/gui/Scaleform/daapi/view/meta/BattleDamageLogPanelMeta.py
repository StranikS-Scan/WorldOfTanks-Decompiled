# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleDamageLogPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleDamageLogPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def as_showDamageLogComponentS(self, value):
        return self.flashObject.as_showDamageLogComponent(value) if self._isDAAPIInited() else None

    def as_summaryStatsS(self, damage, blocked, assist):
        return self.flashObject.as_summaryStats(damage, blocked, assist) if self._isDAAPIInited() else None

    def as_updateSummaryDamageValueS(self, value):
        return self.flashObject.as_updateSummaryDamageValue(value) if self._isDAAPIInited() else None

    def as_updateSummaryBlockedValueS(self, value):
        return self.flashObject.as_updateSummaryBlockedValue(value) if self._isDAAPIInited() else None

    def as_updateSummaryAssistValueS(self, value):
        return self.flashObject.as_updateSummaryAssistValue(value) if self._isDAAPIInited() else None

    def as_detailStatsS(self, isVisible, messages):
        """
        :param messages: Represented by Vector.<MessageRenderModel> (AS)
        """
        return self.flashObject.as_detailStats(isVisible, messages) if self._isDAAPIInited() else None

    def as_addDetailMessageS(self, valueColor, value, actionTypeImg, vehicleTypeImg, vehicleName):
        return self.flashObject.as_addDetailMessage(valueColor, value, actionTypeImg, vehicleTypeImg, vehicleName) if self._isDAAPIInited() else None

    def as_isDownCtrlButtonS(self, value):
        return self.flashObject.as_isDownCtrlButton(value) if self._isDAAPIInited() else None

    def as_isDownAltButtonS(self, value):
        return self.flashObject.as_isDownAltButton(value) if self._isDAAPIInited() else None
