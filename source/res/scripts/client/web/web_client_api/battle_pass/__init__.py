# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/battle_pass/__init__.py
from gui.battle_pass.battle_pass_helpers import isSeasonEndingSoon, isCurrentBattlePassStateBase
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from web.web_client_api import w2c, w2capi, W2CSchema, Field

class _ShowBuyViewSchema(W2CSchema):
    back_btn_descr = Field(required=True, type=basestring)
    back_url = Field(required=True, type=basestring)


class _SetShownVideoSchema(W2CSchema):
    video_id = Field(required=True, type=int)


@w2capi(name='battle_pass', key='action')
class BattlePassWebApi(W2CSchema):
    __battlePassCtrl = dependency.descriptor(IBattlePassController)

    @w2c(W2CSchema, name='get_viewed_videos')
    def handleGetViewedVideos(self, _):
        pass

    @w2c(_SetShownVideoSchema, name='set_shown_video')
    def handleSetShownVideo(self, cmd):
        pass

    @w2c(W2CSchema, name='show_progressions_view')
    def handleShowProgressionsView(self, _):
        showMissionsBattlePassCommonProgression()

    @w2c(W2CSchema, name='get_shop_banners_params')
    def handleGetShopBannerParams(self, _):
        isVisible = (isCurrentBattlePassStateBase() or not self.__battlePassCtrl.isBought()) and not self.__battlePassCtrl.isPaused() and self.__battlePassCtrl.isVisible()
        data = {'isVisible': isVisible,
         'isSeasonLeftSoon': isSeasonEndingSoon()}
        return data
