# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/crew_presenter.py
from __future__ import absolute_import
from collections import OrderedDict
import typing
from enum import Enum
from future.utils import itervalues, iteritems
from typing import NamedTuple, Union
from CurrentVehicle import g_currentVehicle
from cgf_components.marker_component import IGuiLoader
from constants import RENEWABLE_SUBSCRIPTION_CONFIG
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.impl.gen.view_models.views.lobby.loadout.crew.bonus_skills_model import BonusSkillsModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.crew_model import CrewModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.perk_model import PerkModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.slot_model import SlotModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.tankman_model import TankmanModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.vehicle_bonus_detail_model import VehicleBonusDetailModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.gen_utils import DynAccessor
from gui.impl.lobby.crew.crew_header_tooltip_view import CrewHeaderTooltipView
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getTmanNewSkillCount, isTankmanSkillIrrelevant
from gui.impl.lobby.crew.widget.crew_widget import BuildedMessage
from gui.impl.pub.view_component import ViewComponent
from gui.shared.event_dispatcher import showBarracks, showChangeCrewMember, showPersonalCase
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import NO_TANKMAN, Tankman
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.shared.gui_items.processors.vehicle import VehicleTmenXPAccelerator
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, int2roman
from items.special_crew import CustomSkills
from items.tankmen import MAX_SKILL_LEVEL, getLessMasteredIDX
from nations import AVAILABLE_NAMES
from renewable_subscription_common.passive_xp import isTagsSetOk
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from frameworks.wulf import Array
DOG = 'dog'
BuiltMessage = NamedTuple('BuiltMessage', [('text', str),
 ('iconFrom', DynAccessor),
 ('iconTo', DynAccessor),
 ('vehFromCD', DynAccessor),
 ('vehToCD', DynAccessor)])

class IdleCrewBonus(Enum):
    DISABLED = 'Disabled'
    ENABLED = 'Enabled'
    ACTIVE_ON_CURRENT_VEHICLE = 'ActiveOnCurrentVehicle'
    INCOMPATIBLE_WITH_CURRENT_VEHICLE = 'IncompatibleWithCurrentVehicle'
    ACTIVE_ON_ANOTHER_VEHICLE = 'ActiveOnAnotherVehicle'
    INVISIBLE = 'Invisible'


def setCrewSlots(slots, vehicle):
    slots.clear()
    for slotIdx, tman in vehicle.crew:
        slot = SlotModel()
        slot.setId(slotIdx)
        roles = slot.getRoles()
        for role in vehicle.descriptor.type.crewRoles[slotIdx]:
            roles.addString(role)

        slot.setTankmanId(tman.invID if tman else NO_TANKMAN)
        slots.addViewModel(slot)

    slots.invalidate()


