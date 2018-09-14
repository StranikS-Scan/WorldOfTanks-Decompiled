# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventProgressPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventProgressPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_initS(self, isAllyMark1, progress, currentHealth, maxHealth, state, vehName, isColorBlind):
        """
        :param isAllyMark1:
        :param progress:
        :param currentHealth:
        :param maxHealth:
        :param state:
        :param vehName:
        :param isColorBlind:
        :return :
        """
        return self.flashObject.as_init(isAllyMark1, progress, currentHealth, maxHealth, state, vehName, isColorBlind) if self._isDAAPIInited() else None

    def as_updateHealthS(self, health):
        """
        :param health:
        :return :
        """
        return self.flashObject.as_updateHealth(health) if self._isDAAPIInited() else None

    def as_updateProgressS(self, progress):
        """
        :param progress:
        :return :
        """
        return self.flashObject.as_updateProgress(progress) if self._isDAAPIInited() else None

    def as_updateStateS(self, state):
        """
        :param state:
        :return :
        """
        return self.flashObject.as_updateState(state) if self._isDAAPIInited() else None

    def as_updateSettingsS(self, isColorBlind):
        """
        :param isColorBlind:
        :return :
        """
        return self.flashObject.as_updateSettings(isColorBlind) if self._isDAAPIInited() else None
