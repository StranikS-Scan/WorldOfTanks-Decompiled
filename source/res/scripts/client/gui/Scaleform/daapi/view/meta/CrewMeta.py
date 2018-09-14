# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CrewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        """
        :param rendererData:
        :param menuEnabled:
        :return :
        """
        self._printOverrideError('onShowRecruitWindowClick')

    def unloadAllTankman(self):
        """
        :return :
        """
        self._printOverrideError('unloadAllTankman')

    def equipTankman(self, tankmanID, slot):
        """
        :param tankmanID:
        :param slot:
        :return :
        """
        self._printOverrideError('equipTankman')

    def updateTankmen(self):
        """
        :return :
        """
        self._printOverrideError('updateTankmen')

    def openPersonalCase(self, value, tabNumber):
        """
        :param value:
        :param tabNumber:
        :return :
        """
        self._printOverrideError('openPersonalCase')

    def onCrewDogMoreInfoClick(self):
        """
        :return :
        """
        self._printOverrideError('onCrewDogMoreInfoClick')

    def onCrewDogItemClick(self):
        """
        :return :
        """
        self._printOverrideError('onCrewDogItemClick')

    def as_tankmenResponseS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_tankmenResponse(data) if self._isDAAPIInited() else None

    def as_dogResponseS(self, dogName):
        """
        :param dogName:
        :return :
        """
        return self.flashObject.as_dogResponse(dogName) if self._isDAAPIInited() else None
