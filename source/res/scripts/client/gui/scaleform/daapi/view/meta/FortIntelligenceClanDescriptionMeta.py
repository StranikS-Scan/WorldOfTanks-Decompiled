# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceClanDescriptionMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortIntelligenceClanDescriptionMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def onOpenCalendar(self):
        self._printOverrideError('onOpenCalendar')

    def onOpenClanList(self):
        self._printOverrideError('onOpenClanList')

    def onOpenClanStatistics(self):
        self._printOverrideError('onOpenClanStatistics')

    def onOpenClanCard(self):
        self._printOverrideError('onOpenClanCard')

    def onAddRemoveFavorite(self, isAdd):
        self._printOverrideError('onAddRemoveFavorite')

    def onAttackDirection(self, uid):
        self._printOverrideError('onAttackDirection')

    def onHoverDirection(self):
        self._printOverrideError('onHoverDirection')

    def as_setDataS(self, data):
        """
        :param data: Represented by ClanDescriptionVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_updateBookMarkS(self, isAdd):
        return self.flashObject.as_updateBookMark(isAdd) if self._isDAAPIInited() else None
