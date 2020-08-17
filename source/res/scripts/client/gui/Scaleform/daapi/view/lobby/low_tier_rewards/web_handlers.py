# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/low_tier_rewards/web_handlers.py
from gui.shared.event_dispatcher import showHangar, showLowTierRewardsOverlay
from web.web_client_api import webApiCollection
from web.web_client_api.low_tier_rewards import LowTierRewardsWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import HangarSoundWebApi, SoundStateWebApi, SoundWebApi
from web.web_client_api.ui import CloseWindowWebApi, UtilWebApi, OpenWindowWebApi, NotificationWebApi, OpenTabWebApi
from web.web_client_api.vehicles import VehiclesWebApi
from gui.Scaleform.daapi.view.lobby.low_tier_rewards.low_tier_rewards_sound_controller import LowTierRewardsSounds

class _OpenTabWebApi(OpenTabWebApi):

    def _getVehicleStylePreviewCallback(self, cmd):
        return self.__getReturnCallback(cmd.back_url)

    def __getReturnCallback(self, backUrl):

        def callback():
            showHangar()
            showLowTierRewardsOverlay(path=backUrl)

        return callback if backUrl is not None else None


class _SoundWebApi(SoundWebApi):
    _ENTER_EXIT_SOUND_MAPPING = {'eb_ambient_progress_page_enter': 'eb_ambient_progress_page_exit',
     LowTierRewardsSounds.EV_10Y_GIVEAWAY_ENTER: LowTierRewardsSounds.EV_10Y_GIVEAWAY_EXIT}


class _SoundStateWebApi(SoundStateWebApi):
    _ON_EXIT_STATES = {}


def createLowTierRewardsWebHandlers():
    return webApiCollection(CloseWindowWebApi, OpenWindowWebApi, NotificationWebApi, _OpenTabWebApi, RequestWebApi, ShopWebApi, _SoundWebApi, _SoundStateWebApi, HangarSoundWebApi, UtilWebApi, QuestsWebApi, VehiclesWebApi, RewardsWebApi, SocialWebApi, LowTierRewardsWebApi)