class CrewPresenter(ViewComponent[CrewModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(CrewPresenter, self).__init__(model=CrewModel)

    @property
    def viewModel(self):
        return super(CrewPresenter, self).getViewModel()

    def finalize(self):
        self._unsubscribe()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def createToolTipContent(self, event, contentID):
        return CrewHeaderTooltipView(self.__getIdleCrewState()) if contentID == R.views.lobby.crew.CrewHeaderTooltipView() else None

    def _onLoading(self, *args, **kwargs):
        super(CrewPresenter, self)._onLoading(*args, **kwargs)
        self._subscribe()
        self.__updateModel()

    def _getCallbacks(self):
        return (('idleCrewXP', self.__idleCrewXPUpdated),)

    def __idleCrewXPUpdated(self, diff):
        self.__updateIntensiveTraining()

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__onVehicleChanged),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange),
         (self.__wotPlusCtrl.onEnabledStatusChanged, self.__onWotPlusStatusChanged),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.viewModel.onOpenCrew, self.__onOpenCrew),
         (self.viewModel.onOpenBarracks, self.__onOpenBarracks),
         (self.viewModel.onDogMoreInfoClick, self.__onDogMoreInfoClick),
         (self.viewModel.onToggleAcceleratedTraining, self.__onToggleAcceleratedTraining),
         (self.viewModel.onToggleIntensiveTraining, self.__onToggleIntensiveTraining))

    @wg_async
    def __onToggleIntensiveTraining(self):
        wasActive = self.viewModel.getIntensiveTraining() == CrewModel.ON_TRAINING_STATE
        toBeActive = not wasActive

        def toggleCallback():
            vehId = g_currentVehicle.item.invID if toBeActive else None
            self.__wotPlusCtrl.selectIdleCrewXPVehicle(vehId)
            return

        dialogMessage = self.__buildConfirmationMessage()
        if not dialogMessage or not toBeActive:
            toggleCallback()
        else:
            from gui.shared.event_dispatcher import showIdleCrewBonusDialog
            uiLoader = dependency.instance(IGuiLoader)
            layoutID = R.views.dialogs.DefaultDialog()
            if uiLoader.windowsManager.getViewByLayoutID(layoutID) is None:
                yield wg_await(showIdleCrewBonusDialog(dialogMessage, toggleCallback))
            self.__updateIntensiveTraining()
        return

    def __buildConfirmationMessage(self):
        previousVehicleId = self.__wotPlusCtrl.getVehicleIDWithIdleXP()
        previousVehicle = self.__itemsCache.items.getVehicle(previousVehicleId) if previousVehicleId else None
        stringRoot = R.strings.dialogs.idleCrewBonus
        message = None
        if previousVehicle:
            vehicleFromName = '{} %(typeIconFrom) {}'.format(int2roman(previousVehicle.level), previousVehicle.userName)
            removeTypeStringFrom = backport.text(stringRoot.message.removeTypeFrom())
            removeVehFromNameString = backport.text(stringRoot.message.removeName(), vehicleName=vehicleFromName)
            vehicleToName = '{} %(typeIconTo) {}'.format(int2roman(g_currentVehicle.item.level), g_currentVehicle.item.userName)
            removeTypeStringTo = backport.text(stringRoot.message.removeTypeTo())
            removeVehToNameString = backport.text(stringRoot.message.removeName(), vehicleName=vehicleToName)
            endDot = backport.text(stringRoot.message.dot())
            finalString = '{} {} {} {}{}'.format(removeTypeStringFrom, removeVehFromNameString, removeTypeStringTo, removeVehToNameString, endDot)
            message = BuildedMessage(text=finalString, iconFrom=R.images.gui.maps.icons.vehicleTypes.num('24x24').dyn(getIconResourceName(previousVehicle.type)), iconTo=R.images.gui.maps.icons.vehicleTypes.num('24x24').dyn(getIconResourceName(g_currentVehicle.item.type)), vehFromCD=previousVehicle.intCD, vehToCD=g_currentVehicle.item.intCD)
        return message

    def __onWotPlusStatusChanged(self, _):
        self.__updateIntensiveTraining()

    @wg_async
    def __onToggleAcceleratedTraining(self):
        from gui.shared.event_dispatcher import showAccelerateCrewTrainingDialog
        vehicle = g_currentVehicle.item
        wasActive = vehicle.isXPToTman

        def toggleCallback():
            self.__onAccelerateCrewTrainingConfirmed(vehicle, wasActive)

        if wasActive:
            toggleCallback()
        else:
            uiLoader = dependency.instance(IGuiLoader)
            layoutID = R.views.dialogs.DefaultDialog()
            if uiLoader.windowsManager.getViewByLayoutID(layoutID) is None:
                yield wg_await(showAccelerateCrewTrainingDialog(toggleCallback))
        return

    @decorators.adisp_process('updateTankmen')
    def __onAccelerateCrewTrainingConfirmed(self, vehicle, wasActive):
        result = yield VehicleTmenXPAccelerator(vehicle, not wasActive, False).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __getIdleCrewState(self):
        if not self.__lobbyContext.getServerSettings().isRenewableSubPassiveCrewXPEnabled():
            return IdleCrewBonus.INVISIBLE
        if not self.__wotPlusCtrl.isEnabled():
            return IdleCrewBonus.DISABLED
        if not isTagsSetOk(g_currentVehicle.item.tags):
            return IdleCrewBonus.INCOMPATIBLE_WITH_CURRENT_VEHICLE
        if self.__wotPlusCtrl.hasVehicleCrewIdleXP(g_currentVehicle.item.invID):
            return IdleCrewBonus.ACTIVE_ON_CURRENT_VEHICLE
        return IdleCrewBonus.ACTIVE_ON_ANOTHER_VEHICLE if self.__wotPlusCtrl.getVehicleIDWithIdleXP() else IdleCrewBonus.ENABLED

    def __onOpenCrew(self, ctx):
        slotId = int(ctx.get('crewSlotId', 0))
        vehicle = self.__itemsCache.items.getVehicle(g_currentVehicle.item.invID)
        tankmanID = NO_TANKMAN
        for slotIdx, tman in vehicle.crew:
            if slotIdx == slotId:
                if tman:
                    tankmanID = tman.invID
                break

        if tankmanID == NO_TANKMAN:
            showChangeCrewMember(slotId, g_currentVehicle.item.invID)
        else:
            showPersonalCase(int(tankmanID))

    def __onOpenBarracks(self, ctx):
        showBarracks()

    def __onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.__updateIntensiveTraining()

    def __onVehicleChanged(self):
        self.__updateModel()

    def __onCacheResync(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff and g_currentVehicle.isPresent() and g_currentVehicle.item.intCD in diff[GUI_ITEM_TYPE.VEHICLE]:
                self.__updateModel()
            return

    def __updateModel(self):
        if g_currentVehicle.item is None:
            self.viewModel.setAcceleratedTraining(CrewModel.DISABLED_TRAINING_STATE)
            self.viewModel.setIntensiveTraining(CrewModel.DISABLED_TRAINING_STATE)
        else:
            self.__updateCrewModel()
            self.__updateAcceleratedTraining()
            self.__updateIntensiveTraining()
        return

    def __findLessMasteredTman(self):
        crew = OrderedDict(sorted(g_currentVehicle.item.crew, key=lambda item: item[0]))
        tankmenDescrs = [ (tman.descriptor if tman else None) for tman in itervalues(crew) ]
        return getLessMasteredIDX(tankmenDescrs)[1]

    def __updateCrewModel(self):
        with self.viewModel.transaction() as model:
            vehicle = self.__itemsCache.items.getVehicle(g_currentVehicle.item.invID)
            self.viewModel.setVehicleNation(vehicle.nationName)
            slots = model.getSlots()
            slots.clear()
            tankmenBerthsAmount = self.__itemsCache.items.stats.tankmenBerthsCount
            inBarracksTanksmenAmount = self.__itemsCache.items.tankmenInBarracksCount()
            model.setBerthsCount(max(tankmenBerthsAmount - inBarracksTanksmenAmount, 0))
            model.setState(self.__getCrewPanelState())
            model.setHasDog(DOG in self.__itemsCache.items.getItemByCD(g_currentVehicle.item.intCD).tags)
            crew = model.getCrew()
            crew.clear()
            lessMastered = self.__findLessMasteredTman()
            battleBoosterBonus = self.__calcVehicleBooster(vehicle)
            vehicleBonusDetails = self.__calcVehicleBonusDetails(vehicle)
            optDeviceBonuses = self.__calcOptDeviceBonuses(vehicle)
            for _, tman in vehicle.crew:
                if tman:
                    quickTrainingEnabled = vehicle.crewIndices.get(tman.invID) == lessMastered and vehicle.isXPToTman
                    tankman = self.__createTankmanModel(tman, battleBoosterBonus, quickTrainingEnabled, vehicleBonusDetails, optDeviceBonuses)
                    crew.addViewModel(tankman)

            for slotIdx, tman in vehicle.crew:
                slot = SlotModel()
                slot.setId(slotIdx)
                roles = slot.getRoles()
                for role in vehicle.descriptor.type.crewRoles[slotIdx]:
                    roles.addString(role)

                slot.setTankmanId(tman.invID if tman else NO_TANKMAN)
                slots.addViewModel(slot)

            crew.invalidate()
            slots.invalidate()

    def __calcVehicleBonusDetails(self, vehicle):
        if vehicle.consumables.layoutCapacity:
            basic = REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.EQUIPMENT])
            criteria = basic | ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET
            equipments = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.EQUIPMENT, criteria, nationID=vehicle.nationID).values()
            return [ self.__createVehicleBonusDetail(name=equipment.descriptor.iconName, bonusType=TankSetupConstants.CONSUMABLES, bonus=equipment.crewLevelIncrease if equipment.isInstalled(vehicle) else 0) for equipment in equipments if equipment.isStimulator ]
        return []

    def __calcOptDeviceBonuses(self, vehicle):
        if vehicle.optDevices.layoutCapacity:
            optDevices = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.OPTIONALDEVICE]) | ~REQ_CRITERIA.SECRET, nationID=vehicle.nationID).values()
            mergedBonuses = {}
            for optDevice in optDevices:
                if not optDevice.descriptor.factorsContainCrewLevelIncrease():
                    continue
                artefactsBonus = 0
                if optDevice.isInstalled(vehicle):
                    attrPath = 'miscAttrs/crewLevelIncrease'
                    artefactsBonus = optDevice.descriptor.getFactorValue(vehicle.descriptor, attrPath)
                if mergedBonuses.get(optDevice.descriptor.iconName):
                    mergedBonuses[optDevice.descriptor.iconName] += artefactsBonus
                mergedBonuses[optDevice.descriptor.iconName] = artefactsBonus

            return [ self.__createVehicleBonusDetail(name=name, bonusType=TankSetupConstants.OPT_DEVICES, bonus=value) for name, value in mergedBonuses.items() ]
        return []

    def __calcVehicleBooster(self, vehicle):
        if vehicle.battleBoosters.layoutCapacity:
            basic = REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.BATTLE_BOOSTER])
            criteria = basic | ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET
            boosters = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_BOOSTER, criteria).values()
            for booster in boosters:
                if not booster.isAffectOnCrewLevel():
                    continue
                if booster.isInstalled(vehicle) and booster.isAffectOnCrewLevel():
                    return self.__createVehicleBonusDetail(name=booster.descriptor.iconName, bonusType=TankSetupConstants.BATTLE_BOOSTERS, bonus=booster.getCrewBonus(vehicle))

        return None

    def __createTankmanModel(self, tman, battleBoosterBonus, isQuickTrainingEnabled, vehicleBonusDetails, optDeviceBonuses):
        newSkillsCount, lastSkillLevel = getTmanNewSkillCount(tman, withFree=True)
        man = TankmanModel()
        man.setId(tman.invID)
        man.setQuickTraining(isQuickTrainingEnabled)
        man.setLevel(tman.earnedSkillsCount - len(tman.skillsInProgress))
        man.setMaxLevelAchieved(tman.allSkillsLearned())
        man.setCrewSkinId(tman.getExtensionLessIconWithSkin())
        man.setCustomizedSkin(tman.isInSkin)
        man.setNewPerksCount(newSkillsCount)
        man.setTrainingProgress(lastSkillLevel.intSkillLvl)
        self.__addMajorSkills(tman, man)
        self.__addBonusSkills(tman, man)
        man.setIsInNativeTank(tman.isInNativeTank or tman.canUseSkillsInCurrentVehicle)
        man.setRole(tman.role)
        man.setFullName(tman.getFullUserNameWithSkin())
        man.setNation(AVAILABLE_NAMES[tman.nationID])
        man.setSkillsEfficiency(tman.skillsEfficiency)
        man.setSkillsEfficiencyXP(tman.skillsEfficiencyXP)
        man.setCurrentVehicleSkillsEfficiency(tman.currentVehicleSkillsEfficiency)
        man.setLockedByVehicle(tman.isLockedByVehicle())
        man.nativeVehicle.setNation(AVAILABLE_NAMES[tman.nationID])
        man.nativeVehicle.setShortName(tman.vehicleNativeDescr.type.shortUserString)
        man.nativeVehicle.setType(tman.vehicleNativeDescr.type.classTag)
        man.nativeVehicle.setTier(tman.vehicleNativeDescr.type.level)
        man.vehicleBonus.setCommander(tman.vehicleBonuses.get('commander', 0))
        man.vehicleBonus.setEquipment(tman.vehicleBonuses.get('equipment', 0))
        man.vehicleBonus.setBrotherhood(tman.vehicleBonuses.get('brotherhood', 0))
        man.vehicleBonus.setOptDevices(tman.vehicleBonuses.get('optDevices', 0))
        boosterBonusValue = tman.vehicleBonuses.get('battleBooster', 0)
        if battleBoosterBonus is not None:
            boosterBonusValue = battleBoosterBonus.getBonus()
        man.vehicleBonus.setBattleBooster(boosterBonusValue)
        man.setTankmanSuitable(self.__isTankmanTrainedForVehicle(tman))
        self.__setEquipmentsBonuses(man, tman, battleBoosterBonus, vehicleBonusDetails, optDeviceBonuses)
        return man

    def __addMajorSkills(self, tman, model):
        perks = model.getPerks()
        perks.clear()
        self.__addSkills(tman, tman.skills, perks)

    def __addBonusSkills(self, tman, model):
        bonusSkills = model.getBonusSkills()
        bonusSkills.clear()
        newCommonBonusPerksCount = 0
        for role, skills in iteritems(tman.bonusSkills):
            roleBonusSkills = BonusSkillsModel()
            roleBonusSkills.setRole(role)
            availableBonusSkillsCountByRole = tman.bonusSkillsCountByRole.get(role) + tman.newBonusSkillsCountByRole.get(role)
            bonusTrainingProgress = tman.bonusSlotsLevels[availableBonusSkillsCountByRole - 1] if availableBonusSkillsCountByRole > 0 else CrewConstants.DONT_SHOW_LEVEL
            roleBonusSkills.setTrainingProgress(bonusTrainingProgress)
            newBonusSkillsCount = tman.newBonusSkillsCountByRole.get(role)
            roleBonusSkills.setNewCount(newBonusSkillsCount)
            newCommonBonusPerksCount += newBonusSkillsCount
            roleBonusSkillsArray = roleBonusSkills.getSkills()
            roleBonusSkillsArray.clear()
            self.__addSkills(tman, skills, roleBonusSkillsArray)
            bonusSkills.addViewModel(roleBonusSkills)

        model.setNewBonusPerksCount(newCommonBonusPerksCount)

    def __addSkills(self, tman, skills, container):
        for skill in skills:
            if skill is not None:
                state = self.__getPerkState(skill, tman)
                self.__addPerkModel(skill, state, container)

        return

    def __addPerkModel(self, skill, state, container):
        name = skill.customName or skill.name
        perk = PerkModel()
        perk.setName(name)
        perk.setState(state)
        container.addViewModel(perk)

    def __createVehicleBonusDetail(self, name, bonusType, bonus):
        bonusDetail = VehicleBonusDetailModel()
        bonusDetail.setName(name)
        bonusDetail.setType(bonusType)
        bonusDetail.setBonus(bonus)
        return bonusDetail

    def __setBrotherhoodBonus(self, model, tankman):
        _, customName = CustomSkills.getCustomSkill(VehicleBonusDetailModel.BROTHERHOOD, tankman)
        bonusDetail = self.__createVehicleBonusDetail(name=customName or VehicleBonusDetailModel.BROTHERHOOD, bonusType=VehicleBonusDetailModel.BROTHERHOOD, bonus=tankman.vehicleBonuses.get(VehicleBonusDetailModel.BROTHERHOOD, 0))
        model.addViewModel(bonusDetail)

    def __setCommanderBonus(self, model, tankman):
        model.addViewModel(self.__createVehicleBonusDetail(name='commander_bonus', bonusType=VehicleBonusDetailModel.COMMANDER, bonus=tankman.vehicleBonuses.get(VehicleBonusDetailModel.COMMANDER, 0)))

    def __setEquipmentsBonuses(self, man, tankman, battleBoosterBonus, vehicleBonusDetails, optDeviceBonuses):
        vehicleBonusDetailsModel = man.getVehicleBonusDetails()
        vehicleBonusDetailsModel.clear()
        self.__setBrotherhoodBonus(vehicleBonusDetailsModel, tankman)
        if tankman.role != Tankman.ROLES.COMMANDER:
            self.__setCommanderBonus(vehicleBonusDetailsModel, tankman)
        for vehicleBonusDetail in optDeviceBonuses:
            vehicleBonusDetailsModel.addViewModel(vehicleBonusDetail)

        for vehicleBonusDetail in vehicleBonusDetails:
            vehicleBonusDetailsModel.addViewModel(vehicleBonusDetail)

        if battleBoosterBonus is not None:
            vehicleBonusDetailsModel.addViewModel(battleBoosterBonus)
        vehicleBonusDetailsModel.invalidate()
        return

    def __getCrewPanelState(self):
        veh = g_currentVehicle.item
        return CrewModel.DISABLED_STATE if veh.isDisabled or veh.isLocked or veh.isInBattle or veh.isAwaitingBattle or veh.isInPrebattle else CrewModel.DEFAULT_STATE

    @staticmethod
    def __isTankmanTrainedForVehicle(tman):
        return True if tman is None else tman.roleLevel >= MAX_SKILL_LEVEL and tman.realRoleLevel.bonuses.penalty >= 0

    @staticmethod
    def __getPerkState(skill, tman):
        if skill.isZero:
            return PerkModel.FREE_STATE
        if isTankmanSkillIrrelevant(tman, skill):
            return PerkModel.IRRELEVANT_STATE
        return PerkModel.LEARNED_STATE if skill.isMaxLevel else PerkModel.LEARNING_STATE

    def __updateAcceleratedTraining(self):
        isXPToTman = g_currentVehicle.item.isXPToTman if g_currentVehicle.item else False
        acceleratedTrainingState = CrewModel.DISABLED_TRAINING_STATE
        if isXPToTman:
            acceleratedTrainingState = CrewModel.ON_TRAINING_STATE
        elif g_currentVehicle.item.isElite:
            acceleratedTrainingState = CrewModel.OFF_TRAINING_STATE
        self.viewModel.setAcceleratedTraining(acceleratedTrainingState)

    def __updateIntensiveTraining(self):
        with self.viewModel.transaction() as vm:
            wotPlusState = CrewModel.DISABLED_TRAINING_STATE
            vehicle = g_currentVehicle.item
            if vehicle and self.__lobbyContext.getServerSettings().isRenewableSubPassiveCrewXPEnabled():
                if not self.__wotPlusCtrl.isEnabled() or not isTagsSetOk(vehicle.tags):
                    wotPlusState = CrewModel.DISABLED_TRAINING_STATE
                elif self.__wotPlusCtrl.hasVehicleCrewIdleXP(vehicle.invID):
                    wotPlusState = CrewModel.ON_TRAINING_STATE
                else:
                    wotPlusState = CrewModel.OFF_TRAINING_STATE
            vm.setIntensiveTraining(wotPlusState)

    def __onDogMoreInfoClick(self):
        from gui.impl.dialogs import dialogs
        from gui.impl.dialogs.gf_builders import ResDialogBuilder
        builder = ResDialogBuilder()
        builder.setMessagesAndButtons(R.strings.dialogs.rudyInfo, buttons=R.invalid)
        builder.setIcon(R.images.gui.maps.icons.tankmen.windows.aboutRudy())
        dialogs.show(builder.build())
