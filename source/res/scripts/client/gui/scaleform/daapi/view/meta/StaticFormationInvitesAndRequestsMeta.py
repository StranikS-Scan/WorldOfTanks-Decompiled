# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationInvitesAndRequestsMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class StaticFormationInvitesAndRequestsMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def setDescription(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('setDescription')

    def setShowOnlyInvites(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('setShowOnlyInvites')

    def resolvePlayerRequest(self, playerId, playerAccepted):
        """
        :param playerId:
        :param playerAccepted:
        :return :
        """
        self._printOverrideError('resolvePlayerRequest')

    def as_getDataProviderS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_setStaticDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setTeamDescriptionS(self, description):
        """
        :param description:
        :return :
        """
        return self.flashObject.as_setTeamDescription(description) if self._isDAAPIInited() else None
