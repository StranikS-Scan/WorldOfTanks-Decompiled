# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/web_handlers.py
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import createWebHandlers
from gui.impl import backport
from gui.impl.gen import R
from gui.wot_anniversary.wot_anniversary_helpers import WOT_ANNIVERSARY_REWARDS
from helpers import dependency
from skeletons.gui.game_control import IWotAnniversaryController
from web.web_client_api import w2capi
from web.web_client_api.ui import ProfileTabWebApiMixin, ShopWebApiMixin, VehiclePreviewWebApiMixin, MissionsWebApiMixin
from web.web_client_api.ui.hangar import HangarTabWebApiMixin
from web.web_client_api.wot_anniversary import WotAnniversaryWebApi

def createWotAnniversaryWebHandlers():
    return createWebHandlers({'open_tab': _OpenTabWebApi,
     'wot_anniversary': WotAnniversaryWebApi})


@w2capi(name='open_tab', key='tab_id')
class _OpenTabWebApi(HangarTabWebApiMixin, ProfileTabWebApiMixin, ShopWebApiMixin, VehiclePreviewWebApiMixin, MissionsWebApiMixin):
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)

    def _getVehiclePreviewReturnAlias(self, cmd):
        return WOT_ANNIVERSARY_REWARDS

    def _getVehicleStylePreviewReturnAlias(self, cmd):
        return backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.wotAnniversaryRewards())

    def _getVehiclePreviewReturnCallback(self, cmd):
        return self.__getReturnCallback()

    def _getVehicleStylePreviewCallback(self, cmd):
        return self.__getReturnCallback()

    def __getReturnCallback(self):

        def _returnToRewardProgress():
            from gui.shared.event_dispatcher import showHangar
            from gui.wot_anniversary.wot_anniversary_helpers import showRewardProgressView
            showHangar()
            if self.__wotAnniversaryCtrl.isAvailable():
                showRewardProgressView()

        return _returnToRewardProgress
