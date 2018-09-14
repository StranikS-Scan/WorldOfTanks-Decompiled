# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleQueueMeta.py
from gui.Scaleform.framework.entities.View import View

class BattleQueueMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def startClick(self):
        """
        :return :
        """
        self._printOverrideError('startClick')

    def exitClick(self):
        """
        :return :
        """
        self._printOverrideError('exitClick')

    def onEscape(self):
        """
        :return :
        """
        self._printOverrideError('onEscape')

    def as_setTimerS(self, textLabel, timeLabel):
        """
        :param textLabel:
        :param timeLabel:
        :return :
        """
        return self.flashObject.as_setTimer(textLabel, timeLabel) if self._isDAAPIInited() else None

    def as_setTypeInfoS(self, iconLabel, title, description):
        """
        :param iconLabel:
        :param title:
        :param description:
        :return :
        """
        return self.flashObject.as_setTypeInfo(iconLabel, title, description) if self._isDAAPIInited() else None

    def as_setPlayersS(self, text):
        """
        :param text:
        :return :
        """
        return self.flashObject.as_setPlayers(text) if self._isDAAPIInited() else None

    def as_setListByTypeS(self, listData):
        """
        :param listData:
        :return :
        """
        return self.flashObject.as_setListByType(listData) if self._isDAAPIInited() else None

    def as_showStartS(self, vis):
        """
        :param vis:
        :return :
        """
        return self.flashObject.as_showStart(vis) if self._isDAAPIInited() else None

    def as_showExitS(self, vis):
        """
        :param vis:
        :return :
        """
        return self.flashObject.as_showExit(vis) if self._isDAAPIInited() else None
