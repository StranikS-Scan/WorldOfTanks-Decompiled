# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleSessionListMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BattleSessionListMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def requestToJoinTeam(self, prbID, prbType):
        """
        :param prbID:
        :param prbType:
        :return :
        """
        self._printOverrideError('requestToJoinTeam')

    def getClientID(self):
        """
        :return Number:
        """
        self._printOverrideError('getClientID')

    def as_refreshListS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_refreshList(data) if self._isDAAPIInited() else None
