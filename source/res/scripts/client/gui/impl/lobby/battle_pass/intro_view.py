# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/intro_view.py
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.battle_pass.battle_pass_helpers import getIntroVideoURL
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_intro_view_model import BattlePassIntroViewModel
from gui.impl.gen.view_models.views.lobby.common.intro_slide_model import IntroSlideModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared.event_dispatcher import showBrowserOverlayView, showHangar
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from tutorial.control.game_vars import getVehicleByIntCD
SPECIAL_VEHICLES_COUNT = 3

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
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onSubmit),
         (self.viewModel.onVideo, self.__showIntroVideo),
         (self.__battlePassController.onBattlePassSettingsChange, self.__updateBattlePassState),
         (self.__battlePassController.onSeasonStateChanged, self.__updateBattlePassState))

    def __updateViewModel(self):
        texts = R.strings.battle_pass.intro
        images = R.images.gui.maps.icons.battlePass.intro
        with self.viewModel.transaction() as tx:
            tx.setTitle(texts.title())
            tx.setAbout(texts.aboutButton())
            tx.setButtonLabel(texts.button())
            slides = tx.getSlides()
            slides.addViewModel(self.__createSlideModel(images.chapters(), texts.slide1.title(), backport.text(texts.slide1.text())))
            slides.addViewModel(self.__createSlideModel(images.points(), texts.slide2.title(), backport.text(texts.slide2.text())))
            vehIntCDs = self.__battlePassController.getSpecialVehicles()
            points = self.__battlePassController.getVehicleProgression(vehIntCDs[0])[1]
            tanksTextArgs = []
            for vehIntCD in vehIntCDs:
                vehicle = getVehicleByIntCD(vehIntCD)
                tanksTextArgs.append(vehicle.userName if vehicle is not None else '')

            if len(tanksTextArgs) == SPECIAL_VEHICLES_COUNT:
                tanksText = backport.text(texts.slide3.text(), tankName1=tanksTextArgs[0], tankName2=tanksTextArgs[1], tankName3=tanksTextArgs[2], points=points)
                slides.addViewModel(self.__createSlideModel(images.tanks(), texts.slide3.title(), tanksText))
            slides.addViewModel(self.__createSlideModel(images.token_shop(), texts.slide4.title(), backport.text(texts.slide4.text())))
        return

    @staticmethod
    def __createSlideModel(icon, title, description):
        slide = IntroSlideModel()
        slide.setIcon(icon)
        slide.setTitle(title)
        slide.setDescription(description)
        return slide

    @staticmethod
    def __onSubmit():
        showMissionsBattlePass()

    @staticmethod
    def __showIntroVideo():
        showBrowserOverlayView(getIntroVideoURL(), VIEW_ALIAS.BROWSER_OVERLAY)

    def __updateBattlePassState(self, *_):
        if self.__battlePassController.isPaused():
            showMissionsBattlePass()
        elif not self.__battlePassController.isActive():
            showHangar()
