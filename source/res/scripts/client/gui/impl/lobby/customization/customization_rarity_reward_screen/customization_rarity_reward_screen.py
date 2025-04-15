# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_rarity_reward_screen/customization_rarity_reward_screen.py
import BigWorld
import SoundGroups
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, WindowFlags
from gui.impl.gen.view_models.views.lobby.customization.customization_rarity_reward_screen_model import CustomizationRarityRewardScreenModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen import R
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.customization_3d_objects.logger import CustomizationRarityRewardViewLogger
from uilogging.customization_3d_objects.logging_constants import CustomizationButtons, CustomizationViewKeys

class CustomizationRarityRewardScreen(ViewImpl):
    __customizationService = dependency.descriptor(ICustomizationService)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __slots__ = ('__element', '__isFirstEntry', '__uiLogger', '__sound')
    _REWARD_SOUND_ID = 'elements_cust_reward'
    _LAYOUT_ID = R.views.lobby.customization.CustomizationRarityRewardScreen()

    def __init__(self, element, isFirstEntry):
        settings = ViewSettings(self._LAYOUT_ID)
        settings.layoutID = self._LAYOUT_ID
        settings.flags = ViewFlags.VIEW
        settings.model = CustomizationRarityRewardScreenModel()
        super(CustomizationRarityRewardScreen, self).__init__(settings)
        self.__element = element
        self.__isFirstEntry = isFirstEntry
        self.__uiLogger = CustomizationRarityRewardViewLogger()
        self.__sound = None
        return

    @property
    def viewModel(self):
        return super(CustomizationRarityRewardScreen, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.goToExterior, self.__onGoToExterior), (self.viewModel.goToGarage, self.__onGoToGarage), (self.__hangarSpace.onVehicleChanged, self.__onVehicleChanged))

    def _onLoading(self, *args, **kwargs):
        super(CustomizationRarityRewardScreen, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setName(self.__element.name)
            model.setTitle(self.__element.userName)
            model.setRarity(self.__element.rarity)
            model.setIsFirstAttachment(self.__isFirstEntry)
            model.setIsExteriorEnabled(self.__isC11nEnabled())
        switchHangarOverlaySoundFilter(on=True)
        self.__sound = SoundGroups.g_instance.getSound2D(self._REWARD_SOUND_ID)
        self.__sound.play()

    def _finalize(self):
        super(CustomizationRarityRewardScreen, self)._finalize()
        g_eventBus.handleEvent(events.CustomizationEvent(events.CustomizationEvent.ON_RARITY_REWARD_SCREEN_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        switchHangarOverlaySoundFilter(on=False)
        self.__sound = None
        self.__uiLogger.onViewClose(CustomizationViewKeys.CUSTOMIZATION_RARITY_REWARD_VIEW)
        self.__uiLogger = None
        return

    def __onVehicleChanged(self):
        self.viewModel.setIsExteriorEnabled(self.__isC11nEnabled())

    def __onGoToExterior(self):
        self.__uiLogger.onClick(CustomizationButtons.TO_EXTERIOR, parentScreen=CustomizationViewKeys.CUSTOMIZATION_RARITY_REWARD_VIEW)
        self.destroyWindow()
        BigWorld.callback(0.0, lambda : self.__customizationService.showCustomization() if self.__isC11nEnabled() else showHangar())

    def __onGoToGarage(self):
        self.__uiLogger.onClick(CustomizationButtons.TO_GARAGE, parentScreen=CustomizationViewKeys.CUSTOMIZATION_RARITY_REWARD_VIEW)
        self.destroyWindow()
        showHangar()

    def __isC11nEnabled(self):
        return self.__lobbyCtx.getServerSettings().isCustomizationEnabled() and g_currentVehicle.item and g_currentVehicle.item.isCustomizationEnabled()


class CustomizationRarityRewardWindow(LobbyWindow):
    __slots__ = ('_blur',)

    def __init__(self, element, isFirstEntry):
        self._blur = None
        super(CustomizationRarityRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=CustomizationRarityRewardScreen(element, isFirstEntry), layer=WindowLayer.OVERLAY)
        return

    def _initialize(self):
        super(CustomizationRarityRewardWindow, self)._initialize()
        self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)

    def _finalize(self):
        self._blur.fini()
        self._blur = None
        super(CustomizationRarityRewardWindow, self)._finalize()
        return
