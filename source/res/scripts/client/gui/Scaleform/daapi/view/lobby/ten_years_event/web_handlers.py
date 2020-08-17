# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ten_years_event/web_handlers.py
import WWISE
from gui.shared.event_dispatcher import showTenYearsCountdownOverlay, showHangar
from web.web_client_api import webApiCollection
from web.web_client_api.low_tier_rewards import LowTierRewardsWebApi
from web.web_client_api.ten_years_event import TenYCEventWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import SoundWebApi, HangarSoundWebApi, SoundStateWebApi
from web.web_client_api.ui import CloseWindowWebApi, UtilWebApi, OpenWindowWebApi, OpenTabWebApi, NotificationWebApi
from web.web_client_api.vehicles import VehiclesWebApi
from gui.Scaleform.daapi.view.lobby.ten_years_event.ten_years_event_sound_controller import TenYearsEventSounds

class _OpenTabWebApi(OpenTabWebApi):

    def _getVehicleStylePreviewCallback(self, cmd):
        return self.__getReturnCallback(cmd.back_url)

    def __getReturnCallback(self, backUrl):

        def callback():
            showHangar()
            showTenYearsCountdownOverlay(path=backUrl)

        return callback if backUrl is not None else None

    def _getVehiclePreviewReturnCallback(self, cmd):
        return self.__getReturnCallback(cmd.back_url)


class _SoundWebApi(SoundWebApi):
    _ENTER_EXIT_SOUND_MAPPING = {'eb_ambient_progress_page_enter': 'eb_ambient_progress_page_exit',
     TenYearsEventSounds.EV_10Y_COUNTDOWN_ENTER: TenYearsEventSounds.EV_10Y_COUNTDOWN_EXIT}


class _SoundStateWebApi(SoundStateWebApi):
    __ON_EXIT_STATES_EXT = {TenYearsEventSounds.STATE_EV_10Y_COUNTDOWN_EPISODE: TenYearsEventSounds.STATE_EV_10Y_COUNTDOWN_EPISODE_OUT}

    def _statesFini(self):
        super(_SoundStateWebApi, self)._statesFini()
        for stateName, stateValue in self.__ON_EXIT_STATES_EXT.iteritems():
            WWISE.WW_setState(stateName, stateValue)


def createTenYearsEventWebHandlers():
    return webApiCollection(CloseWindowWebApi, OpenWindowWebApi, NotificationWebApi, _OpenTabWebApi, RequestWebApi, ShopWebApi, _SoundWebApi, _SoundStateWebApi, HangarSoundWebApi, UtilWebApi, QuestsWebApi, VehiclesWebApi, RewardsWebApi, SocialWebApi, TenYCEventWebApi, LowTierRewardsWebApi)
