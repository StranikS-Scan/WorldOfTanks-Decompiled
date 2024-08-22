# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/tankman_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.tooltips.tankman_tooltip_modifier_model import TankmanTooltipModifierModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.tankman_tooltip_model import TankmanTooltipModel
from gui.impl.lobby.crew.crew_helpers.model_setters import setTankmanRestoreInfo
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman, BROTHERHOOD_SKILL_NAME, getTankmanSkill
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers import time_utils
from items.components.tankmen_components import SPECIAL_CREW_TAG
from items.special_crew import isWitchesCrew
from items.tankmen import getSpecialVoiceTag, tankmenGroupHasRole, getTankmenWithTag
from skeletons.gui.game_control import ISpecialSoundCtrl
from skeletons.gui.shared import IItemsCache

class TankmanTooltip(ViewImpl):
    __slots__ = ('tankmanID', 'isCalledFromCrewWidget', '__parentLayoutID')
    itemsCache = dependency.descriptor(IItemsCache)
    _specialSounds = dependency.descriptor(ISpecialSoundCtrl)
    _partialInfoViews = (R.views.lobby.crew.BarracksView(), R.views.lobby.crew.MemberChangeView(), R.views.lobby.crew.ConversionConfirmView())

    def __init__(self, tankmanID, isCalledFromCrewWidget=False, *args, **kwargs):
        self.tankmanID = tankmanID
        self.isCalledFromCrewWidget = isCalledFromCrewWidget
        settings = ViewSettings(R.views.lobby.crew.tooltips.TankmanTooltip(), args=args, kwargs=kwargs)
        settings.model = TankmanTooltipModel()
        self.__parentLayoutID = kwargs['layoutID']
        super(TankmanTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankmanTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TankmanTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        tankman = self.itemsCache.items.getTankman(self.tankmanID)
        with self.viewModel.transaction() as vm:
            vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
            nativeVehicle = self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
            vm.setRole(tankman.role)
            vm.setFullName(tankman.getFullUserNameWithSkin())
            vm.setRankUserName(tankman.rankUserName)
            vm.setIsFemale(tankman.isFemale)
            vm.setRankIcon(tankman.extensionLessIconRank)
            vm.setSkillsEfficiency(tankman.currentVehicleSkillsEfficiency)
            vm.setIsInfoAdvanced(self.__parentLayoutID not in self._partialInfoViews or self.isCalledFromCrewWidget)
            self._setVoiceoverReason(vm, tankman, vehicle)
            fillVehicleInfo(vm.nativeVehicle, nativeVehicle, True, nativeVehicle.tags)
            if tankman.isInTank:
                vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
                fillVehicleInfo(vm.currentVehicle, vehicle, True, vehicle.tags)
            if tankman.isDismissed:
                vm.setIsDismissed(True)
                dismissalLength = time_utils.getTimeDeltaTillNow(tankman.dismissedAt)
                tankmenRestoreConfig = self.itemsCache.items.shop.tankmenRestoreConfig
                vm.setSecondsLeftToRestore(tankmenRestoreConfig.billableDuration - dismissalLength)
                vm.setHasFreeRestore(dismissalLength < tankmenRestoreConfig.freeDuration)
                setTankmanRestoreInfo(vm.restoreInfo)
            self._setBonuses(vm, tankman, vehicle)

    def _setVoiceoverReason(self, vm, tankman, vehicle):
        if isWitchesCrew(tankman.descriptor):
            if not vehicle:
                vm.setVoiceoverReason(TooltipConstants.UNIQUE_VOICEOVER_WITCHES)
                return
            isAllCrewMembersWitch = all((isWitchesCrew(tman.descriptor) for _, tman in vehicle.crew))
            witchesCrew = getTankmenWithTag(tankman.descriptor.nationID, tankman.descriptor.isPremium, SPECIAL_CREW_TAG.WITCHES_CREW)
            if len(witchesCrew) != len(vehicle.crew) or not isAllCrewMembersWitch:
                vm.setVoiceoverReason(TooltipConstants.UNIQUE_VOICEOVER_WITCHES)
                return
        else:
            specialVoiceTag = getSpecialVoiceTag(tankman, self._specialSounds)
            if specialVoiceTag:
                hasCommanderRole = tankmenGroupHasRole(tankman.descriptor.nationID, tankman.descriptor.gid, tankman.descriptor.isPremium, Tankman.ROLES.COMMANDER)
                if tankman.role != Tankman.ROLES.COMMANDER and hasCommanderRole and not tankman.isLockedByVehicle():
                    vm.setVoiceoverReason(Tankman.ROLES.COMMANDER)

    def _setBonuses(self, vm, tankman, vehicle):
        finalEffVal = 0
        skill = getTankmanSkill(BROTHERHOOD_SKILL_NAME, tankman=tankman)
        brotherhoodBonus = tankman.vehicleBonuses.get('brotherhood', 0)
        finalEffVal += brotherhoodBonus
        self.__addModifier(vm.getPerks(), brotherhoodBonus, R.images.gui.maps.icons.tankmen.skills.medium.dyn(skill.extensionLessIconName)(), skill.userName)
        if not vehicle:
            return
        isCommanderInVehicle = any((tman and tman.role == Tankman.ROLES.COMMANDER for _, tman in vehicle.crew))
        if tankman.role != Tankman.ROLES.COMMANDER and isCommanderInVehicle:
            commanderBonus = tankman.vehicleBonuses.get('commander', 0)
            finalEffVal += commanderBonus
            self.__addModifier(vm.getCommanderFeatures(), commanderBonus, R.images.gui.maps.icons.tankmen.skills.medium.commander_bonus(), backport.text(R.strings.tooltips.tankman.commanderBonus.title()), backport.text(R.strings.tooltips.tankman.commanderBonus.description()))
        if vehicle.optDevices.layoutCapacity:
            criteria = REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.OPTIONALDEVICE]) | ~REQ_CRITERIA.SECRET
            optDevices = self.itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria, nationID=vehicle.nationID).values()
            archetypes = {}
            for optDevice in optDevices:
                if optDevice.descriptor.factorsContainCrewLevelIncrease():
                    artefactsBonus = 0
                    if optDevice.isInstalled(vehicle):
                        artefactsBonus = optDevice.descriptor.getFactorValue(vehicle.descriptor, 'miscAttrs/crewLevelIncrease')
                        finalEffVal += artefactsBonus
                        bnsId = optDevice.name.split('_tier')[0]
                        self.__addModifier(vm.getConsumables(), artefactsBonus, R.images.gui.maps.icons.vehParams.tooltips.bonuses.dyn(bnsId.split('_class')[0], R.invalid)(), backport.text(R.strings.artefacts.dyn(bnsId).name()))
                    archetype = archetypes.get(optDevice.descriptor.archetype)
                    isBonusInstalled = bool(artefactsBonus)
                    if archetype:
                        if isBonusInstalled:
                            archetype[0] = isBonusInstalled
                    else:
                        archetypes[optDevice.descriptor.archetype] = [isBonusInstalled, optDevice.descriptor.archetype]

            for _, archetype in archetypes.items():
                if not archetype[0]:
                    self.__addModifier(vm.getConsumables(), 0, R.images.gui.maps.icons.vehParams.tooltips.bonuses.archetypes.dyn(archetype[1])(), backport.text(R.strings.artefacts.archetype.template(), name=backport.text(R.strings.artefacts.archetype.dyn(archetype[1]).name())))

        if vehicle.consumables.layoutCapacity:
            criteria = REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.EQUIPMENT]) | ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET
            equipments = self.itemsCache.items.getItems(GUI_ITEM_TYPE.EQUIPMENT, criteria, nationID=vehicle.nationID).values()
            for equipment in equipments:
                equipmentBonus = 0
                if equipment.isStimulator:
                    if equipment.isInstalled(vehicle):
                        equipmentBonus = equipment.crewLevelIncrease
                        finalEffVal += equipmentBonus
                    self.__addModifier(vm.getConsumables(), equipmentBonus, R.images.gui.maps.icons.vehParams.tooltips.bonuses.dyn(equipment.name)(), equipment.shortUserName)

        if vehicle.battleBoosters.layoutCapacity:
            criteria = REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.BATTLE_BOOSTER]) | ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET
            boosters = self.itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_BOOSTER, criteria, nationID=vehicle.nationID).values()
            for booster in boosters:
                battleBoosterBonus = 0
                if booster.isAffectOnCrewLevel():
                    if booster.isInstalled(vehicle):
                        battleBoosterBonus = booster.getCrewBonus(vehicle)
                        finalEffVal += battleBoosterBonus
                    self.__addModifier(vm.getConsumables(), battleBoosterBonus, R.images.gui.maps.icons.vehParams.tooltips.bonuses.dyn(booster.name)(), booster.shortUserName)

        vm.setFinalEfficiencyValue(round(finalEffVal, 2))

    @staticmethod
    def __addModifier(modifierViewList, value, icon, title, description=''):
        modifierModel = TankmanTooltipModifierModel()
        modifierModel.setValue(round(value, 2))
        modifierModel.setIcon(icon)
        modifierModel.setTitle(title)
        modifierModel.setDescription(description)
        modifierViewList.addViewModel(modifierModel)
