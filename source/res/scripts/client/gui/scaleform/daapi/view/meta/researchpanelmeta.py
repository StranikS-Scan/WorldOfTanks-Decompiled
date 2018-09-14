# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ResearchPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ResearchPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def goToResearch(self):
        """
        :return :
        """
        self._printOverrideError('goToResearch')

    def as_updateCurrentVehicleS(self, name, type, vDescription, earnedXP, isElite, isPremIGR):
        """
        :param name:
        :param type:
        :param vDescription:
        :param earnedXP:
        :param isElite:
        :param isPremIGR:
        :return :
        """
        return self.flashObject.as_updateCurrentVehicle(name, type, vDescription, earnedXP, isElite, isPremIGR) if self._isDAAPIInited() else None

    def as_setEarnedXPS(self, earnedXP):
        """
        :param earnedXP:
        :return :
        """
        return self.flashObject.as_setEarnedXP(earnedXP) if self._isDAAPIInited() else None

    def as_setEliteS(self, isElite):
        """
        :param isElite:
        :return :
        """
        return self.flashObject.as_setElite(isElite) if self._isDAAPIInited() else None
