# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/wot_plus_entry_sub_presenter.py
from __future__ import absolute_import
from time import time
import typing
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.game_control.wot_plus.utils import ProBoostUtils
from gui.impl.dialogs.dialogs import showProBoostSwitchDialog, showProBoostConfirmDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.dialogs.wot_plus.pro_boost_confirm_dialog import _ProBoostConfirmDialogParams
from gui.impl.lobby.dialogs.wot_plus.pro_boost_switch_dialog import _ProBoostSwitchDialogVehicleParams, _ProBoostSwitchDialogParams
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter, EntryStateWithReason
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import getIconShopResource
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency, int2roman
from items.vehicles import getItemByCompactDescr
from renewable_subscription_common.settings_constants import PRO_BOOST_PDATA_KEY, RS_TIER
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.shared import IItemsCache
from wg_async import wg_await, wg_async
if typing.TYPE_CHECKING:
    from typing import Any, Dict, Generator
    from gui.shared.gui_items.Vehicle import Vehicle

class WotPlusEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __itemsCache = dependency.descriptor(IItemsCache)

    @wg_async
    def onNavigate(self):
        boostedVehicleInvID = self.__wotPlusCtrl.getProBoostedVehicleInvID()
        subscriptionStorage = self.__wotPlusCtrl.getSettingsStorage()
        currentVehicle = g_currentVehicle.item
        cooldown = subscriptionStorage.getProBoostCooldown(formatted=True)
        bonusPercentage = int(subscriptionStorage.getProBoostBonusFactors().xpFactor * 100)
        if not boostedVehicleInvID:
            vehicleUserName = currentVehicle.userName
            dialogParams = _ProBoostConfirmDialogParams(vehicleUserName, cooldown, bonusPercentage)
            result = yield wg_await(showProBoostConfirmDialog(dialogParams))
        else:
            vehicleFrom = self.__getVehicleSwitchWindowParams(self.__itemsCache.items.getVehicle(boostedVehicleInvID))
            vehicleTo = self.__getVehicleSwitchWindowParams(currentVehicle)
            dialogParams = _ProBoostSwitchDialogParams(vehicleFrom, vehicleTo, cooldown, bonusPercentage)
            result = yield wg_await(showProBoostSwitchDialog(dialogParams))
        if result is None or result.busy or not result.result:
            return
        else:
            self.__wotPlusCtrl.activateProBoostOnVehicle(g_currentVehicle.invID)
            return

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self.__wotPlusCtrl.onProBoostCooldownIsFinished, self.__onProBoostCooldownIsFinished), (self.__wotPlusCtrl.onDataChanged, self.__onProBoostDataChanged))

    def _getState(self):
        subSettings = self.__wotPlusCtrl.getSettingsStorage()
        if not (subSettings.isProBoostFeatureEnabled() and subSettings.isProBoostFeatureAvailable()):
            return VehicleMenuModel.UNAVAILABLE
        if g_currentVehicle.isInBattle():
            return VehicleMenuModel.DISABLED
        if not ProBoostUtils.isGameModeCompatibleForProBoost():
            params = {'tooltipKey': VehicleMenuModel.PRO_BOOST_TOOLTIP_INCOMPATIBLE_MODE}
            return EntryStateWithReason(state=VehicleMenuModel.DISABLED, reason=VehicleMenuModel.PRO_BOOST_TOOLTIP_INCOMPATIBLE_MODE, params=params)
        if not self.__wotPlusCtrl.canBeProBoosted(g_currentVehicle.intCD):
            params = {'tooltipKey': VehicleMenuModel.PRO_BOOST_TOOLTIP_INCOMPATIBLE_VEHICLE}
            return EntryStateWithReason(state=VehicleMenuModel.DISABLED, reason=VehicleMenuModel.PRO_BOOST_TOOLTIP_INCOMPATIBLE_VEHICLE, params=params)
        boostedVehicle = self.__wotPlusCtrl.getProBoostedVehicleInvID()
        activationTime = self.__wotPlusCtrl.getProBoostActivationTime()
        cooldownTimestamp = activationTime + subSettings.getProBoostCooldown() if activationTime else 0
        isActiveState = boostedVehicle == g_currentVehicle.invID
        isLockedState = cooldownTimestamp > int(time())
        if isActiveState and isLockedState:
            params = {'tooltipKey': VehicleMenuModel.PRO_BOOST_TOOLTIP_LOCKED_ACTIVE,
             'isActive': True,
             'expirationTimestamp': cooldownTimestamp}
            return EntryStateWithReason(state=VehicleMenuModel.DISABLED, reason=VehicleMenuModel.PRO_BOOST_TOOLTIP_LOCKED_ACTIVE, params=params)
        if isActiveState:
            params = {'tooltipKey': VehicleMenuModel.PRO_BOOST_TOOLTIP_ACTIVE,
             'isActive': True}
            return EntryStateWithReason(state=VehicleMenuModel.DISABLED, reason=VehicleMenuModel.PRO_BOOST_TOOLTIP_ACTIVE, params=params)
        if isLockedState and boostedVehicle:
            boostedVehicleCD = self.__itemsCache.items.getVehicle(boostedVehicle).intCD
            params = {'tooltipKey': VehicleMenuModel.PRO_BOOST_TOOLTIP_LOCKED,
             'expirationTimestamp': cooldownTimestamp,
             'vehicle': getItemByCompactDescr(boostedVehicleCD).userString}
            return EntryStateWithReason(state=VehicleMenuModel.DISABLED, reason=VehicleMenuModel.PRO_BOOST_TOOLTIP_LOCKED, params=params)
        return VehicleMenuModel.WARNING if not boostedVehicle else VehicleMenuModel.ENABLED

    def __onProBoostDataChanged(self, data):
        if RS_TIER in data or PRO_BOOST_PDATA_KEY in data:
            self.packEntry()

    def __getVehicleSwitchWindowParams(self, vehicle):
        return _ProBoostSwitchDialogVehicleParams(vehicleItemImagePath=getIconShopResource(vehicle.name, STORE_CONSTANTS.ICON_SIZE_SMALL), vehicleName=vehicle.userName, vehicleTier=int2roman(vehicle.level), vehicleIcon=self.__getType48x48IconResource(vehicle.type))

    def __getType48x48IconResource(self, vehicleType, isElite=False):
        return R.images.gui.maps.icons.vehicleTypes.c_48x48.dyn(replaceHyphenToUnderscore(vehicleType + '_elite' if isElite else vehicleType))

    def __onPrbEntitySwitched(self, *args, **kwargs):
        self.packEntry()

    def __onProBoostCooldownIsFinished(self, *args, **kwargs):
        self.packEntry()
