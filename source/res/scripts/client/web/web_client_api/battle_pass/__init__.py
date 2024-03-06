# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/battle_pass/__init__.py
import logging
from itertools import chain
from gui.impl.gen import R
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBattlePassTankmenVoiceover
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from web.common import formatBattlePassInfo
from web.web_client_api import Field, W2CSchema, WebCommandException, w2c, w2capi
_logger = logging.getLogger(__name__)
_R_VIEWS = R.views.lobby.battle_pass
_VIEWS_IDS = {'intro': _R_VIEWS.BattlePassIntroView(),
 'chapter_choice': _R_VIEWS.ChapterChoiceView(),
 'progression': _R_VIEWS.BattlePassProgressionsView()}
_VIEWS_COMMANDS = {'voiceover': showBattlePassTankmenVoiceover}

def _isValidViewID(_, data):
    viewID = data.get('id')
    if viewID in chain(_VIEWS_IDS, _VIEWS_COMMANDS):
        return True
    raise WebCommandException('id: "{}" is not supported'.format(viewID))


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def _isValidChapterID(_, data, battlePass):
    chapterID = data.get('chapter_id')
    if chapterID in battlePass.getChapterIDs():
        return True
    raise WebCommandException('chapter_id: "{}" is not valid'.format(chapterID))


class _ShowViewSchema(W2CSchema):
    id = Field(required=False, type=basestring, validator=_isValidViewID)
    chapter_id = Field(required=False, type=int, validator=_isValidChapterID)


@w2capi(name='battle_pass', key='action')
class BattlePassWebApi(W2CSchema):
    __battlePass = dependency.descriptor(IBattlePassController)

    @w2c(_ShowViewSchema, name='show_view')
    def handleShowView(self, cmd):
        if cmd.id in _VIEWS_COMMANDS:
            showView = _VIEWS_COMMANDS[cmd.id]
            showView()
        else:
            showMissionsBattlePass(_VIEWS_IDS.get(cmd.id), cmd.chapter_id)

    @w2c(W2CSchema, name='get_info')
    def handleGetInfo(self, _):
        return formatBattlePassInfo()

    @w2c(W2CSchema, name='finish_bp_purchase')
    def finishBattlePassPurchase(self, _):
        g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.ON_FINISH_BATTLE_PASS_PURCHASE), scope=EVENT_BUS_SCOPE.LOBBY)
