# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tankman_change_and_recruit_view.py
import operator
import BigWorld
import constants
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui import GUI_NATIONS, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.customization.shared import getPurchaseMoneyState, MoneyForPurchase, getPurchaseGoldForCredits
from gui.impl import backport
from gui.impl.dialogs.dialogs import showRetrainingTankmanWindowDialog
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.vehicle_item_view_model import VehicleItemViewModel
from gui.impl.gen.view_models.views.lobby.crew.drop_down_item_view_model import DropDownItemViewModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_change_and_recruit_view_model import TankmanChangeAndRecruitViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.change_tankman_skin_view import ChangeTankmanSkinView
from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog_utils import getSortedItems
from gui.impl.lobby.crew.filter import FilterState
from gui.impl.lobby.crew.filter.data_providers import CompoundDataProvider, CrewSkinsDataProvider, DocumentsDataProvider
from gui.impl.lobby.crew.tooltips.tankman_change_preview_tooltip import TankmanChangePreviewTooltip
from gui.impl.lobby.crew.utils import getDocGroupValues
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.event_dispatcher import showChangeTankmanSkinWindow, showExchangeCurrencyWindowModal
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.Tankman import NO_TANKMAN
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, getIconResourceName, getNationLessName
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.items_actions import factory
from gui.shared.gui_items.processors.tankman import TankmanTokenRecruit, TankmanUnload, TankmanEquip
from gui.shared.money import Money, Currency
from gui.shared.utils.functions import replaceHyphenToUnderscore, capitalizeText
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils import decorators
from gui.shop import showBuyGoldForCrew
from helpers import dependency, i18n
from items import tankmen, vehicles
from items.components.skills_constants import ORDERED_ROLES
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from tutorial.control.game_vars import getVehicleByIntCD
from th_async import th_async
from nations import INDICES, MAP
_INVALID_IDX = -1
_FIRST_ELEMENT = 0
_EMPTY_VALUE = ''
_RETRAINING_TYPES = ('free', 'silver', 'academy')

