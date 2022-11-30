# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_style_reward_view.py
import itertools
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.ny_marketplace_view_model import VehicleState
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_style_reward_view_model import NewYearStyleRewardViewModel
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.lobby.new_year.marketplace import createBonuses, showStyleFromMarketPlace
from gui.impl.lobby.new_year.ny_views_helpers import marketPlaceKeySortOrder
from gui.impl.new_year.new_year_bonus_packer import getNYMarketplaceRewardBonuses
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from frameworks.wulf import ViewSettings, WindowLayer
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController
_MAX_CAPACITY = 8

class NewYearStyleRewardView(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    _service = dependency.descriptor(ICustomizationService)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_tooltips', '_showStyleBonus', '_showStyleVehicleID')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.StyleRewardView())
        settings.model = NewYearStyleRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearStyleRewardView, self).__init__(settings)
        self._tooltips = {}
        self._showStyleBonus = None
        self._showStyleVehicleID = None
        return

    @property
    def viewModel(self):
        return super(NewYearStyleRewardView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NewYearStyleRewardView, self).createToolTip(event)

    def _onLoading(self, yearName, kitName, rewards, *args, **kwargs):
        super(NewYearStyleRewardView, self)._onLoading(*args, **kwargs)
        if rewards:
            self.__setRewards(yearName, kitName, rewards)
            self.__updateVehicleState()

    def _initialize(self, *args, **kwargs):
        super(NewYearStyleRewardView, self)._initialize(*args, **kwargs)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.AWARD_STYLE_SCREEN)
        setOverlayHangarGeneral(True)

    def _finalize(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.AWARD_STYLE_SCREEN_EXIT)
        setOverlayHangarGeneral(False)
        self._showStyleBonus = None
        self._showStyleVehicleID = None
        super(NewYearStyleRewardView, self)._finalize()
        return

    def _getEvents(self):
        return ((self._nyController.onStateChanged, self.__onEventStateChanged), (self.viewModel.onStylePreview, self.__onStylePreview))

    def _getCallbacks(self):
        return (('cache', self.__onCacheUpdated),)

    def __setRewards(self, yearName, kitName, rewards):
        bonuses = createBonuses(rewards)
        rewardBonuses = getNYMarketplaceRewardBonuses(bonuses, isMerge=False, sortKey=lambda b: marketPlaceKeySortOrder(*b))
        self._showStyleBonus = styleBonus = findFirst(lambda b: b.get('custType', None) == 'style', itertools.chain(*(b.getValue() for b in bonuses)), None)
        with self.getViewModel().transaction() as model:
            model.setStyleName('{}_{}'.format(kitName, yearName))
            model.setIsStyle(styleBonus is not None)
            rewardsList = model.getRewards()
            rewardsList.clear()
            for index, (bonus, tooltip) in enumerate(rewardBonuses):
                tooltipId = str(index)
                bonus.setTooltipId(tooltipId)
                bonus.setIndex(index)
                self._tooltips[tooltipId] = tooltip
                rewardsList.addViewModel(bonus)

            rewardsList.invalidate()
        return

    def __onCacheUpdated(self, diff):
        if 'vehsLock' in diff:
            self.__updateVehicleState()

    def __onEventStateChanged(self):
        if not self._nyController.isEnabled():
            self.destroyWindow()

    def __onStylePreview(self):
        vehicle = g_currentPreviewVehicle.item
        actualVehicle = self._itemsCache.items.getItemByCD(vehicle.intCD) if vehicle else None
        if not actualVehicle or not actualVehicle.isCustomizationEnabled():
            return
        else:
            self._showStyleVehicleID = actualVehicle.invID
            g_currentPreviewVehicle.selectNoVehicle()
            g_currentPreviewVehicle.resetAppearance()
            g_eventBus.handleEvent(events.NyMarketPlaceRewardEvent(events.NyMarketPlaceRewardEvent.ON_VEHICLE_APPEARANCE_RESET), EVENT_BUS_SCOPE.LOBBY)
            self._hangarSpace.onVehicleChanged += self.__delayedShowCustomization
            self._hangarSpace.onSpaceChanged += self.__delayedShowCustomization
            return

    def __delayedShowCustomization(self):
        self._hangarSpace.onVehicleChanged -= self.__delayedShowCustomization
        self._hangarSpace.onSpaceChanged -= self.__delayedShowCustomization
        styleID = self._showStyleBonus['id']
        vehInvID = self._showStyleVehicleID
        self.destroyWindow()
        showStyleFromMarketPlace(styleID, vehInvID)

    def __updateVehicleState(self):
        vehicle = g_currentPreviewVehicle.item
        actualVehicle = self._itemsCache.items.getItemByCD(vehicle.intCD) if vehicle else None
        if actualVehicle:
            with self.viewModel.transaction() as model:
                model.setIsVehicleCustomizationEnabled(actualVehicle.isCustomizationEnabled())
                if actualVehicle.isCustomizationEnabled():
                    model.setVehicleState(VehicleState.DEFAULT.value)
                elif not actualVehicle.isInInventory:
                    model.setVehicleState(VehicleState.NOT_IN_INVENTORY.value)
                elif actualVehicle.isInUnit:
                    model.setVehicleState(VehicleState.IN_UNIT.value)
                elif actualVehicle.isBroken:
                    model.setVehicleState(VehicleState.BROKEN.value)
                elif actualVehicle.isInBattle:
                    model.setVehicleState(VehicleState.IN_BATTLE.value)
                else:
                    model.setVehicleState(VehicleState.CUSTOMIZATION_UNAVAILABLE.value)
        return


class NewYearStyleRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearStyleRewardWindow, self).__init__(content=NewYearStyleRewardView(*args, **kwargs), layer=WindowLayer.FULLSCREEN_WINDOW)
