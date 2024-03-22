# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/retrain_single_dialog.py
import BigWorld
from typing import TYPE_CHECKING, Any, Optional
import SoundGroups
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.impl.auxiliary.tankman_operations import packRetrainTankman, packSkills
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.dialogs.retrain_role_model import RetrainRoleModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.retrain_single_dialog_model import RetrainSingleDialogModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.role_change_model import DisableState
from gui.impl.lobby.crew.crew_helpers.skill_helpers import isTmanSkillIrrelevant
from gui.impl.lobby.crew.crew_sounds import SOUNDS
from gui.impl.lobby.crew.dialogs.price_cards_content.retrain_single_price_list import RetrainSinglePriceList
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.Tankman import Tankman, NO_SLOT
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TAGS
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.items_actions import factory
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from items.tankmen import TankmanDescr
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from uilogging.crew5075.loggers import Crew5075DialogLogger
from uilogging.crew5075.logging_constants import Crew5075DialogKeys
if TYPE_CHECKING:
    pass
_LOC = R.strings.dialogs.retrain

class RetrainSingleDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_tankman', '_vehicle', '_priceListContent', '_roles', '_targetRole', '_isChangeRoleVisible', '_beforeActions', '_isRoleChangeForced', '_lastChangeRoleChecked', '_toolTipMgr', '_targetSlotIdx', '_nativeTankmanRoles')
    LAYOUT_ID = R.views.lobby.crew.dialogs.RetrainSingleDialog()
    VIEW_MODEL = RetrainSingleDialogModel
    _UI_LOGGER_CLASS = Crew5075DialogLogger
    _itemsCache = dependency.descriptor(IItemsCache)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, tankmanId, vehicleCD, targetRole=None, targetSlotIdx=None, isChangeRoleVisible=False, beforeActions=None, **kwargs):
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        self._vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        self._isChangeRoleVisible = isChangeRoleVisible
        self._beforeActions = beforeActions or []
        self._toolTipMgr = self._appLoader.getApp().getToolTipMgr()
        self._nativeTankmanRoles = self._tankman.descriptor.nativeRoles
        if targetRole is None and targetSlotIdx is not None:
            targetRole = self._vehicle.descriptor.type.crewRoles[targetSlotIdx][0]
        ro = Tankman.TANKMEN_ROLES_ORDER
        vehicleRoles = list(dict.fromkeys([ role[0] for role in self._vehicle.descriptor.type.crewRoles if role[0] in self._nativeTankmanRoles ]))
        self._roles = sorted(vehicleRoles, cmp=lambda a, b: ro[a] - ro[b])
        if self._tankman.role in self._roles:
            self._roles.remove(self._tankman.role)
            self._lastChangeRoleChecked = self._isRoleChangeForced = False
            self._targetRole = targetRole or self._tankman.role
        else:
            self._lastChangeRoleChecked = self._isRoleChangeForced = True
            self._targetRole = self._vehicle.descriptor.type.crewRoles[targetSlotIdx or 0][0]
        self._targetSlotIdx = targetSlotIdx or self.__getSlotByVehicleRole(self._targetRole, self._vehicle)
        self._priceListContent = RetrainSinglePriceList(tankmanId, vehicleCD, self._targetRole)
        super(RetrainSingleDialog, self).__init__(loggingKey=Crew5075DialogKeys.RETRAIN_SINGLE, **kwargs)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if tooltipId == TooltipConstants.CREW_SKILL_UNTRAINED:
                args = ()
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_SKILL_UNTRAINED, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_SKILL_UNTRAINED
            if tooltipId == TooltipConstants.SKILLS_EFFICIENCY:
                args = (event.getArgument('tankmanInvId'), event.getArgument('skillEfficiency'))
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.SKILLS_EFFICIENCY, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return tooltipId
        return super(RetrainSingleDialog, self).createToolTip(event)

    def _getCallbacks(self):
        return (('inventory.1.compDescr', self._onVehiclesInventoryUpdate),)

    def _getEvents(self):
        return ((self._priceListContent.onPriceChange, self._onPriceChange), (self.viewModel.onRoleCheckChanged, self._onRoleChanged), (self.viewModel.onRoleSelected, self._onRoleSelected))

    def _onRoleChanged(self):
        isChecked = not self.viewModel.roleChange.getIsChecked()
        self._lastChangeRoleChecked = isChecked
        self.viewModel.roleChange.setIsChecked(isChecked)
        idx = self.viewModel.roleChange.getSelectedIdx()
        self._targetRole = self._roles[idx] if isChecked else self._tankman.role
        self._targetSlotIdx = self.__getSlotByVehicleRole(self._targetRole, self._vehicle)
        self._priceListContent.updateTargetRole(self._targetRole)
        SoundGroups.g_instance.playSound2D(SOUNDS.CREW_CHANGE_ROLE)

    def _onRoleSelected(self, args):
        idx = int(args.get('idx'))
        self._targetRole = self._roles[idx]
        self._targetSlotIdx = self.__getSlotByVehicleRole(self._targetRole, self._vehicle)
        self._priceListContent.updateTargetRole(self._targetRole)
        with self.viewModel.transaction() as vm:
            vm.roleChange.setSelectedIdx(idx)
            self._updateTankmanAfter(vm)

    def _onPriceChange(self, index=None):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        if submitBtn is not None:
            submitBtn.isDisabled = index is None
        with self.viewModel.transaction() as vm:
            self._updateTankmanAfter(vm)
            vm.setIsPriceSelected(index is not None)
            if self._isChangeRoleVisible:
                self._updateRoles(vm)
        return

    def _onVehiclesInventoryUpdate(self, diff):
        if self._vehicle.invID in diff and diff[self._vehicle.invID] is None:
            self.destroyWindow()
        return

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
        self.setChildView(self._priceListContent.layoutID, self._priceListContent)
        self.addButton(ConfirmButton(_LOC.submit(), isDisabled=True, buttonType=ButtonType.MAIN))
        self.addButton(CancelButton(_LOC.cancel()))
        self._initModel()
        super(RetrainSingleDialog, self)._onLoading(*args, **kwargs)

    def _getWarning(self):
        isPremium = self._tankman.descriptor.canUseSkills(self._vehicle.descriptor.type)
        isIrrelevant = self.__hasIrrelevantPerk()
        if isPremium and isIrrelevant:
            return R.strings.dialogs.retrain.warning.irrelevantPerkAndPrem()
        if isPremium:
            return R.strings.dialogs.retrain.warning.premiumVehicle()
        return R.strings.dialogs.retrain.warning.irrelevantPerk() if isIrrelevant else R.invalid()

    def _initModel(self):
        with self.viewModel.transaction() as vm:
            isRoleChange = self.__isRoleChanging()
            vm.setTitle(_LOC.title.single.complex() if isRoleChange else _LOC.title.single.simple())
            vm.setWarning(self._getWarning())
            packRetrainTankman(vm.tankmanBefore, self._tankman)
            vm.tankmanAfter.setRole(self._targetRole)
            vm.tankmanAfter.setIsFemale(self._tankman.isFemale)
            packSkills(vm.tankmanBefore.getSkills(), self._tankman)
            fillVehicleInfo(vm.targetVehicle, self._vehicle, tags=[VEHICLE_TAGS.PREMIUM])
            roleChangeModel = vm.roleChange
            roleChangeModel.setIsVisible(self._isChangeRoleVisible)
            roleChangeModel.setIsChecked(isRoleChange or self._isRoleChangeForced)
            roleChangeModel.setDisableState(self._getRoleChangeDisableState())
            rolesVl = roleChangeModel.getRoles()
            for role in self._roles:
                roleModel = RetrainRoleModel()
                roleModel.setIconName(role)
                roleModel.setIsTaken(self.__isRoleTaken(role))
                roleModel.setRolesCount(self.__countSlotsForRole(role))
                rolesVl.addViewModel(roleModel)

            rolesVl.invalidate()

    def _updateTankmanAfter(self, vm):
        _, skillEfficienciesAfter, _, _ = self._priceListContent.selectedOperationData
        if skillEfficienciesAfter is None:
            return
        else:
            tankman = self.__getTankmanWithTargetRole()
            packRetrainTankman(vm.tankmanAfter, tankman, skillEfficienciesAfter)
            packSkills(vm.tankmanAfter.getSkills(), tankman)
            return

    def _getRoleChangeDisableState(self):
        role = self._tankman.role
        if not any((roles[0] in self._nativeTankmanRoles and roles[0] != role for roles in self._vehicle.descriptor.type.crewRoles)):
            return DisableState.CREWLOCK
        if self._isRoleChangeForced:
            return DisableState.FORCED
        return DisableState.FREEOPERATION if not self._priceListContent.isRoleChangeAvailable else DisableState.AVAILABLE

    def _updateRoles(self, vm):
        state = self._getRoleChangeDisableState()
        vm.roleChange.setDisableState(state)
        vm.roleChange.setIsChecked(self._lastChangeRoleChecked and state in [DisableState.AVAILABLE, DisableState.FORCED])

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            if not self._retrainTankmen():
                return
        super(RetrainSingleDialog, self)._setResult(result)

    def _retrainTankmen(self):
        itemPrice, _, retrainKey = self._priceListContent.selectedPriceData
        operationPrice = itemPrice
        purchaseMoneyState = getPurchaseMoneyState(operationPrice.price)
        if purchaseMoneyState is MoneyForPurchase.NOT_ENOUGH:
            showBuyGoldForCrew(operationPrice.price.gold)
            return False
        if purchaseMoneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            purchaseGold = getPurchaseGoldForCredits(operationPrice.price)
            event_dispatcher.showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
            return False
        doActions = self._beforeActions
        if self._targetSlotIdx != NO_SLOT and self.__isRoleChanging() and retrainKey > 0:
            doActions.append((factory.CHANGE_ROLE_TANKMAN,
             self._tankman.invID,
             self._targetRole,
             self._vehicle.intCD,
             self._targetSlotIdx))
        doActions.append((factory.RETRAIN_TANKMAN,
         self._tankman.invID,
         self._vehicle.intCD,
         retrainKey,
         self.__isRoleChanging() and retrainKey > 0))
        tman = self._tankman
        if not (tman.isInTank and tman.role == self._targetRole and tman.vehicleInvID == self._vehicle.invID and tman.vehicleSlotIdx == self._targetSlotIdx):
            if self._targetSlotIdx != NO_SLOT and self.__isVehicleReady(self._vehicle):
                doActions.append((factory.EQUIP_TANKMAN,
                 self._tankman.invID,
                 self._vehicle.invID,
                 self._targetSlotIdx))
            elif self._tankman.isInTank:
                doActions.append((factory.UNLOAD_TANKMAN, self._tankman.vehicleInvID, self._tankman.vehicleSlotIdx))
        BigWorld.player().doActions(doActions)
        return True

    @staticmethod
    def __isVehicleReady(veh):
        return veh and veh.isInInventory and not veh.isLocked

    @staticmethod
    def __getSlotByVehicleRole(requestRole, veh):
        resSlotIdx = NO_SLOT
        if veh:
            for idx, roles in enumerate(veh.descriptor.type.crewRoles):
                if requestRole == roles[0]:
                    slotIdx, tman = veh.crew[idx]
                    if idx != slotIdx:
                        slotIdx, tman = veh.crew[slotIdx]
                    if tman is None:
                        return slotIdx
                    if resSlotIdx != NO_SLOT:
                        return resSlotIdx
                    resSlotIdx = slotIdx

        return resSlotIdx

    def __isRoleChanging(self):
        return self._targetRole != self._tankman.role

    def __isRoleTaken(self, role):
        for idx, roles in enumerate(self._vehicle.descriptor.type.crewRoles):
            slotIdx, vehTankman = self._vehicle.crew[idx]
            if idx != slotIdx:
                slotIdx, vehTankman = self._vehicle.crew[slotIdx]
            if role == roles[0] and not vehTankman:
                return False

        return True

    def __countSlotsForRole(self, role):
        countSlots = 0
        for _, roles in enumerate(self._vehicle.descriptor.type.crewRoles):
            if role == roles[0]:
                countSlots += 1

        return countSlots

    def __hasIrrelevantPerk(self):
        tankman = self.__getTankmanWithTargetRole()
        return any((isTmanSkillIrrelevant(tankman, skill) for skill in self._tankman.skills))

    def __getTankmanWithTargetRole(self):
        tmanDescr = TankmanDescr(self._tankman.strCD)
        tmanDescr.role = self._targetRole
        vehicleRoles = self._vehicle.descriptor.type.crewRoles
        vehicleSlotIdx = next((idx for idx, roles in enumerate(vehicleRoles) if roles[0] == self._targetRole), -1)
        return Tankman(tmanDescr.makeCompactDescr(), vehicle=self._vehicle, vehicleSlotIdx=vehicleSlotIdx)
