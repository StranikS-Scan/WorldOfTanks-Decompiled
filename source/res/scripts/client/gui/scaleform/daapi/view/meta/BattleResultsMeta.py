# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleResultsMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BattleResultsMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def saveSorting(self, iconType, sortDirection, bonusType):
        """
        :param iconType:
        :param sortDirection:
        :param bonusType:
        :return :
        """
        self._printOverrideError('saveSorting')

    def showEventsWindow(self, questID, eventType):
        """
        :param questID:
        :param eventType:
        :return :
        """
        self._printOverrideError('showEventsWindow')

    def getClanEmblem(self, uid, clanID):
        """
        :param uid:
        :param clanID:
        :return :
        """
        self._printOverrideError('getClanEmblem')

    def getTeamEmblem(self, uid, teamID, isUseHtmlWrap):
        """
        :param uid:
        :param teamID:
        :param isUseHtmlWrap:
        :return :
        """
        self._printOverrideError('getTeamEmblem')

    def startCSAnimationSound(self):
        """
        :return :
        """
        self._printOverrideError('startCSAnimationSound')

    def onResultsSharingBtnPress(self):
        """
        :return :
        """
        self._printOverrideError('onResultsSharingBtnPress')

    def onTeamCardClick(self, teamDBID):
        """
        :param teamDBID:
        :return :
        """
        self._printOverrideError('onTeamCardClick')

    def showUnlockWindow(self, itemId, unlockType):
        """
        :param itemId:
        :param unlockType:
        :return :
        """
        self._printOverrideError('showUnlockWindow')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, uid, iconTag):
        """
        :param uid:
        :param iconTag:
        :return :
        """
        return self.flashObject.as_setClanEmblem(uid, iconTag) if self._isDAAPIInited() else None

    def as_setTeamInfoS(self, uid, iconTag, teamName):
        """
        :param uid:
        :param iconTag:
        :param teamName:
        :return :
        """
        return self.flashObject.as_setTeamInfo(uid, iconTag, teamName) if self._isDAAPIInited() else None

    def as_setAnimationS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setAnimation(data) if self._isDAAPIInited() else None
