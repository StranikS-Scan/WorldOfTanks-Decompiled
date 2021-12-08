# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ammunition_panel.py
from adisp import process
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from constants import ROLE_TYPE
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.customization.shared import getEditableStylesExtraNotificationCounter, getItemTypesAvailableForVehicle
from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta
from gui.impl.new_year.new_year_helper import BONUS_ICONS
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters.icons import getRoleIcon
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.items_actions.actions import VehicleRepairAction
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBootcampController, IUISpamController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.new_year import INewYearController
from gui.customization.shared import isVehicleCanBeCustomized
from new_year.ny_constants import SyncDataKeys, PERCENT
from ny_common.settings import NY_CONFIG_NAME, NYVehBranchConsts

class AmmunitionPanel(AmmunitionPanelMeta, IGlobalListener):
    __slots__ = ('__hangarMessage',)
    __bootcampCtrl = dependency.descriptor(IBootcampController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __service = dependency.descriptor(ICustomizationService)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __uiSpamController = dependency.descriptor(IUISpamController)
    _nyController = dependency.descriptor(INewYearController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _keysForUpdate = (SyncDataKeys.VEHICLE_BRANCH, SyncDataKeys.VEHICLE_BONUS_CHOICES)

    def __init__(self):
        super(AmmunitionPanel, self).__init__()
        self.__hangarMessage = None
        g_currentVehicle.onChanged += self.__updateTankName
        return

    def update(self):
        self._update()

    @process
    def showRepairDialog(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            yield VehicleRepairAction(vehicle).doAction()

    def showCustomization(self):
        self.__service.showCustomization()

    def toRentContinue(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            canBuyOrRent, _ = vehicle.mayObtainForMoney(self.__itemsCache.items.stats.money)
            if vehicle.isRentable and vehicle.rentalIsOver and canBuyOrRent:
                shared_events.showVehicleBuyDialog(vehicle)

    def showChangeNation(self):
        if g_currentVehicle.isPresent() and g_currentVehicle.item.hasNationGroup:
            ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_NATION, g_currentVehicle.item.intCD)

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentVehicle.item.descriptor)
        return

    def onNYBonusPanelClicked(self):
        shared_events.showNewYearVehiclesView()

    @staticmethod
    def _getVehicleIcon(vehicleType):
        vehTypeStr = vehicleType.replace('-', '_') + '_widget'
        backPortImage = backport.image(R.images.gui.maps.icons.newYear.vehicles.icons.dyn(vehTypeStr)())
        return "<img src='{0}' vspace='-3'/>".format(backPortImage.replace('../', 'img://gui/'))

    def _populate(self):
        super(AmmunitionPanel, self)._populate()
        self.startGlobalListening()
        g_clientUpdateManager.addMoneyCallback(self.__moneyUpdateCallback)
        g_clientUpdateManager.addCallbacks({'inventory': self.__inventoryUpdateCallBack})
        self._nyController.onDataUpdated += self.__onNewYearDataUpdated
        self._nyController.onStateChanged += self.__onNewYearStateUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsUpdate

    def _dispose(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__hangarMessage = None
        self._nyController.onDataUpdated -= self.__onNewYearDataUpdated
        self._nyController.onStateChanged -= self.__onNewYearStateUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsUpdate
        g_currentVehicle.onChanged -= self.__updateTankName
        super(AmmunitionPanel, self)._dispose()
        return

    def _update(self, onlyMoneyUpdate=False):
        if g_currentVehicle.isPresent():
            hangarMessage = g_currentVehicle.getHangarMessage()
            if onlyMoneyUpdate and self.__hangarMessage == hangarMessage:
                return
            vehicle = g_currentVehicle.item
            self.__hangarMessage = hangarMessage
            statusId, msg, msgLvl = hangarMessage
            rentAvailable = False
            if statusId in (Vehicle.VEHICLE_STATE.RENTAL_IS_OVER, Vehicle.VEHICLE_STATE.RENTABLE_AGAIN):
                canBuyOrRent, _ = vehicle.mayObtainForMoney(self.__itemsCache.items.stats.money)
                rentAvailable = vehicle.isRentable and canBuyOrRent
            if msgLvl == Vehicle.VEHICLE_STATE_LEVEL.RENTABLE:
                msgLvl = Vehicle.VEHICLE_STATE_LEVEL.INFO
            statusOverrideRes = R.strings.ranked_battles.currentVehicleStatus.dyn(statusId)
            if statusOverrideRes:
                msg = backport.text(statusOverrideRes())
            msgString = ''
            if statusId != Vehicle.VEHICLE_STATE.UNDAMAGED:
                msgString = makeHtmlString('html_templates:vehicleStatus', msgLvl, {'message': msg})
            self.__applyCustomizationNewCounter(vehicle)
            self.__updateDevices(vehicle)
            nySlot, isNewYearVehicle = None, self.__isNewYearSupportedPrbActive()
            if isNewYearVehicle:
                nySlot = self._nyController.getVehicleBranch().getSlotForVehicle(vehicle.invID)
                isNewYearVehicle = self._nyController.isVehicleBranchEnabled() and nySlot is not None
            if self._nyController.isPostEvent() and isNewYearVehicle:
                creditBonus = self._nyController.getActiveSettingBonusValue()
            else:
                creditBonus = 0
            nyCreditBonus = ''
            shouldShowCreditsBonus = creditBonus > 0
            if shouldShowCreditsBonus:
                nyCreditBonus = backport.text(R.strings.ny.totalBonusWidget.pbBonus(), value=100 * creditBonus)
            if isNewYearVehicle:
                bonusType, bonusValue = nySlot.getSlotBonus()
                nyBonusValue = backport.text(R.strings.ny.vehiclesView.bonusFormat(), bonus=int(bonusValue * PERCENT))
                nyBonusIcon = backport.image(BONUS_ICONS[bonusType])
                nyTooltip = makeTooltip(header=backport.text(R.strings.tooltips.tankCarusel.newYearSlot.header()), body=backport.text(R.strings.tooltips.tankCarusel.newYearSlot.body()))
            else:
                nyBonusValue = ''
                nyBonusIcon = ''
                nyTooltip = ''
            self.as_updateVehicleStatusS({'message': msgString,
             'rentAvailable': rentAvailable,
             'isElite': vehicle.isElite,
             'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
             'vehicleLevel': '{}'.format(int2roman(vehicle.level)),
             'vehicleName': '{}'.format(vehicle.shortUserName),
             'roleId': vehicle.role,
             'roleMessage': self.__getRoleMessage(),
             'vehicleCD': vehicle.intCD,
             'isNYVehicle': isNewYearVehicle,
             'nyBonusIcon': nyBonusIcon,
             'nyBonusValue': nyBonusValue,
             'nyTooltip': nyTooltip,
             'isCreditsBonusVisible': shouldShowCreditsBonus,
             'creditsAmount': nyCreditBonus})
        return

    @staticmethod
    def __getRoleMessage():
        msg = ''
        hasRole = g_currentVehicle.item.role != ROLE_TYPE.NOT_DEFINED
        if hasRole:
            roleLabel = g_currentVehicle.item.roleLabel
            msg = text_styles.concatStylesToSingleLine(getRoleIcon(roleLabel), ' ', backport.text(R.strings.menu.roleExp.roleName.dyn(roleLabel)(), groupName=backport.text(R.strings.menu.roleExp.roleGroupName.dyn(roleLabel)())))
        return makeHtmlString('html_templates:vehicleStatus', Vehicle.VEHICLE_STATE_LEVEL.ROLE, {'message': msg}) if hasRole else ''

    def __isNewYearSupportedPrbActive(self):
        return self.prbEntity and not bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANKED)

    def __inventoryUpdateCallBack(self, *args):
        self.update()

    def __updateTankName(self):
        self.update()

    def __applyCustomizationNewCounter(self, vehicle):
        if vehicle.isCustomizationEnabled() and not self.__bootcampCtrl.isInBootcamp():
            availableItemTypes = getItemTypesAvailableForVehicle()
            counter = vehicle.getC11nItemsNoveltyCounter(self.__itemsCache.items, itemTypes=availableItemTypes)
            serverSettings = self.__settingsCore.serverSettings
            progressiveItemsViewVisited = serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_VIEW_HINT)
            if not progressiveItemsViewVisited and self.__uiSpamController.shouldBeHidden(OnceOnlyHints.C11N_PROGRESSION_VIEW_HINT):
                progressiveItemsViewVisited = True
                serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.C11N_PROGRESSION_VIEW_HINT: True,
                 OnceOnlyHints.C11N_EDITABLE_STYLES_HINT: True,
                 OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLES_HINT: True})
            if not progressiveItemsViewVisited and isVehicleCanBeCustomized(vehicle, GUI_ITEM_TYPE.PROJECTION_DECAL):
                counter += 1
            counter += getEditableStylesExtraNotificationCounter()
        else:
            counter = 0
        self.as_setCustomizationBtnCounterS(counter)

    def __moneyUpdateCallback(self, *_):
        self._update(onlyMoneyUpdate=True)

    def __updateDevices(self, vehicle):
        stateWarning = False
        if g_currentVehicle.isPresent():
            stateWarning = vehicle.isBroken
        self.as_setWarningStateS(stateWarning)

    def __onNewYearDataUpdated(self, keys):
        if any((key in keys for key in self._keysForUpdate)):
            self._update()

    def __onNewYearStateUpdated(self):
        self._update()

    def __onServerSettingsUpdate(self, diff):
        if NY_CONFIG_NAME in diff and NYVehBranchConsts.CONFIG_NAME in diff[NY_CONFIG_NAME]:
            self._update()
