# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBattlePageMeta.py
from gui.Scaleform.daapi.view.battle.event_mark1.page import EventMark1Page

class EventBattlePageMeta(EventMark1Page):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends EventMark1Page
    null
    """

    def as_setPostmortemGasAtackInfoS(self, infoStr, respawnStr, showDeadIcon):
        """
        :param infoStr:
        :param respawnStr:
        :param showDeadIcon:
        :return :
        """
        return self.flashObject.as_setPostmortemGasAtackInfo(infoStr, respawnStr, showDeadIcon) if self._isDAAPIInited() else None

    def as_hidePostmortemGasAtackInfoS(self):
        """
        :return :
        """
        return self.flashObject.as_hidePostmortemGasAtackInfo() if self._isDAAPIInited() else None
