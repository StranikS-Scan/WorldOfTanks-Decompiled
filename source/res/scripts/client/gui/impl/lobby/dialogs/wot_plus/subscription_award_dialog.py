# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/wot_plus/subscription_award_dialog.py
import json
from typing import TYPE_CHECKING, List, Dict
import WWISE
from chat_shared import SYS_MESSAGE_TYPE
from constants import IS_CHINA
from gui.Scaleform.daapi.view.lobby.wot_plus.sound_constants import SOUNDS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.date_time_formats import DateTimeFormatsEnum
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_button_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_view_model import MonoDialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.page.header.wot_plus_subscription_model import WotPlusPeriodicityEnum
from gui.impl.lobby.dialogs.wot_plus.base_dialog import BaseDialog
from gui.server_events.bonuses_wot_plus import getAvailableCoreBonuses, getUniqueAvailableProBonuses
from gui.shared.event_dispatcher import showWotPlusInfoPage
from gui.shared.formatters.date_time import getRegionalDateTime
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from helpers import dependency
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from renewable_subscription_common.settings_constants import WotPlusTier, PRO_THRESHOLD_DAYS
from renewable_subscription_common.settings_helpers import SubscriptionSettingsStorage
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.system_messages import ISystemMessages
from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource
if TYPE_CHECKING:
    from gui.server_events.bonuses import WoTPlusBonus
    from gui.Scaleform.SystemMessagesInterface import SystemMessagesInterface
    from gui.game_control.wot_plus_controller import WotPlusController
BG_IMAGE_RESOURCE_BY_TIER = {WotPlusTier.CORE: R.images.gui.maps.icons.subscription.activation_dialog.background_core(),
 WotPlusTier.PRO: R.images.gui.maps.icons.subscription.activation_dialog.background_pro()}
PERIODICITY_TO_RESOURCE = {WotPlusPeriodicityEnum.P6MONTHS: R.strings.dialogs.wotPlusActivationDialog.planInterval6(),
 WotPlusPeriodicityEnum.P12MONTHS: R.strings.dialogs.wotPlusActivationDialog.planInterval12()}

