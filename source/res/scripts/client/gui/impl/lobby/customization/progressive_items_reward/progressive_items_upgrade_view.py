# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/progressive_items_reward/progressive_items_upgrade_view.py
import BigWorld
import WWISE
from CurrentVehicle import g_currentVehicle
from adisp import adisp_process
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.shared import getItemInstalledCount
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import currentHangarIsBattleRoyale
from gui.customization.shared import isVehicleCanBeCustomized
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.progressive_items_reward.progressive_items_reward_view_model import ProgressiveItemsRewardViewModel
from gui.impl.lobby.customization.shared import goToC11nStyledMode
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ViewEventType
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import OutfitApplier
from gui.shared.image_helper import getTextureLinkByID
from helpers import dependency, int2roman
from items.components.c11n_constants import SeasonType, UNBOUND_VEH_KEY
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IEventBattlesController
from soft_exception import SoftException
from gui.impl.lobby.progressive_reward.progressive_award_sounds import ProgressiveRewardSoundEvents

class ProgressiveItemsUpgradeView(ViewImpl):
    __slots__ = ('__item', '__vehicle', '__level', '__itemsInNeedToUpgrade')
    __c11nService = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.customization.progressive_items_reward.ProgressiveItemsUpgradeView())
        settings.model = ProgressiveItemsRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ProgressiveItemsUpgradeView, self).__init__(settings)
        self.__item = None
        self.__vehicle = None
        self.__level = 0
        self.__itemsInNeedToUpgrade = {}
        return

    @property
    def viewModel(self):
        return super(ProgressiveItemsUpgradeView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ProgressiveItemsUpgradeView, self)._initialize(*args, **kwargs)
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(ProgressiveItemsUpgradeView, self)._finalize()

    def _onLoading(self, itemCD, vehicleCD, progressionLevel, showSecondButton):
        self.__item = self.__itemsCache.items.getItemByCD(itemCD)
        self.__vehicle = self.__itemsCache.items.getItemByCD(vehicleCD) if vehicleCD != UNBOUND_VEH_KEY else g_currentVehicle.item
        self.__level = progressionLevel
        self.__itemsInNeedToUpgrade = self.__getItemsInNeedToUpgrade()
        if self.__item is None:
            raise SoftException('invalid item: &s', itemCD)
        if self.__vehicle is None:
            raise SoftException('invalid vehicle: &s', vehicleCD)
        if self.__level > 1 and not self.__itemsInNeedToUpgrade and getItemInstalledCount(self.__item) > 0:
            self.__resetItemNovelty()
        isNewItem = self.__level == 1
        with self.viewModel.transaction() as model:
            model.setIsNewItem(isNewItem)
            showSecondButton = showSecondButton and isVehicleCanBeCustomized(self.__vehicle, GUI_ITEM_TYPE.STYLE, itemsFilter=lambda item: item.isProgressionRequiredCanBeEdited(self.__vehicle.intCD))
            if vehicleCD != UNBOUND_VEH_KEY:
                self.__setVehicleInfo(model)
            self.__setItemInfo(model)
            self.__setButtons(model, showSecondButton)
            self.__updateButtons(model=model)
        if isNewItem:
            eventName = SOUNDS.NEW_PROGRESSIVE_DECAL
        else:
            eventName = SOUNDS.PROGRESSIVE_DECAL_UPGRADE
        WWISE.WW_eventGlobal(eventName)
        WWISE.WW_setState(ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_GROUP, ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_ENTER)
        return

    def _updateButtons(self, *_):
        self.__updateButtons(lock=False)

    def __addListeners(self):
        self.viewModel.onOkClick += self.__onOkClick
        self.viewModel.onSecondaryClick += self.__onShowC11nClick
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCallbacks({'inventory': self._updateButtons})
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self._updateButtons})

    def __removeListeners(self):
        self.viewModel.onOkClick -= self.__onOkClick
        self.viewModel.onSecondaryClick -= self.__onShowC11nClick
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __loadViewHandler(self, event):
        if event.alias == VIEW_ALIAS.LOBBY_HANGAR:
            self._updateButtons()
        elif event.alias in (VIEW_ALIAS.HERO_VEHICLE_PREVIEW, VIEW_ALIAS.BATTLE_QUEUE):
            self.__updateButtons(lock=True)

    def __setVehicleInfo(self, model):
        model.setTankName(self.__vehicle.shortUserName)
        model.setTankTypeIcon(self.__vehicle.typeBigIconResource())
        model.setTankLevel(int2roman(self.__vehicle.level))
        model.setShowTankLevel(self.__vehicle.level > 0)

    def __setItemInfo(self, model):
        if self.__level == 1:
            congratsText = backport.text(R.strings.vehicle_customization.progressiveItemReward.congrats.received())
            itemName = backport.text(R.strings.vehicle_customization.progressiveItemReward.itemName(), itemName=self.__item.userName)
        else:
            congratsText = backport.text(R.strings.vehicle_customization.progressiveItemReward.congrats.upgraded(), level=self.__level)
            itemName = backport.text(R.strings.vehicle_customization.progressiveItemReward.itemName.upgraded(), itemName=self.__item.userName)
        model.setCongratsText(congratsText)
        model.setItemName(itemName)
        model.setFormFactor(self.__item.formfactor)
        itemIcons = model.getItemIcons()
        if self.__level > 1:
            itemIcons.addString(self.__getIcon(self.__level - 1))
        itemIcons.addString(self.__getIcon(self.__level))

    def __getIcon(self, level):
        texture = self.__item.getTextureByProgressionLevel(self.__item.texture, level)
        return getTextureLinkByID(texture)

    def __setButtons(self, model, showSecondButton=False):
        if not self.__itemsInNeedToUpgrade:
            model.setOkButtonLabel(backport.text(R.strings.vehicle_customization.progressiveItemReward.okButton.label()))
        else:
            model.setOkButtonLabel(backport.text(R.strings.vehicle_customization.progressiveItemReward.applyButton.label()))
        if showSecondButton:
            model.setSecondaryButtonLabel(backport.text(R.strings.vehicle_customization.progressiveItemReward.gotoCustomizationButton.label()))

    @replaceNoneKwargsModel
    def __updateButtons(self, lock=False, model=None):
        okEnabled = True
        isEventHangar = self.__gameEventCtrl.isEventPrbActive()
        isBRHangar = currentHangarIsBattleRoyale()
        vehCustomizationEbabled = self.__vehicle.isCustomizationEnabled()
        c11nEnabled = not lock and vehCustomizationEbabled and not isEventHangar and not isBRHangar
        if self.__itemsInNeedToUpgrade:
            okEnabled = c11nEnabled
            if okEnabled:
                tooltipRes = R.strings.vehicle_customization.progressiveItemReward.applyButton.tooltip()
            else:
                tooltipRes = R.strings.vehicle_customization.progressiveItemReward.disabledApplyButton.tooltip()
            model.setOkButtonTooltip(backport.text(tooltipRes))
        model.setIsOkButtonEnabled(okEnabled)
        if c11nEnabled:
            tooltipText = ''
        else:
            tooltipText = backport.text(R.strings.vehicle_customization.progressiveItemReward.gotoCustomizationButton.disabled.tooltip())
        model.setIsSecondaryButtonEnabled(c11nEnabled)
        model.setSecondaryButtonTooltip(tooltipText)

    def __getItemsInNeedToUpgrade(self):
        itemsInNeedToUpgrade = {}
        for season in SeasonType.RANGE:
            outfit = self.__vehicle.getOutfit(season)
            if outfit is not None:
                components = [ slotData.component for slotData in outfit.slotsData() if slotData.intCD == self.__item.intCD and slotData.component.progressionLevel != 0 ]
                if components:
                    itemsInNeedToUpgrade.update({season: components})

        return itemsInNeedToUpgrade

    def __onOkClick(self):
        if not self.__itemsInNeedToUpgrade:
            self.__onWindowClose()
        else:
            self.__onApplyClick()
            self.__onWindowClose()

    def __onWindowClose(self):
        WWISE.WW_setState(ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_GROUP, ProgressiveRewardSoundEvents.PROGRESSIVE_REWARD_VIEW_EXIT)
        self.destroyWindow()

    def __onApplyClick(self):
        if self.__itemsInNeedToUpgrade:
            self.__upgradeItems()

    @adisp_process
    def __upgradeItems(self):
        self.__resetItemNovelty()
        vehicle = self.__vehicle
        modifiedOutfits = {}
        for season, components in self.__itemsInNeedToUpgrade.iteritems():
            for component in components:
                component.progressionLevel = 0

            outfit = vehicle.getOutfit(season)
            if outfit is not None:
                modifiedOutfits.update({season: outfit.copy()})

        yield OutfitApplier(vehicle, [ (outfit, season) for season, outfit in modifiedOutfits.iteritems() ]).request()
        return

    def __resetItemNovelty(self):
        BigWorld.player().shop.resetC11nItemsNovelty([(self.__vehicle.intCD, self.__item.intCD)], callback=None)
        return

    def __onShowC11nClick(self):
        BigWorld.callback(0.0, goToC11nStyledMode)
        self.destroy()


class ProgressiveItemsUpgradeWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, itemCD, vehicleCD, progressionLevel, showSecondButton):
        super(ProgressiveItemsUpgradeWindow, self).__init__(content=ProgressiveItemsUpgradeView(itemCD, vehicleCD, progressionLevel, showSecondButton))
