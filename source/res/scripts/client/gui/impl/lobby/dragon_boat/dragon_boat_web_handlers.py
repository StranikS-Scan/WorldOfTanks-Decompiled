# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dragon_boat/dragon_boat_web_handlers.py
from functools import partial
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import createWebHandlers
from gui.game_control.dragon_boat_controller import DBOAT_REWARDS
from web.web_client_api import w2capi
from web.web_client_api.ui import ProfileTabWebApiMixin, ShopWebApiMixin, VehiclePreviewWebApiMixin, MissionsWebApiMixin
from web.web_client_api.ui.hangar import HangarTabWebApiMixin

def createDragonBoatWebHandlers():
    return createWebHandlers({'open_tab': _OpenTabWebApi})


@w2capi(name='open_tab', key='tab_id')
class _OpenTabWebApi(HangarTabWebApiMixin, ProfileTabWebApiMixin, ShopWebApiMixin, VehiclePreviewWebApiMixin, MissionsWebApiMixin):

    def _getVehiclePreviewReturnCallback(self, cmd):
        from gui.server_events.events_dispatcher import showDragonBoatTab, showMissionsDragonBoat
        return partial(showDragonBoatTab, url=DBOAT_REWARDS) if cmd.back_url == 'rewards/' else showMissionsDragonBoat

    def _getVehiclePreviewReturnAlias(self, cmd):
        return DBOAT_REWARDS if cmd.back_url == 'rewards/' else ''
