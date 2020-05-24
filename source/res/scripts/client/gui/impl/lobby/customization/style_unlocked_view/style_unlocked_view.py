# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/style_unlocked_view/style_unlocked_view.py
import BigWorld
import WWISE
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.customization.style_unlocked_view.style_unlocked_view_model import StyleUnlockedViewModel
from gui.impl.lobby.customization.shared import goToC11nStyledMode
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from frameworks.wulf import WindowFlags
from gui.impl.gen import R
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency, int2roman
from items.components.c11n_constants import UNBOUND_VEH_KEY
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from gui.impl.lobby.progressive_reward.progressive_award_sounds import ProgressiveRewardSoundEvents

class StyleUnlockedView(ViewImpl):
    c11nService = dependency.descriptor(ICustomizationService)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.customization.style_unlocked_view.StyleUnlockedView())
        settings.flags = ViewFlags.OVERLAY_VIEW
        settings.model = StyleUnlockedViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__vehicle = None
        super(StyleUnlockedView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(StyleUnlockedView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(StyleUnlockedView, self)._initialize(*args, **kwargs)
        self._addListeners()

    def _finalize(self):
        self._removeListeners()
        super(StyleUnlockedView, self)._finalize()

    def _onLoading(self, vehicleCD):
        self.__vehicle = self.itemsCache.items.getItemByCD(vehicleCD) if vehicleCD != UNBOUND_VEH_KEY else g_currentVehicle.item
        if self.__vehicle is None:
            raise SoftException('invalid vehicle: &s', vehicleCD)
        with self.viewModel.transaction() as model:
            if vehicleCD != UNBOUND_VEH_KEY:
                self.__setVehicleInfo(model)
            self.__updateC11nButton(model=model)
        return

    def _lockC11nButton(self, *_):
        self.__updateC11nButton(lock=True)

    def _updateC11nButton(self, *_):
        self.__updateC11nButton(lock=False)

    def _addListeners(self):
        self.viewModel.onOkClick += self.__onOkClick
        self.viewModel.onSecondaryClick += self.__onShowC11nClick
        self.viewModel.onAnimationSound += self.__onAnimationSound
        g_eventBus.addListener(VIEW_ALIAS.HERO_VEHICLE_PREVIEW, self._lockC11nButton, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(VIEW_ALIAS.BATTLE_QUEUE, self._lockC11nButton, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(VIEW_ALIAS.LOBBY_HANGAR, self._updateC11nButton, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCallbacks({'inventory': self._updateC11nButton})
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self._updateC11nButton})

    def _removeListeners(self):
        self.viewModel.onOkClick -= self.__onOkClick
        self.viewModel.onSecondaryClick -= self.__onShowC11nClick
        self.viewModel.onAnimationSound -= self.__onAnimationSound
        g_eventBus.removeListener(VIEW_ALIAS.HERO_VEHICLE_PREVIEW, self._lockC11nButton, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(VIEW_ALIAS.BATTLE_QUEUE, self._lockC11nButton, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(VIEW_ALIAS.LOBBY_HANGAR, self._updateC11nButton, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __setVehicleInfo(self, model):
        model.setTankName(self.__vehicle.shortUserName)
        model.setTankTypeIcon(self.__vehicle.typeBigIconResource())
        model.setTankLevel(int2roman(self.__vehicle.level))

    @replaceNoneKwargsModel
    def __updateC11nButton(self, lock=False, model=None):
        isEnabled = not lock and self.__vehicle.isCustomizationEnabled()
        if isEnabled:
            tooltipText = ''
        else:
            tooltipText = backport.text(R.strings.vehicle_customization.progressiveItemReward.gotoCustomizationButton.disabled.tooltip())
        model.setSecondaryButtonTooltip(tooltipText)
        model.setSecondaryButtonEnabled(isEnabled)

    def __onOkClick(self):
        self.destroyWindow()

    def __onAnimationSound(self):
        WWISE.WW_eventGlobal(SOUNDS.PROGRESSIVE_DECAL_COULD_BE_INSTALLED)
        WWISE.WW_setState(ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_GROUP, ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_ENTER)

    def __onShowC11nClick(self):
        BigWorld.callback(0.0, goToC11nStyledMode)
        self.destroy()


class StyleUnlockedWindow(LobbyWindow):

    def __init__(self, vehicleCD):
        super(StyleUnlockedWindow, self).__init__(content=StyleUnlockedView(vehicleCD), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return
