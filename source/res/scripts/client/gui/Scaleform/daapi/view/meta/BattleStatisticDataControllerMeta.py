# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleStatisticDataControllerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class BattleStatisticDataControllerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def onRefreshComplete(self):
        """
        :return :
        """
        self._printOverrideError('onRefreshComplete')

    def as_refreshS(self):
        """
        :return :
        """
        return self.flashObject.as_refresh() if self._isDAAPIInited() else None

    def as_setVehiclesDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setVehiclesData(data) if self._isDAAPIInited() else None

    def as_addVehiclesInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_addVehiclesInfo(data) if self._isDAAPIInited() else None

    def as_updateVehiclesInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateVehiclesInfo(data) if self._isDAAPIInited() else None

    def as_updateVehicleStatusS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateVehicleStatus(data) if self._isDAAPIInited() else None

    def as_setVehiclesStatsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setVehiclesStats(data) if self._isDAAPIInited() else None

    def as_updateVehiclesStatsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateVehiclesStats(data) if self._isDAAPIInited() else None

    def as_updatePlayerStatusS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updatePlayerStatus(data) if self._isDAAPIInited() else None

    def as_setArenaInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setArenaInfo(data) if self._isDAAPIInited() else None

    def as_setUserTagsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setUserTags(data) if self._isDAAPIInited() else None

    def as_updateUserTagsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateUserTags(data) if self._isDAAPIInited() else None

    def as_updateInvitationsStatusesS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateInvitationsStatuses(data) if self._isDAAPIInited() else None

    def as_setPersonalStatusS(self, bitmask):
        """
        :param bitmask:
        :return :
        """
        return self.flashObject.as_setPersonalStatus(bitmask) if self._isDAAPIInited() else None

    def as_updatePersonalStatusS(self, added, removed):
        """
        :param added:
        :param removed:
        :return :
        """
        return self.flashObject.as_updatePersonalStatus(added, removed) if self._isDAAPIInited() else None
