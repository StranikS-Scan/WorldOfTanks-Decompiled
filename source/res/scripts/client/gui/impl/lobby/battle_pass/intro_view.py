# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/intro_view.py
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.battle_pass.battle_pass_helpers import getIntroVideoURL
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_intro_view_model import BattlePassIntroViewModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared.event_dispatcher import showBrowserOverlayView, showHangar
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from tutorial.control.game_vars import getVehicleByIntCD

class IntroView(ViewImpl):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassIntroView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = BattlePassIntroViewModel()
        super(IntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(IntroView, self).getViewModel()

    def markVisited(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.INTRO_SHOWN: True})

    def _onLoading(self, *args, **kwargs):
        super(IntroView, self)._onLoading(*args, **kwargs)
        self.__updateBattlePassState()
        self.__showIntroVideo(onStart=True)
        with self.viewModel.transaction() as tx:
            vehIntCDs = self.__battlePassController.getSpecialVehicles()
            capacity = self.__battlePassController.getVehicleProgression(vehIntCDs[0])[1]
            tx.setPoints(capacity)
            for vehIntCD in vehIntCDs:
                vehicle = getVehicleByIntCD(vehIntCD)
                tx.getTankNames().addString(vehicle.userName if vehicle is not None else '')

        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onSubmit), (self.viewModel.onVideo, self.__showIntroVideo), (self.__battlePassController.onBattlePassSettingsChange, self.__updateBattlePassState))

    def __onSubmit(self):
        showMissionsBattlePass()

    def __showIntroVideo(self, onStart=False):
        settings = self.__settingsCore.serverSettings
        if onStart:
            if settings.getBPStorage().get(BattlePassStorageKeys.INTRO_VIDEO_SHOWN):
                return False
            settings.saveInBPStorage({BattlePassStorageKeys.INTRO_VIDEO_SHOWN: True})
        showBrowserOverlayView(getIntroVideoURL(), VIEW_ALIAS.BROWSER_OVERLAY)
        return True

    def __updateBattlePassState(self, *_):
        if not self.__battlePassController.isActive():
            showHangar()
