# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/comp7_voip_helper.py
import enum
import typing
import VOIP
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.interfaces import IComp7VOIPController
_HTML_TEMPLATE = 'html_templates:comp7/voiceChat'

@enum.unique
class VoiceChatControlTextStyles(enum.Enum):
    FULL_STATS = 'fullStatsStyle'
    PLAYERS_PANEL = 'playersPanelStyle'


class Comp7VoipHelper(object):
    __slots__ = ('__component', '__textStyle', '__enabled')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, component, textStyle):
        self.__component = component
        self.__textStyle = textStyle
        self.__enabled = False

    @property
    def __voipController(self):
        return self.__sessionProvider.dynamic.comp7VOIPController

    @property
    def __isVisible(self):
        voipCtrl = self.__voipController
        return self.__enabled and voipCtrl is not None and voipCtrl.isTeamVoipEnabled

    @property
    def __isJoined(self):
        voipCtrl = self.__voipController
        return self.__enabled and voipCtrl is not None and voipCtrl.isJoined

    def populate(self):
        component = self.__component
        component.as_setVoiceChatDataS({'activeText': self.__makeHtmlString(backport.text(R.strings.comp7.voiceChat.active())),
         'inactiveText': self.__makeHtmlString(backport.text(R.strings.comp7.voiceChat.inactive()))})
        self.__update()
        self.__subscribe()

    def dispose(self):
        self.__unsubscribe()
        self.__component = None
        return

    def enable(self, enable):
        self.__enabled = enable
        self.__update()

    def onVoiceChatControlClick(self):
        self.__voipController.toggleChannelConnection()

    def __subscribe(self):
        voipMgr = VOIP.getVOIPManager()
        if voipMgr is not None:
            voipMgr.onChannelAvailable += self.__update
            voipMgr.onChannelLost += self.__update
            voipMgr.onJoinedChannel += self.__update
            voipMgr.onLeftChannel += self.__update
        return

    def __unsubscribe(self):
        voipMgr = VOIP.getVOIPManager()
        if voipMgr is not None:
            voipMgr.onChannelAvailable -= self.__update
            voipMgr.onChannelLost -= self.__update
            voipMgr.onJoinedChannel -= self.__update
            voipMgr.onLeftChannel -= self.__update
        return

    def __update(self, *_, **__):
        self.__component.as_setVoiceChatControlVisibleS(self.__isVisible)
        self.__component.as_setVoiceChatControlSelectedS(self.__isJoined)

    def __makeHtmlString(self, text):
        return makeHtmlString(_HTML_TEMPLATE, self.__textStyle.value, {'message': text})