class TankmanChangeAndRecruitView(ViewImpl):
    __slots__ = ('__tankmanInvID', '__tankman', '__isRecruit', '__selectedVehType', '__currentVehicle', '__nativeVehicle', '__keepInVeh', '__firstNamesList', '__lastNamesList', '__firstNameIdx', '__lastNameIdx', '__filterState', '__dataProviders', '__retrainKey', '__isSpecialtyChanged', '__retrain', '__selectedIcon', '__selectedIconID', '__selectedSkinID', '__recruitData', '__slotID', '__predefinedNations', '__predefinedRoles', '__predefinedVehicle', '__predefinedVehicleType', '__selectedNationID', '__isFemale', '__initialVehicle', '__selectedSpecialty', '__predefinedData', '__predefinedRole', '__selectedNationName', '__stats')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, tankmanInvID, isRecruit, slotToUnpack, vehicle, recruitData=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = TankmanChangeAndRecruitViewModel()
        self.__tankmanInvID = tankmanInvID
        self.__isRecruit = isRecruit
        self.__recruitData = recruitData
        self.__currentVehicle = vehicle
        self.__initialVehicle = None
        self.__tankman = None
        self.__nativeVehicle = None
        self.__selectedVehType = None
        self.__selectedNationID = None
        self.__selectedNationName = None
        self.__selectedSpecialty = None
        self.__retrainKey = None
        self.__retrain = None
        self.__isFemale = None
        self.__selectedIcon = None
        self.__selectedIconID = None
        self.__selectedSkinID = None
        self.__predefinedNations = None
        self.__predefinedRoles = None
        self.__predefinedVehicle = None
        self.__predefinedVehicleType = None
        self.__predefinedData = False
        self.__predefinedRole = None
        self.__firstNamesList = []
        self.__lastNamesList = []
        self.__firstNameIdx = 0
        self.__lastNameIdx = 0
        self.__keepInVeh = False
        self.__isSpecialtyChanged = False
        self.__slotID = slotToUnpack
        self.__stats = self.itemsCache.items.stats
        self.__filterState = FilterState({FilterState.GROUPS.PERSONALDATATYPE.value: ['suitableSkin', 'document']})
        self.__dataProviders = CompoundDataProvider(skins=CrewSkinsDataProvider(self.__filterState, self.tankman), documents=DocumentsDataProvider(self.__filterState, self.tankman))
        super(TankmanChangeAndRecruitView, self).__init__(settings)
        return

    @property
    def tankman(self):
        if self.__tankman is None and self.__tankmanInvID:
            self.__tankman = self.itemsCache.items.getTankman(self.__tankmanInvID)
        return self.__tankman

    @property
    def targetVehicle(self):
        return self.vehicle or self.nativeVehicle

    @property
    def vehicle(self):
        if self.__currentVehicle is None and self.tankman and self.tankman.vehicleDescr:
            self.__currentVehicle = self.itemsCache.items.getItemByCD(self.tankman.vehicleDescr.type.compactDescr)
        return self.__currentVehicle

    @property
    def initialVehicle(self):
        if self.__initialVehicle is None and self.tankman and self.tankman.vehicleDescr:
            self.__initialVehicle = self.itemsCache.items.getItemByCD(self.tankman.vehicleDescr.type.compactDescr)
        return self.__initialVehicle

    @property
    def nativeVehicle(self):
        if self.__nativeVehicle is None and self.tankman.vehicleNativeDescr:
            self.__nativeVehicle = self.itemsCache.items.getItemByCD(self.tankman.vehicleNativeDescr.type.compactDescr)
        return self.__nativeVehicle

    def __getTotalGold(self, vm):
        return vm.getSpecialtyGold() + vm.getRetrainingGold()

    @property
    def viewModel(self):
        return super(TankmanChangeAndRecruitView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return TankmanChangePreviewTooltip(credits=self.viewModel.getCredits(), retrainingGold=self.viewModel.getRetrainingGold(), specialityGold=self.viewModel.getSpecialtyGold()) if event.contentID == R.views.lobby.crew.tooltips.TankmanChangePreviewTooltip() else None

    def _onLoading(self, *args, **kwargs):
        super(TankmanChangeAndRecruitView, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyChange)
        self.__dataProviders.subscribe()
        with self.viewModel.transaction() as vm:
            vm.setIsRecruit(self.__isRecruit)
            if not self.__isRecruit:
                self.setChildView(R.views.dialogs.sub_views.topRight.MoneyBalance(), MoneyBalance())
                self.__dataProviders.update()
                self.__selectedNationID = self.tankman.nationID
                self.__selectedNationName = MAP.get(self.tankman.nationID)
                self.__selectedSpecialty = self.tankman.role
                self.__isFemale = self.tankman.isFemale
                if self.tankman.isInSkin:
                    iconID = self.itemsCache.items.getCrewSkin(self.tankman.skinID).getIconID()
                    icon = R.images.gui.maps.icons.tankmen.icons.big.crewSkins.dyn(iconID)()
                    self.__selectedSkinID = self.tankman.skinID
                else:
                    icon = R.images.gui.maps.icons.tankmen.icons.big.dyn(Tankman.getDynIconName(self.tankman.icon))()
                vm.setInitialIcon(icon)
                vm.setIsPhotoLocked(self.tankman.descriptor.getRestrictions().isPassportReplacementForbidden())
                for tankman in (vm.currentTankman, vm.futureTankman):
                    tankman.setIsFemale(self.__isFemale)
                    tankman.setNationName(self.__selectedNationName)
                    tankman.setSpecialty(self.tankman.role)
                    tankman.setIcon(icon)
                    tankman.setVehicleID(str(self.nativeVehicle.intCD))
                    tankman.setVehicleName(self.nativeVehicle.descriptor.type.shortUserString)
                    tankman.setVehicleLevel(self.nativeVehicle.level)
                    tankman.setVehicleIcon(R.images.gui.maps.shop.vehicles.c_360x270.dyn(getIconResourceName(getNationLessName(self.nativeVehicle.name)))())
                    tankman.setIsEliteVehicle(self.nativeVehicle.isPremium)

                self.__fillNames(vm, self.tankman.isInSkin)
                self.__fillDataFields(vm)
            else:
                vm.setIsPhotoLocked(True)
                vm.futureTankman.setIcon(R.images.gui.maps.icons.tankmen.icons.big.dyn(Tankman.getDynIconName(self.__recruitData.getSmallIcon()))())
                namesData = (self.__recruitData.getFirstName(), self.__recruitData.getLastName())
                if self.__slotID != _INVALID_IDX:
                    self.__fillPredefinedRecruitData(vm)
                    self.__predefinedData = True
                else:
                    self.__predefinedNations = self.__recruitData.getNations()
                    self.__predefinedRoles = self.__recruitData.getRoles()
                    if len(self.__predefinedNations) == 1:
                        self.__selectedNationID = _FIRST_ELEMENT
                        self.__selectedNationName = first(self.__predefinedNations)
                        self.__fillVehTypes(vm)
                        vm.futureTankman.setVehType(str(_INVALID_IDX))
                        vm.futureTankman.setNationID(first(self.__predefinedNations))
                    else:
                        vm.futureTankman.setNationID(str(_INVALID_IDX))
                    self.__predefinedRole = len(self.__predefinedRoles) == 1
                    if self.__predefinedRole:
                        self.__fillSpecialties(vm)
                        self.__selectedSpecialty = first(self.__predefinedRoles)
                        vm.futureTankman.setSpecialty(self.__selectedSpecialty)
                self.__fillNations(vm)
                self.__fillNames(vm, isSkin=True, updateFutureTankman=True, namesData=namesData)

    def _finalize(self):
        super(TankmanChangeAndRecruitView, self)._finalize()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__dataProviders.unsubscribe()
        self.__dataProviders.clear()
        self.__filterState = None
        self.__dataProviders = None
        return

    def _getEvents(self):
        return ((self.viewModel.onViewClose, self.__onViewClose),
         (self.viewModel.onVehTypeChange, self.__onVehTypeChange),
         (self.viewModel.onTankmanPhotoChange, self.__onTankmanPhotoChange),
         (self.viewModel.onRetrainingChange, self.__onRetrainingChange),
         (self.viewModel.onSpecialtyChange, self.__onSpecialtyChange),
         (self.viewModel.onSetInVehChange, self.__onSetInVehChange),
         (self.viewModel.onNameChange, self.__onNameChange),
         (self.viewModel.onSurnameChange, self.__onSurnameChange),
         (self.viewModel.onTankmanUpdate, self.__onTankmanUpdate),
         (self.viewModel.onVehChange, self.__onVehChange),
         (self.viewModel.onNationChange, self.__onNationChange),
         (self.viewModel.onRecruit, self.__onRecruit),
         (ChangeTankmanSkinView.onTankmanIconChanged, self.__onTankmanIconChanged))

    def __fillPredefinedRecruitData(self, vm):
        self.__selectedVehType = self.vehicle.type
        self.__selectedSpecialty = self.vehicle.descriptor.type.crewRoles[self.__slotID][_FIRST_ELEMENT]
        nation = self.vehicle.nationName
        self.__predefinedVehicle = ((self.vehicle.intCD, self.vehicle),)
        self.__predefinedVehicleType = (self.__selectedVehType,)
        self.__predefinedNations = (nation,)
        self.__predefinedRoles = (self.__selectedSpecialty,)
        vm.futureTankman.setNationID(nation)
        vm.futureTankman.setVehicleID(str(self.vehicle.intCD))
        vm.futureTankman.setVehType(self.__selectedVehType)
        vm.futureTankman.setSpecialty(self.__selectedSpecialty)
        self.__selectedNationID = self.vehicle.nationID
        self.__isFemale = self.__recruitData.isFemale()
        self.__fillDataFields(vm)

    def __fillDataFields(self, vm):
        self.__fillVehTypes(vm)
        self.__fillVehicles(vm)
        self.__fillSpecialties(vm)

    def __fillNames(self, vm, isSkin, updateFutureTankman=False, namesData=None):
        if self.tankman:
            isPassportReplacementForbidden = self.tankman.descriptor.getRestrictions().isPassportReplacementForbidden()
        else:
            isPassportReplacementForbidden = True
        firstName, lastName = namesData if namesData is not None else self.__getTankmanName(isSkin)
        if isSkin or isPassportReplacementForbidden:
            vm.setIsNameCanBeChanged(False)
            self.__firstNamesList = ((_EMPTY_VALUE, _EMPTY_VALUE, firstName),)
            self.__lastNamesList = ((_EMPTY_VALUE, _EMPTY_VALUE, lastName),)
        else:
            vm.setIsNameCanBeChanged(True)
            config = tankmen.getNationConfig(self.__selectedNationID)
            self.__firstNamesList = getDocGroupValues(self.tankman, config, operator.attrgetter('firstNamesList'), config.getFirstName)
            self.__lastNamesList = getDocGroupValues(self.tankman, config, operator.attrgetter('lastNamesList'), config.getLastName)
        self.__firstNameIdx = self.__fillItemsList(vm.getNames(), self.__firstNamesList, firstName)
        self.__lastNameIdx = self.__fillItemsList(vm.getSurnames(), self.__lastNamesList, lastName)
        tankmenList = (vm.futureTankman,) if updateFutureTankman else (vm.futureTankman, vm.currentTankman)
        for tankman in tankmenList:
            tankman.setNameID(self.__firstNameIdx)
            tankman.setSurnameID(self.__lastNameIdx)
            tankman.setNameText(firstName)
            tankman.setSurnameText(lastName)

        return

    def __fillItemsList(self, modelList, itemList, selectedItemName):
        modelList.clear()
        selectedIdx = _EMPTY_VALUE
        for idx, itemData in enumerate(itemList):
            _, _, nameStr = itemData
            if selectedItemName == nameStr:
                selectedIdx = str(idx)
            self.__setDropDownModel(modelList, str(idx), nameStr)

        modelList.invalidate()
        return selectedIdx

    def __fillVehTypes(self, vm):
        vehTypes = vm.getVehTypes()
        vehTypes.clear()
        vehTypeList = getSortedItems(self.__getVehTypeList(), VEHICLE_TYPES_ORDER)
        for name in vehTypeList:
            self.__setDropDownModel(vehTypes, name, capitalizeText(backport.text(R.strings.menu.classes.dyn(replaceHyphenToUnderscore(name))())))

        if self.tankman:
            curVehType = self.tankman.vehicleNativeType
            self.__selectedVehType = curVehType if curVehType in vehTypeList else _EMPTY_VALUE
            for tankman in (vm.currentTankman, vm.futureTankman):
                tankman.setVehType(self.__selectedVehType)

        vehTypes.invalidate()

    def __fillVehicles(self, vm):
        vehs = vm.getVehicles()
        vehs.clear()
        nationVehicleList = self.__getVehicleList()
        for intCD, vehicle in nationVehicleList:
            if len(nationVehicleList) == 1:
                self.__currentVehicle = getVehicleByIntCD(intCD)
                vm.futureTankman.setVehicleID(str(intCD))
                self.__fillSpecialties(vm)
            model = VehicleItemViewModel()
            model.setId(intCD)
            model.setName(vehicle.descriptor.type.shortUserString)
            model.setType(replaceHyphenToUnderscore(vehicle.type))
            model.setIsElite(vehicle.isPremium)
            model.setIsIGR(vehicle.isPremiumIGR)
            vehs.addViewModel(model)

        vehs.invalidate()

    def __fillSpecialties(self, vm):
        specializations = vm.getSpecialties()
        specializations.clear()
        rolesList = getSortedItems(self.__getSpecialtiesList(), ORDERED_ROLES)
        if self.__selectedSpecialty not in rolesList:
            self.__selectedSpecialty = None
            vm.futureTankman.setSpecialty(str(_INVALID_IDX))
            vm.setSpecialtyGold(0)
            self.__setMoneyState(vm)
        for name in rolesList:
            if self.__isFemale:
                value = backport.text(R.strings.item_types.tankman.roles.female.dyn(name)())
            else:
                value = backport.text(R.strings.item_types.tankman.roles.dyn(name)())
            self.__setDropDownModel(specializations, name, value)

        specializations.invalidate()
        return

    def __getVehicleList(self):
        vehiclesCriteria = self.__getVehicleTypeCriteria(self.__selectedNationID, self.__selectedVehType)
        vehiclesByNation = self.itemsCache.items.getVehicles(vehiclesCriteria).items()
        filteredVehicles = set(vehiclesByNation)
        if self.__predefinedVehicle:
            filteredVehicles = filteredVehicles.intersection(set(self.__predefinedVehicle))
        return sorted(filteredVehicles, key=lambda x: (x[1].level, x[1].shortUserName))

    def __getVehTypeList(self):
        nationVehTypes = self.itemsCache.items.getVehicles(self.__getClassesCriteria(self.__selectedNationID)).values()
        filteredVehTypes = set((v.type for v in nationVehTypes))
        if self.__predefinedVehicleType:
            filteredVehTypes = filteredVehTypes.intersection(set(self.__predefinedVehicleType))
        return list(filteredVehTypes)

    def __getSpecialtiesList(self):
        filteredSpecialties = set()
        if not self.__predefinedRole:
            if self.tankman and not self.tankman.isInTank and self.vehicle is None or self.__currentVehicle is None:
                vehCompDescr = self.nativeVehicle.compactDescr
            else:
                vehCompDescr = self.vehicle.compactDescr
            _, _, vehTypeID = vehicles.parseIntCompactDescr(vehCompDescr)
            modulesAll = self.itemsCache.items.getVehicles(self.__getSpecialtiesCriteria(self.__selectedNationID, self.__selectedVehType, vehTypeID)).values()
            filteredSpecialties = set((r[_FIRST_ELEMENT] for v in modulesAll for r in v.descriptor.type.crewRoles))
        if self.__predefinedRoles:
            filteredSpecialties = filteredSpecialties.intersection(set(self.__predefinedRoles))
            if not filteredSpecialties:
                return list(self.__predefinedRoles)
        return list(filteredSpecialties)

    def __fillNations(self, vm):
        nations = vm.getNations()
        nations.clear()
        nationsList = getSortedItems(self.__getNationsList(), GUI_NATIONS)
        for name in nationsList:
            self.__setDropDownModel(nations, name, backport.text(R.strings.nations.dyn(name)()))

        nations.invalidate()

    def __getNationsList(self):
        filteredNations = set(GUI_NATIONS)
        if self.__predefinedNations:
            self.__selectedNationID = INDICES.get(self.__predefinedNations[_FIRST_ELEMENT])
            filteredNations = filteredNations.intersection(set(self.__predefinedNations))
        else:
            self.__selectedNationID = _FIRST_ELEMENT
        return list(filteredNations)

    def __clearSpecialties(self, vm):
        self.__selectedSpecialty = None
        specialties = vm.getSpecialties()
        vm.futureTankman.setSpecialty(str(_INVALID_IDX))
        specialties.clear()
        specialties.invalidate()
        return

    @staticmethod
    def __setDropDownModel(modelList, labelId, label):
        model = DropDownItemViewModel()
        model.setId(labelId)
        model.setValue(label)
        modelList.addViewModel(model)

    def __onMoneyChange(self, *_):
        with self.viewModel.transaction() as vm:
            self.__setMoneyState(vm)

    def __setMoneyState(self, vm):
        vm.commit()
        gold = vm.getRetrainingGold() + vm.getSpecialtyGold()
        vm.setIsEnoughCredits(self.__stats.money.getSignValue(Currency.CREDITS) - vm.getCredits() >= 0)
        vm.setIsEnoughGold(self.__stats.money.getSignValue(Currency.GOLD) - gold >= 0)

    def __onViewClose(self):
        self.destroyWindow()

    @args2params(str)
    def __onVehChange(self, vehicleID):
        self.__currentVehicle = getVehicleByIntCD(int(vehicleID))
        with self.viewModel.transaction() as vm:
            self.__fillSpecialties(vm)
            vm.futureTankman.setVehicleName(self.vehicle.descriptor.type.shortUserString)
            vm.futureTankman.setVehicleID(str(self.vehicle.intCD))
            vm.futureTankman.setVehicleLevel(self.vehicle.level)
            vm.futureTankman.setVehicleIcon(R.images.gui.maps.shop.vehicles.c_360x270.dyn(getIconResourceName(getNationLessName(self.vehicle.name)))())
            vm.futureTankman.setIsEliteVehicle(self.vehicle.isPremium)
            self.__keepInVeh = False
            vm.setIsShowCheckBox(self.__tmanCanTransferToVehicle() if self.__selectedSpecialty else self.__keepInVeh)
            vm.setIsCheckBoxSelected(self.__keepInVeh)
            if not self.__retrain and not self.__isSpecialtyChanged:
                self.setInitialRetraining(vm)
            if self.initialVehicle == self.vehicle:
                self.setBlockedRetraining(vm, _EMPTY_VALUE)
                self.__setMoneyState(vm)

    @args2params(str)
    def __onVehTypeChange(self, vehType):
        if vehType != self.__selectedVehType:
            with self.viewModel.transaction() as vm:
                if not self.__predefinedRole:
                    self.__clearSpecialties(vm)
                vm.setIsShowCheckBox(False)
                self.__selectedVehType = vehType
                vm.futureTankman.setVehType(self.__selectedVehType)
                vm.futureTankman.setVehicleID(str(_INVALID_IDX))
                self.__fillVehicles(vm)

    def __onTankmanPhotoChange(self):
        showChangeTankmanSkinWindow(tankmanID=self.__tankmanInvID, selectedIcon=self.__selectedIcon, selectedNation=self.__selectedNationName, selectedIconID=self.__selectedIconID, selectedSkinID=self.__selectedSkinID, parent=self.getWindow())

    def __getTankmanName(self, isSkin):
        if isSkin and self.__selectedSkinID:
            skin = self.itemsCache.items.getCrewSkin(self.__selectedSkinID)
            firstName = i18n.makeString(skin.getFirstName())
            lastName = i18n.makeString(skin.getLastName())
        else:
            firstName = self.tankman.firstUserName
            lastName = self.tankman.lastUserName
        return (firstName, lastName)

    def __onTankmanIconChanged(self, icon, iconID, isSkin):
        with self.viewModel.transaction() as vm:
            if isSkin:
                skin = self.itemsCache.items.getCrewSkin(iconID)
                self.__selectedSkinID = iconID
                image = R.images.gui.maps.icons.tankmen.icons.big.crewSkins.dyn(skin.getIconID())()
                self.__fillNames(vm, isSkin, True)
                vm.setIsNameCanBeChanged(False)
            else:
                image = R.images.gui.maps.icons.tankmen.icons.big.dyn(Tankman.getDynIconName(icon))()
                self.__selectedIcon = icon
                self.__selectedIconID = iconID
                if self.__selectedSkinID:
                    self.__fillNames(vm, isSkin, True)
                    self.__selectedSkinID = None
            vm.futureTankman.setIcon(image)
        return

    @th_async
    def __onRetrainingChange(self):
        result = yield showRetrainingTankmanWindowDialog()
        if result.result[1] is not None and result.result[0]:
            itemPrice, self.__retrainKey = result.result[1]
            with self.viewModel.transaction() as vm:
                self.__retrain = _RETRAINING_TYPES[self.__retrainKey]
                vm.setRetraining(self.__retrain)
                vm.setCredits(itemPrice.price.credits)
                vm.setRetrainingGold(itemPrice.price.gold)
                self.__setMoneyState(vm)
        return

    @args2params(str)
    def __onNationChange(self, nationID):
        self.__selectedNationName = nationID
        self.__selectedNationID = INDICES.get(self.__selectedNationName)
        with self.viewModel.transaction() as vm:
            vehicleList = vm.getVehicles()
            vm.futureTankman.setNationID(self.__selectedNationName)
            vm.futureTankman.setVehType(str(_INVALID_IDX))
            vm.futureTankman.setVehicleID(str(_INVALID_IDX))
            self.__selectedVehType = _EMPTY_VALUE
            vm.setIsShowCheckBox(False)
            if not self.__predefinedRole:
                self.__clearSpecialties(vm)
            vehicleList.clear()
            vehicleList.invalidate()
            self.__fillVehTypes(vm)

    @args2params(str)
    def __onSpecialtyChange(self, specialty):
        with self.viewModel.transaction() as vm:
            if self.tankman is None:
                self.__isSpecialtyChanged = self.__selectedSpecialty != specialty
            else:
                self.__isSpecialtyChanged = self.tankman.role != specialty
            if self.__isSpecialtyChanged:
                vm.setSpecialtyGold(self.itemsCache.items.shop.changeRoleCost)
                self.__isSpecialtyChanged = True
                self.setBlockedRetraining(vm, _RETRAINING_TYPES[-1])
            else:
                self.setInitialRetraining(vm)
            self.__selectedSpecialty = specialty
            vm.futureTankman.setSpecialty(specialty)
            vm.setIsShowCheckBox(self.__tmanCanTransferToVehicle())
            self.__setMoneyState(vm)
        return

    def setInitialRetraining(self, vm):
        self.__retrain = first(_RETRAINING_TYPES)
        self.__retrainKey = _RETRAINING_TYPES.index(self.__retrain)
        vm.setRetraining(self.__retrain)
        vm.setCanChangeRetraining(True)

    def setBlockedRetraining(self, vm, value):
        self.__retrain = None
        self.__retrainKey = None
        vm.setRetraining(value)
        vm.setRetrainingGold(0)
        vm.setCredits(0)
        vm.setCanChangeRetraining(False)
        return

    @args2params(bool)
    def __onSetInVehChange(self, isKeepInVeh):
        self.__keepInVeh = isKeepInVeh
        with self.viewModel.transaction() as vm:
            vm.setIsCheckBoxSelected(self.__keepInVeh)

    @args2params(str)
    def __onNameChange(self, nameID):
        with self.viewModel.transaction() as vm:
            vm.futureTankman.setNameID(nameID)
            _, _, nameStr = self.__firstNamesList[int(nameID)]
            self.__firstNameIdx = int(nameID)
            vm.futureTankman.setNameText(nameStr)
            vm.futureTankman.setNameID(nameID)

    @args2params(str)
    def __onSurnameChange(self, surnameID):
        with self.viewModel.transaction() as vm:
            vm.futureTankman.setSurnameID(surnameID)
            _, _, surnameStr = self.__lastNamesList[int(surnameID)]
            self.__lastNameIdx = int(surnameID)
            vm.futureTankman.setSurnameText(surnameStr)
            vm.futureTankman.setSurnameID(surnameID)

    def __getSpecialtiesCriteria(self, nationID, vclass, typeID):
        return self.__getVehicleTypeCriteria(nationID, vclass) | REQ_CRITERIA.INNATION_IDS([typeID])

    def __getClassesCriteria(self, nationID):
        if self.__isRecruit:
            criteria = self.__getNationsCriteria() | REQ_CRITERIA.NATIONS([nationID])
            maxResearchedLevel = self.itemsCache.items.stats.getMaxResearchedLevel(nationID)
            criteria |= ~(REQ_CRITERIA.COLLECTIBLE | ~REQ_CRITERIA.VEHICLE.LEVELS(range(1, maxResearchedLevel + 1)) | ~REQ_CRITERIA.INVENTORY)
            criteria |= ~(REQ_CRITERIA.SECRET | ~REQ_CRITERIA.INVENTORY_OR_UNLOCKED)
            if self.__predefinedRole and self.__selectedVehType:
                criteria |= REQ_CRITERIA.VEHICLE.HAS_ROLE(self.__selectedSpecialty)
        else:
            criteria = REQ_CRITERIA.NATIONS([nationID])
            criteria |= ~REQ_CRITERIA.SECRET
        return criteria

    def __getNationsCriteria(self):
        rqc = REQ_CRITERIA
        criteria = ~(~rqc.UNLOCKED | ~rqc.COLLECTIBLE)
        criteria |= ~rqc.VEHICLE.OBSERVER
        criteria |= ~rqc.VEHICLE.BATTLE_ROYALE
        criteria |= ~rqc.VEHICLE.MAPS_TRAINING
        criteria |= ~rqc.VEHICLE.EVENT_BATTLE
        criteria |= ~rqc.VEHICLE.MODE_HIDDEN
        return criteria

    def __getVehicleTypeCriteria(self, nationID, vclass):
        criteria = self.__getClassesCriteria(nationID) | REQ_CRITERIA.VEHICLE.CLASSES([vclass])
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        if not constants.IS_IGR_ENABLED:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        if constants.IS_DEVELOPMENT:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_BOT
        return criteria

    def __onTankmanUpdate(self):
        with self.viewModel.transaction() as vm:
            currentTankman = vm.currentTankman
            futureTankman = vm.futureTankman
            defCost = self.itemsCache.items.shop.defaults.tankmanCost[self.__retrainKey] if self.__retrainKey else {}
            specialtyChangeCost = self.itemsCache.items.shop.changeRoleCost if self.__isSpecialtyChanged else 0
            itemPrice = ItemPrice(price=Money(credits=vm.getCredits(), gold=self.__getTotalGold(vm)), defPrice=Money(credits=defCost.get(Currency.CREDITS, 0), gold=defCost.get(Currency.GOLD, 0) + specialtyChangeCost))
            purchaseMoneyState = getPurchaseMoneyState(itemPrice.price)
            if purchaseMoneyState is MoneyForPurchase.NOT_ENOUGH:
                showBuyGoldForCrew(itemPrice.price.gold)
                return False
            if purchaseMoneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
                purchaseGold = getPurchaseGoldForCredits(itemPrice.price)
                showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
                return False
            doActions = []
            self.__validatePassportAction(doActions, currentTankman, futureTankman)
            self.__validateSpecialty(doActions, currentTankman, futureTankman)
            self.__validateEquip(doActions)
            self.__validateUnEquip(doActions)
            self.__validateRetraining(doActions)
            groupSize = len(doActions)
            groupID = int(BigWorld.serverTime())
            while doActions:
                factory.doAction(*(doActions.pop(0) + (groupID, groupSize)))

            self.destroyWindow()

    def __onRecruit(self):
        slotTankman = self.vehicle.getTankmanIDBySlotIdx(self.__slotID) if self.vehicle else NO_TANKMAN
        if self.__predefinedData and slotTankman != NO_TANKMAN:
            self._unloadOldTankman()
        else:
            self._processRecruit()

    @decorators.adisp_process('updating')
    def _processRecruit(self):
        _, _, vehTypeID = vehicles.parseIntCompactDescr(self.vehicle.compactDescr)
        res = yield TankmanTokenRecruit(int(self.__selectedNationID), int(vehTypeID), self.__selectedSpecialty, self.__tankmanInvID, self.__recruitData).request()
        if res.userMsg:
            SystemMessages.pushMessage(res.userMsg, type=res.sysMsgType)
        if res.success:
            if self.__keepInVeh or self.__predefinedData:
                tmn = self.itemsCache.items.getTankman(res.auxData)
                self._equipTankman(tmn)
        self.destroyWindow()

    @decorators.adisp_process('equipping')
    def _equipTankman(self, newTankman):
        slotID = self.__slotID if self.__slotID != _INVALID_IDX else self.__getSlotForTmanInVeh()
        result = yield TankmanEquip(newTankman.invID, self.vehicle.invID, slotID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.adisp_process('unloading')
    def _unloadOldTankman(self):
        result = yield TankmanUnload(self.vehicle.invID, self.__slotID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self._processRecruit()

    def __getSlotForTmanInVeh(self):
        if self.vehicle and self.vehicle.isInInventory:
            for idx, roles in enumerate(self.vehicle.descriptor.type.crewRoles):
                if self.__selectedSpecialty == roles[0]:
                    slotIdx, vehTankman = self.vehicle.crew[idx]
                    if idx != slotIdx:
                        slotIdx, vehTankman = self.vehicle.crew[slotIdx]
                    if vehTankman is None:
                        return slotIdx

        return

    def __getSlotIdForCurrentVeh(self):
        for slotIdx, tman in self.initialVehicle.crew:
            if tman and tman.invID == self.tankman.invID:
                return slotIdx

        return _INVALID_IDX

    def __tmanCanTransferToVehicle(self):
        if self.vehicle and self.vehicle.isInInventory:
            for _, tankman in self.vehicle.crew:
                if tankman is not None:
                    continue
                slotIdx = self.__getSlotForTmanInVeh()
                if slotIdx is not None:
                    return True

        return False

    def __validateEquip(self, doActions):
        if self.__keepInVeh:
            doActions.append((factory.EQUIP_TANKMAN,
             self.tankman.invID,
             self.vehicle.invID,
             self.__getSlotForTmanInVeh()))

    def __validateUnEquip(self, doActions):
        if self.tankman.isInTank and self.initialVehicle != self.vehicle:
            self.__unloadTankman(doActions)

    def __unloadTankman(self, doActions):
        unloadCmd = (factory.UNLOAD_TANKMAN, self.initialVehicle.invID, self.__getSlotIdForCurrentVeh())
        if unloadCmd not in doActions:
            doActions.append(unloadCmd)

    def __validateRetraining(self, doActions):
        if self.__retrain:
            doActions.append((factory.RETRAIN_TANKMAN,
             self.tankman.invID,
             self.targetVehicle.intCD,
             self.__retrainKey))

    def __validateSpecialty(self, doActions, currentTankman, futureTankman):
        futureTankmanSpetialty = str(futureTankman.getSpecialty())
        if currentTankman.getSpecialty() != futureTankmanSpetialty:
            doActions.append((factory.CHANGE_ROLE_TANKMAN,
             self.tankman.invID,
             futureTankmanSpetialty,
             self.targetVehicle.intCD,
             self.__getSlotForTmanInVeh()))
            if self.tankman.isInTank:
                self.__unloadTankman(doActions)

    def __validatePassportAction(self, doActions, currentTankman, futureTankman):
        firstNameID = futureTankman.getNameID()
        lastNameID = futureTankman.getSurnameID()
        if currentTankman.getIcon() != futureTankman.getIcon():
            if self.tankman.isInSkin:
                doActions.append((factory.CREW_SKIN_UNEQUIP, self.__tankmanInvID))
            if self.__selectedSkinID:
                doActions.append((factory.CREW_SKIN_EQUIP, self.__tankmanInvID, self.__selectedSkinID))
                return
        if currentTankman.getNameID() != firstNameID or currentTankman.getSurnameID() != lastNameID or currentTankman.getIcon() != futureTankman.getIcon():
            firstNameGroup = lastNameGroup = iconID = iconGroup = _INVALID_IDX
            docsProvider = self.__dataProviders['documents']
            cardData = None
            for item in docsProvider.items():
                if item.icon.id == self.__selectedIconID:
                    cardData = item
                    break

            if cardData:
                iconData = cardData.icon
                iconID = iconData.id if iconData.id is not None else _INVALID_IDX
                iconGroup = iconData.group if iconData.group is not None else _INVALID_IDX
            if 0 <= int(firstNameID) < len(self.__firstNamesList):
                firstNameID, firstNameGroup, _ = self.__firstNamesList[int(firstNameID)]
            if 0 <= int(lastNameID) < len(self.__lastNamesList):
                lastNameID, lastNameGroup, _ = self.__lastNamesList[int(lastNameID)]
            doActions.append((factory.CHANGE_TANKMAN_PASSPORT,
             self.__tankmanInvID,
             firstNameID,
             firstNameGroup,
             lastNameID,
             lastNameGroup,
             iconID,
             iconGroup))
        return


class TankmanChangeAndRecruitViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None, tankmanInvID=None, isRecruit=False, slotToUnpack=_INVALID_IDX, vehicle=None, recruitData=None):
        super(TankmanChangeAndRecruitViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TankmanChangeAndRecruitView(R.views.lobby.crew.TankmanChangeAndRecruitView(), tankmanInvID=tankmanInvID, isRecruit=isRecruit, recruitData=recruitData, slotToUnpack=slotToUnpack, vehicle=vehicle), parent=parent)
