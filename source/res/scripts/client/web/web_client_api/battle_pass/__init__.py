# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/battle_pass/__init__.py
import logging
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_helpers import isSeasonEndingSoon
from gui.impl.gen import R
from gui.server_events.events_dispatcher import showMissionsBattlePass
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from web.common import formatBattlePassInfo
from web.web_client_api import Field, W2CSchema, WebCommandException, w2c, w2capi
_logger = logging.getLogger(__name__)
_R_VIEWS = R.views.lobby.battle_pass
_VIEWS_IDS = {'intro': _R_VIEWS.BattlePassIntroView(),
 'chapter_choice': _R_VIEWS.ChapterChoiceView(),
 'progression': _R_VIEWS.BattlePassProgressionsView()}

def _isValidViewID(_, data):
    viewID = data.get('id')
    if viewID in _VIEWS_IDS:
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
        showMissionsBattlePass(_VIEWS_IDS.get(cmd.id), cmd.chapter_id)

    @w2c(W2CSchema, name='get_info')
    def handleGetInfo(self, _):
        return formatBattlePassInfo()

    @w2c(W2CSchema, name='show_progressions_view')
    def handleShowProgressionsView(self, _):
        _logger.error('W2C "show_progressions_view" is deprecated, use "show_view" instead!')
        showMissionsBattlePass()

    @w2c(W2CSchema, name='get_shop_banners_params')
    def handleGetShopBannerParams(self, _):
        _logger.error('W2C "get_shop_banners_params" is deprecated, use "get_info" instead!')
        isActive = not self.__battlePass.isPaused() and self.__battlePass.isVisible()
        chaptersBuyInfo = {chapterID:self.__battlePass.isBought(chapterID=chapterID) for chapterID in self.__battlePass.getChapterIDs()}
        canBuyBP = not all(chaptersBuyInfo.values())
        hasBP = any(chaptersBuyInfo.values())
        canBuyLevels = any((isBought and self.__battlePass.getChapterState(chapterID) == ChapterState.ACTIVE for chapterID, isBought in chaptersBuyInfo.iteritems()))
        return {'isActive': isActive,
         'canBuyBP': canBuyBP,
         'canBuyLevels': canBuyLevels,
         'hasBP': hasBP,
         'isSeasonLeftSoon': isSeasonEndingSoon()}
