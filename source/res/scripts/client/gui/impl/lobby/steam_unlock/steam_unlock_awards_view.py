# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/steam_unlock/steam_unlock_awards_view.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.awards_view_model import AwardsViewModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.steam_unlock.steam_unlock_bonus_packer import getSteamUnlockBonuses, getSteamUnlockBonusPacker
from gui.impl.lobby.steam_unlock.steam_unlock_sounds import STEAM_UNLOCK_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import VehiclesBonus
from gui.shared.event_dispatcher import selectVehicleInHangar
from shared_utils import first

class SteamUnlockAwardsView(ViewImpl):
    _COMMON_SOUND_SPACE = STEAM_UNLOCK_SOUND_SPACE

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.common.AwardsView(), model=AwardsViewModel(), args=args, kwargs=kwargs)
        self.__rewards = kwargs.get('rewards', {})
        self.__vehicleIntCD = None
        self.__tooltips = {}
        super(SteamUnlockAwardsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(SteamUnlockAwardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SteamUnlockAwardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        return self.__tooltips.get(event.getArgument('tooltipId'))

    def _getEvents(self):
        return super(SteamUnlockAwardsView, self)._getEvents() + ((self.viewModel.onClose, self.__onClose), (self.viewModel.onRedirect, self.__onRedirect), (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _onLoading(self, *args, **kwargs):
        super(SteamUnlockAwardsView, self)._onLoading(*args, **kwargs)
        self.__processVehicles()
        locales = R.strings.ingame_gui.steamUnlockAwards
        bonuses = getSteamUnlockBonuses(self.__rewards)
        with self.viewModel.transaction() as tx:
            tx.setTitle(locales.title())
            tx.setUnderTitle(locales.underTitle())
            tx.setDefaultButtonTitle(locales.button.submit())
            tx.setRedirectButtonTitle(locales.button.redirect())
            tx.setBackground(R.images.gui.maps.icons.windows.steam_unlock_background())
            packBonusModelAndTooltipData(bonuses, tx.mainRewards, tooltipData=self.__tooltips, packer=getSteamUnlockBonusPacker())

    def _finalize(self):
        self.__clear()
        super(SteamUnlockAwardsView, self)._finalize()

    def __clear(self):
        self.__rewards = {}
        self.__vehicleIntCD = None
        self.__tooltips = {}
        return

    def __onClose(self, *_):
        self.destroyWindow()

    def __onRedirect(self, *_):
        if self.__vehicleIntCD is not None:
            selectVehicleInHangar(self.__vehicleIntCD)
        self.__onClose()
        return

    def __onDisconnected(self):
        self.__onClose()

    def __processVehicles(self):
        vehiclesCDs = []
        for vehicles in self.__rewards.get(VehiclesBonus.VEHICLES_BONUS, []):
            vehiclesCDs.extend(vehicles.keys())

        self.__vehicleIntCD = first(vehiclesCDs)


class SteamUnlockAwardsWindow(LobbyNotificationWindow):

    def __init__(self, **kwargs):
        super(SteamUnlockAwardsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SteamUnlockAwardsView(**kwargs))
