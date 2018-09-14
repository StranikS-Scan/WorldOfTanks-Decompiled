# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationLadderViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StaticFormationLadderViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def showFormationProfile(self, fromationId):
        self._printOverrideError('showFormationProfile')

    def updateClubIcons(self, ids):
        self._printOverrideError('updateClubIcons')

    def as_updateHeaderDataS(self, data):
        """
        :param data: Represented by StaticFormationLadderViewHeaderVO (AS)
        """
        return self.flashObject.as_updateHeaderData(data) if self._isDAAPIInited() else None

    def as_updateLadderDataS(self, data):
        """
        :param data: Represented by StaticFormationLadderViewLadderVO (AS)
        """
        return self.flashObject.as_updateLadderData(data) if self._isDAAPIInited() else None

    def as_setLadderStateS(self, data):
        """
        :param data: Represented by LadderStateDataVO (AS)
        """
        return self.flashObject.as_setLadderState(data) if self._isDAAPIInited() else None

    def as_onUpdateClubIconsS(self, data):
        """
        :param data: Represented by StaticFormationLadderViewIconsVO (AS)
        """
        return self.flashObject.as_onUpdateClubIcons(data) if self._isDAAPIInited() else None

    def as_onUpdateClubIconS(self, clubId, iconPath):
        return self.flashObject.as_onUpdateClubIcon(clubId, iconPath) if self._isDAAPIInited() else None