class SubscriptionAwardDialog(BaseDialog):
    LAYOUT_ID = R.views.mono.dialogs.wot_plus_activated_dialog()
    _systemMessages = dependency.descriptor(ISystemMessages)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def __init__(self, unlockedTier, expirationTime, billingDays, messageType, *args, **kwargs):
        self._unlockedTier = unlockedTier
        self._storage = SubscriptionSettingsStorage(self._unlockedTier)
        self._expirationTime = expirationTime
        if billingDays < PRO_THRESHOLD_DAYS:
            self._periodicity = WotPlusPeriodicityEnum.P6MONTHS
        else:
            self._periodicity = WotPlusPeriodicityEnum.P12MONTHS
        self._messageType = messageType
        self.BACKGROUND_IMAGE = BG_IMAGE_RESOURCE_BY_TIER[self._unlockedTier] if not IS_CHINA else BG_IMAGE_RESOURCE_BY_TIER[WotPlusTier.CORE]
        contentParams = self._buildContentParams(self._unlockedTier)
        resourcesParams = self._buildResourcesParams(self._unlockedTier)
        super(SubscriptionAwardDialog, self).__init__(contentParams, resourcesParams, *args, **kwargs)

    def _onLoading(self, *args, **kwargs):
        super(SubscriptionAwardDialog, self)._onLoading(*args, **kwargs)
        WWISE.WW_eventGlobal(backport.sound(R.sounds.gui_reward_screen_general()))
        WWISE.WW_setState(SOUNDS.OVERLAY_HANGAR_GENERAL, SOUNDS.OVERLAY_HANGAR_GENERAL_ON)

    def _finalize(self):
        super(SubscriptionAwardDialog, self)._finalize()
        self._sendNotificationsOnClose()
        WWISE.WW_setState(SOUNDS.OVERLAY_HANGAR_GENERAL, SOUNDS.OVERLAY_HANGAR_GENERAL_OFF)

    def _buildContentParams(self, unlockedTier):
        if IS_CHINA or unlockedTier == WotPlusTier.CORE:
            return self.__buildWotPlusCoreContent()
        return self.__buildWotPlusProContent() if unlockedTier == WotPlusTier.PRO else {}

    def _buildResourcesParams(self, unlockedTier):
        if IS_CHINA or unlockedTier == WotPlusTier.CORE:
            return self.__buildWotPlusCoreResources()
        return self.__buildWotPlusProResources() if unlockedTier == WotPlusTier.PRO else {}

    def __buildWotPlusCoreContent(self):
        content = {'descriptionStringParams': json.dumps({'date': getRegionalDateTime(self._expirationTime or 0, DateTimeFormatsEnum.SHORTDATE)})}
        coreBenefits = getAvailableCoreBonuses(self._storage)
        benefitsData = self.__buildBenefits(coreBenefits)
        content.update({'benefits': json.dumps(benefitsData)})
        return content

    def __buildWotPlusProContent(self):
        content = {'descriptionStringParams': json.dumps({'date': getRegionalDateTime(self._expirationTime or 0, DateTimeFormatsEnum.SHORTDATE),
                                     'planInterval': backport.text(PERIODICITY_TO_RESOURCE[self._periodicity or WotPlusPeriodicityEnum.P6MONTHS])})}
        proBenefits = getUniqueAvailableProBonuses(self._storage)
        coreBenefits = getAvailableCoreBonuses(self._storage)
        coreBenefitsData = self.__buildBenefits(coreBenefits)
        proBenefitsData = self.__buildBenefits(proBenefits)
        content.update({'benefits': json.dumps(coreBenefitsData),
         'emphasizedBenefits': json.dumps(proBenefitsData)})
        return content

    def __buildWotPlusCoreResources(self):
        if IS_CHINA:
            titleString = backport.text(R.strings.dialogs.wotPlusActivationDialog.cn.heading())
        else:
            titleString = backport.text(R.strings.dialogs.wotPlusActivationDialog.core.heading())
        return {'titleString': titleString,
         'iconImage': backport.image(R.images.gui.maps.icons.subscription.activation_dialog.core()),
         'iconGlowImage': backport.image(R.images.gui.maps.icons.subscription.activation_dialog.icon_glow_core()),
         'descriptionString': backport.text(R.strings.dialogs.wotPlusActivationDialog.core.description())}

    def __buildWotPlusProResources(self):
        return {'titleString': backport.text(R.strings.dialogs.wotPlusActivationDialog.pro.heading()),
         'iconImage': backport.image(R.images.gui.maps.icons.subscription.activation_dialog.pro()),
         'iconGlowImage': backport.image(R.images.gui.maps.icons.subscription.activation_dialog.icon_glow_pro()),
         'descriptionString': backport.text(R.strings.dialogs.wotPlusActivationDialog.pro.description())}

    def __buildBenefits(self, benefitsList):
        bonusPacker = getDefaultBonusPacker()
        benefitsData = []
        for benefit in benefitsList:
            packedBonus = bonusPacker.pack(benefit)[0]
            benefitsData.append({'type': packedBonus.getName(),
             'label': packedBonus.getLabel()})

        return benefitsData

    def _setButtons(self):
        with self.viewModel.transaction() as vm:
            buttonsArray = vm.getButtons()
            buttonsArray.clear()
            self._addButton(self._buildButton(MonoDialogTemplateViewModel.ACTION_CONFIRM, R.strings.dialogs.wotPlusActivationDialog.confirmation(), ButtonType.PRIMARY, False))
            self._addButton(self._buildButton(MonoDialogTemplateViewModel.ACTION_SECONDARY, R.strings.dialogs.wotPlusActivationDialog.details(), ButtonType.SECONDARY, False))

    def _onInfo(self):
        showWotPlusInfoPage(WotPlusInfoPageSource.REWARD_SCREEN, useCustomSoundSpace=True)

    def _sendNotificationsOnClose(self):
        if IS_CHINA:
            sysMessageType = SCH_CLIENT_MSG_TYPE.WOTPLUS_SUBSCRIPTION_UNLOCKED
        else:
            if self._messageType == SYS_MESSAGE_TYPE.wotPlusUpgrade.index():
                return
            if self._unlockedTier == WotPlusTier.PRO:
                sysMessageType = SYS_MESSAGE_TYPE.wotPlusProUnlocked.index()
            else:
                sysMessageType = SYS_MESSAGE_TYPE.wotPlusCoreUnlocked.index()
        self._systemMessages.proto.serviceChannel.pushClientMessage({'expiryTime': self._expirationTime,
         'periodicity': self._periodicity}, sysMessageType)
        self._wotPlusCtrl.processSwitchNotifications()

    def _onAction(self, event):
        super(SubscriptionAwardDialog, self)._onAction(event)
        actionType = event.get('action')
        if actionType == MonoDialogTemplateViewModel.ACTION_SECONDARY:
            self._onInfo()
            self.destroy()
