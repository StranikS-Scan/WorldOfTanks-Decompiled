# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/notifications/special_rewards_notification.py
from __future__ import absolute_import
from functools import partial
from future.utils import viewitems
from gui.customization.constants import CustomizationModes, CustomizationModeSource
from helpers import dependency
from gui.Scaleform.daapi.view.lobby.customization.shared import isC11nEnabled, CustomizationTabs
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.gf_notifications.notification_base import NotificationBase
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.event_dispatcher import showHangar, showStylePreview, selectVehicleInHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from open_bundle.gui.impl.gen.view_models.views.lobby.notifications.special_rewards_notification_model import SpecialRewardsNotificationModel
from open_bundle.helpers.bonuses.bonus_packers import packBonusModelAndTooltipData, sortBonuses
from open_bundle.helpers.bonuses.bonuses_constants import ATTACHMENTS_TOKEN_NAME
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from skeletons.gui.customization import ICustomizationService

class SpecialRewardsNotification(NotificationBase):
    __openBundle = dependency.descriptor(IOpenBundleController)
    __c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, resId, *args, **kwargs):
        super(SpecialRewardsNotification, self).__init__(resId, SpecialRewardsNotificationModel(), *args, **kwargs)

    @property
    def viewModel(self):
        return super(SpecialRewardsNotification, self).getViewModel()

    @property
    def bundleID(self):
        return self._getPayload()['bundleID']

    @property
    def cellRewards(self):
        return self._getPayload().get('randomBonus')

    def _getEvents(self):
        return super(SpecialRewardsNotification, self)._getEvents() + ((self.viewModel.onShowReward, self.__onShowReward),)

    def _update(self):
        allRewards = {}
        if self.cellRewards is not None:
            allRewards.update(self.cellRewards)
        with self.viewModel.transaction() as tx:
            tx.setIsPopUp(self._isPopUp)
            tx.setIsButtonDisabled(not self._canNavigate())
            tx.setBundleType(self.__openBundle.getBundle(self.bundleID).type)
            self.__fillBonuses(allRewards, model=tx)
        return

    @replaceNoneKwargsModel
    def __fillBonuses(self, bonusesInfo, model=None):
        bonuses = []
        for k, v in viewitems(bonusesInfo):
            bonuses.extend(getNonQuestBonuses(k, v))

        bonuses = sortBonuses(bonuses)
        bonusModels = model.getBonuses()
        bonusModels.clear()
        packBonusModelAndTooltipData(bonuses, bonusModels, showAttachmentSet=True)

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
