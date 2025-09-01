# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/intro_view.py
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.battle_pass.battle_pass_helpers import getIntroSlidesNames, getIntroVideoURL
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_intro_view_model import BattlePassIntroViewModel
from gui.impl.gen.view_models.views.lobby.common.intro_slide_model import IntroSlideModel
from gui.impl.lobby.battle_pass.common import isExtraChapterSeen, setExtraChapterSeen
from gui.impl.pub.view_component import ViewComponent
from gui.shared.event_dispatcher import showBattlePass, showBrowserOverlayView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from tutorial.control.game_vars import getVehicleByIntCD
_IMAGES = R.images.gui.maps.icons.battlePass.intro
_TEXTS = R.strings.battle_pass.intro
_BG = R.images.gui.maps.icons.battlePass.backgrounds

class IntroPresenter(ViewComponent[BattlePassIntroViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args, **kwargs):
        super(IntroPresenter, self).__init__(R.aliases.battle_pass.Intro(), BattlePassIntroViewModel)

    @property
    def viewModel(self):
        return super(IntroPresenter, self).getViewModel()

    def activate(self):
        self._subscribe()

    def deactivate(self):
        self._unsubscribe()

    def _onLoading(self, *args, **kwargs):
        super(IntroPresenter, self)._onLoading(*args, **kwargs)
        self.__updateBattlePassState()
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__setIntroShown),
         (self.viewModel.onVideo, self.__showVideo),
         (self.__battlePass.onBattlePassSettingsChange, self.__updateBattlePassState),
         (self.__battlePass.onSeasonStateChanged, self.__updateBattlePassState))

    def __updateViewModel(self):
        with self.viewModel.transaction() as tx:
            placeholders = self.__genResCommPlaceholders()
            slides = tx.getSlides()
            for slideName in getIntroSlidesNames():
                slides.addViewModel(self.__createSlideModel(slideName, **placeholders))

            tx.setTitle(_TEXTS.title())
            tx.setAbout(_TEXTS.aboutButton())
            tx.setButtonLabel(_TEXTS.button())
            tx.setBackground(_BG.common())

    @staticmethod
    def __createSlideModel(slideName, **kwargs):
        slide = IntroSlideModel()
        slide.setIcon(_IMAGES.dyn(slideName)())
        slide.setTitle(_TEXTS.dyn(slideName).title())
        slide.setDescription(backport.text(_TEXTS.dyn(slideName).text(), **kwargs))
        return slide

    def __setIntroShown(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.INTRO_SHOWN: True})
        if self.__battlePass.hasExtra() and not isExtraChapterSeen():
            setExtraChapterSeen()

    @staticmethod
    def __showVideo():
        showBrowserOverlayView(getIntroVideoURL(), VIEW_ALIAS.BROWSER_OVERLAY)

    def __genResCommPlaceholders(self):
        commonResArgs = {}
        vehIntCDs = self.__battlePass.getSpecialVehicles()
        commonResArgs['points'] = self.__battlePass.getSpecialVehicleCapBonus()
        for idx, vehIntCD in enumerate(vehIntCDs, 1):
            vehicle = getVehicleByIntCD(vehIntCD)
            commonResArgs['tankName{}'.format(idx)] = vehicle.userName if vehicle else ''

        return commonResArgs

    def __updateBattlePassState(self, *_):
        if self.__battlePass.isPaused():
            showBattlePass()
