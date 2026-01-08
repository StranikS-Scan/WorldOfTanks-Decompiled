# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/style_unlocked_view/style_unlocked_view.py
import BigWorld
import WWISE
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.customization.shared import isVehicleCanBeCustomized
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.customization.style_unlocked_view.style_unlocked_view_model import StyleUnlockedViewModel
from gui.impl.lobby.customization.shared import goToC11nStyledMode
from gui.impl.lobby.progressive_reward.progressive_award_sounds import ProgressiveRewardSoundEvents
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.gen import R
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, int2roman
from items.components.c11n_constants import UNBOUND_VEH_KEY
from gui.shared.system_factory import collectCustomizationHangarDecorator
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException

class StyleUnlockedView(ViewImpl):
    c11nService = dependency.descriptor(ICustomizationService)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.customization.style_unlocked_view.StyleUnlockedView())
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
        WWISE.WW_setState(ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_GROUP, ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_EXIT)
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

    def _updateC11nButton(self, *_):
        self.__updateC11nButton(lock=False)

    def _addListeners(self):
        self.viewModel.onOkClick += self.__onOkClick
        self.viewModel.onSecondaryClick += self.__onShowC11nClick
        self.viewModel.onAnimationSound += self.__onAnimationSound
        lsm = getLobbyStateMachine()
        lsm.onVisibleRouteChanged += self.__onVisibleRouteChanged
        g_clientUpdateManager.addCallbacks({'inventory': self._updateC11nButton})
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self._updateC11nButton})

    def _removeListeners(self):
        self.viewModel.onOkClick -= self.__onOkClick
        self.viewModel.onSecondaryClick -= self.__onShowC11nClick
        self.viewModel.onAnimationSound -= self.__onAnimationSound
        lsm = getLobbyStateMachine()
        lsm.onVisibleRouteChanged -= self.__onVisibleRouteChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __setVehicleInfo(self, model):
        model.setTankName(self.__vehicle.shortUserName)
        model.setTankTypeIcon(self.__vehicle.typeBigIconResource())
        model.setTankLevel(int2roman(self.__vehicle.level))

    def __onVisibleRouteChanged(self, routeInfo):
        from gui.lobby_state_machine.states import isHangarState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import HeroTankPreviewState
        from gui.Scaleform.daapi.view.lobby.battle_queue.states import CommonBattleQueueState
        if isHangarState(routeInfo.state):
            self._updateC11nButton()
        elif isinstance(routeInfo.state, (HeroTankPreviewState, CommonBattleQueueState)):
            self.__updateC11nButton(lock=True)

    @replaceNoneKwargsModel
    def __updateC11nButton(self, lock=False, model=None):
        isEnabled = not lock and self.__isCustEnabledForActiveVehicle()
        if any((handler() for handler in collectCustomizationHangarDecorator())):
            isEnabled = False
        if isEnabled:
            tooltipText = ''
        else:
            tooltipText = backport.text(R.strings.vehicle_customization.progressiveItemReward.gotoCustomizationButton.disabled.tooltip())
        model.setSecondaryButtonTooltip(tooltipText)
        model.setSecondaryButtonEnabled(isEnabled)

    def __isCustEnabledForActiveVehicle(self):
        currentVehicle = g_currentVehicle.item
        if currentVehicle is not None and currentVehicle.intCD != self.__vehicle.intCD:
            vehicle = currentVehicle
        else:
            vehicle = self.__vehicle
        return vehicle.isCustomizationEnabled() and isVehicleCanBeCustomized(vehicle, GUI_ITEM_TYPE.STYLE)

    def __onOkClick(self):
        self.destroyWindow()

    def __onAnimationSound(self):
        WWISE.WW_eventGlobal(SOUNDS.PROGRESSIVE_DECAL_COULD_BE_INSTALLED)
        WWISE.WW_setState(ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_GROUP, ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_ENTER)

    def __onShowC11nClick(self):
        BigWorld.callback(0.0, goToC11nStyledMode)
        self.destroy()


class StyleUnlockedWindow(LobbyNotificationWindow):

    def __init__(self, vehicleCD):
        super(StyleUnlockedWindow, self).__init__(content=StyleUnlockedView(vehicleCD))
