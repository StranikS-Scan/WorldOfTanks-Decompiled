# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/notifications/special_rewards_notification.py
from __future__ import absolute_import
from functools import partial
from gui.customization.constants import CustomizationModes, CustomizationModeSource
from helpers import dependency
from gui.Scaleform.daapi.view.lobby.customization.shared import isC11nEnabled, CustomizationTabs
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.gf_notifications.notification_base import NotificationBase
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showHangar, showStylePreview, selectVehicleInHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from open_bundle.gui.impl.gen.view_models.views.lobby.notifications.special_rewards_notification_model import SpecialRewardsNotificationModel
from open_bundle.helpers.bonuses.bonus_packers import findVehicleCD, packBonusModelAndTooltipData, composeBonuses, sortBonuses
from open_bundle.helpers.bonuses.bonuses_constants import ATTACHMENTS_TOKEN_NAME
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

class SpecialRewardsNotification(NotificationBase):
    __itemsCache = dependency.descriptor(IItemsCache)
    __openBundle = dependency.descriptor(IOpenBundleController)
    __c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, resId, *args, **kwargs):
        super(SpecialRewardsNotification, self).__init__(resId, SpecialRewardsNotificationModel(), *args, **kwargs)
        self.__allRewards = []

    @property
    def viewModel(self):
        return super(SpecialRewardsNotification, self).getViewModel()

    @property
    def bundleID(self):
        return self._getPayload()['bundleID']

    @property
    def cellRewards(self):
        return self._getPayload().get('randomBonus')

    def _getCallbacks(self):
        return super(SpecialRewardsNotification, self)._getCallbacks() + (('inventory', self.__onInventoryUpdate),)

    def _getEvents(self):
        return super(SpecialRewardsNotification, self)._getEvents() + ((self.viewModel.onShowReward, self.__onShowReward),)

    def _update(self):
        with self.viewModel.transaction() as tx:
            tx.setIsPopUp(self._isPopUp)
            tx.setIsButtonDisabled(not self._canNavigate())
            tx.setBundleType(self.__openBundle.getBundle(self.bundleID).type)
            self.__fillBonuses(model=tx)

    def _canNavigate(self):
        allRewards = self.__getAllRewards()
        vehicleCD = findVehicleCD(allRewards)
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD) if vehicleCD is not None else None
        isAvailable = vehicle.isInInventory if vehicle is not None else True
        return super(SpecialRewardsNotification, self)._canNavigate() and isAvailable

    def __getAllRewards(self):
        if not self.__allRewards:
            rewards = [self.cellRewards] if self.cellRewards is not None else []
            bonuses = composeBonuses(rewards)
            self.__allRewards = sortBonuses(bonuses)
        return self.__allRewards

    @replaceNoneKwargsModel
    def __fillBonuses(self, model=None):
        bonuses = self.__getAllRewards()
        bonusModels = model.getBonuses()
        bonusModels.clear()
        packBonusModelAndTooltipData(bonuses, bonusModels, showAttachmentsSets=True)

    def __onInventoryUpdate(self, _, diff):
        if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
            self._update()
        return

    @args2params(str, int)
    def __onShowReward(self, bonusType, bonusId):
        if self._canNavigate():
            if bonusType == 'customizations':
                style = self.__c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, bonusId)
                vehicleCD = getVehicleCDForStyle(style)
                showStylePreview(vehicleCD, style, backCallback=showHangar)
            elif bonusType == 'vehicles':
                self.__selectVehicle(vehicleCD=bonusId)
            elif bonusType in ('attachment', ATTACHMENTS_TOKEN_NAME):
                if isC11nEnabled():

                    def _callback():
                        ctx = self.__c11nService.getCtx()
                        ctx.changeMode(CustomizationModes.CUSTOM, source=CustomizationModeSource.NOTIFICATION)
                        ctx.mode.changeTab(tabId=CustomizationTabs.ATTACHMENTS)

                    self.__c11nService.showCustomization(tabId=CustomizationTabs.ATTACHMENTS, callback=_callback)
                else:
                    showHangar()

    def __selectVehicle(self, vehicleCD):
        if self.__openBundle.isRandomPrb():
            selectVehicleInHangar(vehicleCD, loadHangar=True)
        else:
            self.__openBundle.selectRandomBattle(partial(selectVehicleInHangar, vehicleCD, loadHangar=False))
