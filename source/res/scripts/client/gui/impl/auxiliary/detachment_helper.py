# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/detachment_helper.py
import time
import typing
import nations
from AccountCommands import LOCK_REASON
from CurrentVehicle import g_currentVehicle
from constants import SECONDS_IN_DAY
from crew2 import settings_globals
from crew2.detachment_states import CanAssignResult
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl.auxiliary.instructors_helper import fillInstructorConvertList, fillInstructorList
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_base_model import DetachmentBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_card_model import DetachmentCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_location_constants import DetachmentLocationConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_instructor_model import DetachmentShortInfoInstructorModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_states import DetachmentStates
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_with_points_model import DetachmentWithPointsModel
from gui.impl.gen.view_models.views.lobby.detachment.common.dismiss_states import DismissStates
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.detachment.common.recruit_constants import RecruitConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.rose_sheet_model import RoseSheetModel
from gui.impl.gen.view_models.views.lobby.detachment.common.skill_constants import SkillConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.skill_model import SkillModel
from gui.shared.gui_items.crew_skin import localizedFullName, getCrewSkinIconSmallWithoutPath
from gui.shared.money import Money
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, i18n
from items.components.component_constants import EMPTY_STRING
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.components.detachment_components import getBranchPointsAndTalents
from items.components.detachment_constants import DetachmentOperations, DOG_TAG, SPECIALIZATION_PAYMENT_OPTION_TO_TYPE, NO_DETACHMENT_ID, DropSkillPaymentOption, PROGRESS_MAX
from items.tankmen import MAX_SKILL_LEVEL
from skeletons.gui.detachment import IDetachmentCache, IDetachementStates
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from typing import Tuple, Optional, Dict, List
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
    from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_top_panel_model import DetachmentTopPanelModel
    from crew2.perk.matrices import PerkMatrix
    from gui.shared.gui_items.detachment import Detachment
    from gui.shared.gui_items import Vehicle
    from gui.shared.gui_items.Tankman import Tankman
    from gui.impl.gen.view_models.views.lobby.detachment.common.rose_model import RoseModel
    from skeletons.gui.shared.utils import IItemsRequester
PROGRESS_DELTA_UNCHANGED = -1
LEVEL_NO_GAINED = 0
DEFAULT_LVL_ICON_ID = -1
_CAN_ASSIGN_TO_DETACHMENT_STATE = {CanAssignResult.OK: DetachmentStates.AVAILABLE,
 CanAssignResult.SAME_VEHICLE: DetachmentStates.SELECTED,
 CanAssignResult.DETACHMENT_LOCKED: DetachmentStates.IN_BATTLE,
 CanAssignResult.WRONG_CLASS: DetachmentStates.WRONG_CLASS,
 CanAssignResult.NON_SUITABLE_TYPE: DetachmentStates.WRONG_SPECIALIZATION,
 CanAssignResult.DETACHMENT_DISSOLVED: DetachmentStates.DISMISSED,
 CanAssignResult.DETACHMENT_LOCKED_BY_LOCK_CREW: DetachmentStates.AVAILABLE}

@dependency.replace_none_kwargs(detachmentStates=IDetachementStates)
def isDetachmentLocked(detachment, detachmentStates=None):
    return detachmentStates.states.isDetachmentLocked(detachment.invID)


@dependency.replace_none_kwargs(detachmentStates=IDetachementStates)
def isDetachmentInRecycleBin(detachment, detachmentStates=None):
    return detachmentStates.states.isDetachmentDissolved(detachment.invID)


@dependency.replace_none_kwargs(detachmentStates=IDetachementStates)
def canProcessDetachment(detachment, detachmentStates=None, checkLockCrew=True):
    return detachmentStates.states.canProcessDetachment(detachment.invID, checkLockCrew)


def getVehicleLockStatusForDetachment(detGuiItem, vehicle=None, checkLockCrew=True):
    if isDetachmentInRecycleBin(detGuiItem):
        return (CanAssignResult.DETACHMENT_DISSOLVED, None)
    else:
        if detGuiItem.isInTank:
            if vehicle:
                pass
            else:
                itemsCache = dependency.instance(IItemsCache)
                vehicle = itemsCache.items.getVehicle(detGuiItem.vehInvID)
                if not vehicle:
                    return (CanAssignResult.DETACHMENT_LOCKED, None)
            if vehicle.isLocked:
                return (CanAssignResult.VEHICLE_LOCKED, vehicle.lockReason)
            if checkLockCrew and vehicle.isCrewLocked:
                return (CanAssignResult.VEHICLE_HAS_LOCK_CREW, None)
        return (CanAssignResult.OK, None)


@dependency.replace_none_kwargs(detachmentStates=IDetachementStates)
def canAssignDetachmentToVehicle(detachment, vehicle, detachmentStates=None):
    return detachmentStates.states.canAssignDetachmentToVehicle(detachment.invID, vehicle.invID)


def getDetachmentLockState(detachment):
    canProcessRes, reason = getVehicleLockStatusForDetachment(detachment)
    if canProcessRes == CanAssignResult.DETACHMENT_DISSOLVED:
        return DetachmentStates.DISMISSED
    if canProcessRes == CanAssignResult.VEHICLE_LOCKED:
        if reason == LOCK_REASON.ON_ARENA:
            return DetachmentStates.IN_BATTLE
        if reason == LOCK_REASON.UNIT or reason == LOCK_REASON.PREBATTLE:
            return DetachmentStates.IN_PLATOON
    return DetachmentStates.UNKNOWN


def getVehicleLockState(vehicle):
    if vehicle.isLocked:
        if vehicle.lockReason == LOCK_REASON.ON_ARENA:
            return DetachmentStates.IN_BATTLE
        if vehicle.lockReason == LOCK_REASON.UNIT or vehicle.lockReason == LOCK_REASON.PREBATTLE:
            return DetachmentStates.IN_PLATOON
    return EMPTY_STRING


def getDetachmentDismissState(detachment):
    lobbyContext = dependency.instance(ILobbyContext)
    if not detachment or not lobbyContext.getServerSettings().isDissolveDetachmentEnabled():
        return DismissStates.DISABLE
    canProcessRes, _ = getVehicleLockStatusForDetachment(detachment)
    if detachment.isSellsDailyLimitReached():
        return DismissStates.SELL_LIMIT_REACHED
    if canProcessRes == CanAssignResult.VEHICLE_HAS_LOCK_CREW:
        return DismissStates.HAS_LOCK_CREW
    return DismissStates.DISABLE if canProcessRes == CanAssignResult.VEHICLE_LOCKED else DismissStates.AVAILABLE


def _trimImageExt(imagePath):
    return imagePath[:-len('.png')]


def _setCardLocation(cardModel, detachmentGuiItem):
    if detachmentGuiItem.isInTank:
        location = DetachmentLocationConstants.VEHICLE
    elif detachmentGuiItem.isInRecycleBin:
        location = DetachmentLocationConstants.DISMISSED
    else:
        location = DetachmentLocationConstants.BARRACKS
    cardModel.setLocation(location)


def _setDetachmentCardState(detachmentModel, detachmentGuiItem, canAssignResult):
    state = _CAN_ASSIGN_TO_DETACHMENT_STATE.get(canAssignResult, DetachmentStates.UNKNOWN)
    if state == DetachmentStates.WRONG_SPECIALIZATION:
        for detSlotVehCD in detachmentGuiItem.vehicleSlots:
            if detSlotVehCD is None:
                state = DetachmentStates.EMPTY_VEHICLE_SLOT
                break

    elif state == DetachmentStates.IN_BATTLE:
        state = getDetachmentLockState(detachmentGuiItem)
    dismissState = getDetachmentDismissState(detachmentGuiItem)
    detachmentModel.setIsDismissDisable(dismissState != DismissStates.AVAILABLE)
    detachmentModel.setState(state)
    return


def fillRestorePriceModel(priceModel, stats, detInvID=None):
    priceData = getDetachmentRestorePrice(detInvID, 0)
    defaultPrice = getDetachmentRestorePrice(detInvID, 0, default=True)
    currency = priceData.getCurrency()
    price = priceData.get(currency, 0)
    defaultPrice = defaultPrice.get(currency, 0)
    isDiscount = defaultPrice != price
    priceModel.setType(currency)
    priceModel.setValue(price)
    priceModel.setIsEnough(not stats.money.getShortage(priceData).get(currency))
    priceModel.setHasDiscount(isDiscount)
    if isDiscount:
        priceModel.setDiscountValue(100 - int(price * 100.0 / defaultPrice))


def fillDetachmentBaseModel(detBaseModel, detachmentGuiItem, inVehicle=None):
    fillDetachmentShortInfoModel(detBaseModel, detachmentGuiItem, fillInstructors=False)
    _setCardLocation(detBaseModel, detachmentGuiItem)
    detBaseModel.setNation(detachmentGuiItem.nationName)
    detBaseModel.vehicle.setType(detachmentGuiItem.classTypeUnderscore)
    if inVehicle:
        detBaseModel.vehicle.setName(inVehicle.shortUserName)
    fillInstructorList(detBaseModel.getInstructorsList(), detachmentGuiItem)


def fillDetachmentCardModel(cardModel, detachmentGuiItem, inVehicle=None, assignVehicle=None):
    if assignVehicle is not None:
        detStatus = canAssignDetachmentToVehicle(detachmentGuiItem, assignVehicle)
    else:
        detStatus = canProcessDetachment(detachmentGuiItem)
    _setDetachmentCardState(cardModel, detachmentGuiItem, detStatus)
    fillDetachmentBaseModel(cardModel, detachmentGuiItem, inVehicle=inVehicle)
    cardModel.setAvailablePoints(detachmentGuiItem.freePoints)
    if detachmentGuiItem.isInRecycleBin:
        cardModel.setRecoveryTime(detachmentGuiItem.expDate)
    return


def fillDetachmentShortInfoModel(model, detachmentGuiItem, fillInstructors=True, vehicle=None):
    model.setId(detachmentGuiItem.invID)
    model.setName(detachmentGuiItem.cmdrFullName)
    model.setRank(detachmentGuiItem.rankName)
    model.setLevel(detachmentGuiItem.level)
    model.setPrevLevel(detachmentGuiItem.level)
    model.setMaxLevel(detachmentGuiItem.getDescriptor().progression.maxLevel)
    currentProgress = detachmentGuiItem.currentXPProgress * PROGRESS_MAX
    model.setProgressValue(currentProgress)
    model.setProgressDeltaFrom(-1)
    model.setProgressMax(PROGRESS_MAX)
    model.setCommanderIcon(detachmentGuiItem.cmdrPortrait)
    model.setHasCrewSkin(detachmentGuiItem.hasSkin)
    model.setIsUnique(detachmentGuiItem.uniqueCmdrIcon is not None)
    model.setCommanderIconName(detachmentGuiItem.cmdrPortraitIconName)
    model.setStripeIcon(detachmentGuiItem.rankIcon)
    model.setIsMaxLevel(detachmentGuiItem.hasMaxMasteryLevel)
    model.setIsElite(detachmentGuiItem.hasMaxLevel)
    model.setLevelIconId(detachmentGuiItem.levelIconID)
    model.setNation(detachmentGuiItem.nationName)
    model.setMastery(detachmentGuiItem.masteryName)
    model.vehicle.setType(detachmentGuiItem.classTypeUnderscore)
    if vehicle is None:
        itemsCache = dependency.instance(IItemsCache)
        vehicle = itemsCache.items.getVehicle(detachmentGuiItem.vehInvID)
    fillDog(model, vehicle)
    if fillInstructors:
        instructorsList = model.getInstructorsList()
        fillInstructorList(instructorsList, detachmentGuiItem, fillEmpty=False, customModel=DetachmentShortInfoInstructorModel)
    return


def fillDog(model, vehicle):
    if vehicle is None:
        return
    else:
        hasDog = DOG_TAG in vehicle.tags
        model.setHasDog(hasDog)
        if hasDog:
            vehNationName = vehicle.nationName
            headerKey = ''.join((TOOLTIPS.HANGAR_CREW_RUDY_DOG, vehNationName, '/header'))
            model.setDogTooltipHeader(i18n.makeString(headerKey))
            bodyKey = ''.join((TOOLTIPS.HANGAR_CREW_RUDY_DOG, vehNationName, '/body'))
            model.setDogTooltipText(i18n.makeString(bodyKey))
        return


def fillDetachmentWithPointsModel(model, detDescr, skinID, instrDescrs, vehicle, itemsCache=None, itemsFactory=None, lobbyContext=None):
    if itemsCache is None:
        itemsCache = dependency.instance(IItemsCache)
    if itemsFactory is None:
        itemsFactory = dependency.instance(IGuiItemsFactory)
    if lobbyContext is None:
        lobbyContext = dependency.instance(ILobbyContext)
    detachment = itemsFactory.createDetachment(detDescr.makeCompactDescr())
    model.setRank(detachment.rankName)
    model.setAvailablePoints(detachment.freePoints)
    model.setLevel(detachment.level)
    model.setPrevLevel(detachment.level)
    currentProgress = detachment.currentXPProgress * PROGRESS_MAX
    model.setProgressDeltaFrom(-1)
    model.setProgressValue(currentProgress)
    model.setProgressMax(PROGRESS_MAX)
    model.setLevelIconId(detachment.levelIconID)
    model.setPrevLevelIconId(detachment.levelIconID)
    model.setIsMaxLevel(detachment.hasMaxMasteryLevel)
    model.setIsElite(detachment.hasMaxLevel)
    model.setNation(detachment.nationName)
    model.setStripeIcon(detachment.rankIcon)
    model.setCommanderIconName(detachment.cmdrPortraitIconName)
    model.setIsUnique(detachment.uniqueCmdrIcon is not None)
    model.setName(detachment.cmdrFullName)
    model.setMastery(detachment.masteryName)
    model.vehicle.setType(detachment.classTypeUnderscore)
    fillDog(model, vehicle)
    model.setHasCrewSkin(False)
    if skinID != NO_CREW_SKIN_ID and lobbyContext.getServerSettings().isCrewSkinsEnabled():
        skinItem = itemsCache.items.getCrewSkin(skinID)
        if skinItem.getFreeCount():
            model.setName(localizedFullName(skinItem))
            model.setHasCrewSkin(True)
            model.setCommanderIconName(skinItem.getIconID())
    instructorsListVM = model.getInstructorsList()
    instructors, emptyInstructorSlots = fillInstructorConvertList(instructorsListVM, detDescr, instrDescrs)
    instructorsListVM.invalidate()
    model.setEmptyInstructorSlots(emptyInstructorSlots)
    return instructors


def fillRoseSheetsModel(roseModel, detachment, vehicle=None, newBuild={}, diffBuild=None):
    from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
    matrixSett = detachment.getDescriptor().getPerksMatrix()
    roseSheets = roseModel.getSheets()
    branchPoints, branchTalents, _ = getBranchPointsAndTalents(matrixSett, detachment.build)
    newBranchPoints, newBranchTalents, _ = getBranchPointsAndTalents(matrixSett, newBuild)
    for branch in matrixSett.branches.itervalues():
        if len(roseSheets) <= branch.index:
            roseSheetModel = RoseSheetModel()
            roseSheetModel.setCourse(branch.index)
            roseSheetModel.setIconName(branch.icon)
            roseSheets.addViewModel(roseSheetModel)
        else:
            roseSheetModel = roseSheets.getValue(branch.index)
        roseMaxPoints = branch.ultimate_threshold
        savedBranchPoints = branchPoints.get(branch.id, 0)
        roseSheetModel.setProgress(savedBranchPoints * PROGRESS_MAX / roseMaxPoints)
        if newBuild:
            currentBranchPoints = newBranchPoints.get(branch.id, 0)
            if currentBranchPoints < savedBranchPoints:
                roseSheetModel.setProgress(currentBranchPoints * PROGRESS_MAX / roseMaxPoints)
                roseSheetModel.setPlus(0)
            else:
                roseSheetModel.setPlus((currentBranchPoints - savedBranchPoints) * PROGRESS_MAX / roseMaxPoints)
            roseSheetModel.setIsUltimate(newBranchTalents.get(branch.id, False))
        else:
            roseSheetModel.setPlus(False)
            roseSheetModel.setIsUltimate(branchTalents.get(branch.id, False))
        comparableInstructors = g_detachmentTankSetupVehicle.comparableInstructors
        instructorInfluence = detachment.getPerksInstructorInfluence(bonusPerks=diffBuild, vehicle=vehicle, comparableInstructors=comparableInstructors)
        bonusPoints = sum((points for _, perkID, points, _ in instructorInfluence if matrixSett.perks[perkID].branch == branch.id))
        roseSheetModel.setInstructorPoints(bonusPoints)
        boosterInfluence = detachment.getPerksBoosterInfluence(bonusPerks=diffBuild, vehicle=vehicle, comparableInstructors=comparableInstructors)
        bonusPoints = sum((points for _, perkID, points, _ in boosterInfluence if matrixSett.perks[perkID].branch == branch.id))
        roseSheetModel.setBoosterPoints(bonusPoints)
        totalPerks = detachment.getPerks(bonusPerks=diffBuild)
        hasOvercappedPerk = any((points > matrixSett.perks[perkID].max_points for perkID, points in totalPerks.iteritems() if perkID in matrixSett.perks and matrixSett.perks[perkID].branch == branch.id))
        roseSheetModel.setHasOvercappedPerk(hasOvercappedPerk)

    roseSheets.invalidate()


def fillDetachmentTopPanelModel(model, detachment):
    detDescr = detachment.getDescriptor()
    model.setName(detachment.cmdrFullName)
    model.setIcon(detachment.cmdrPortrait)
    model.setNation(detachment.nationName)
    model.setRankIcon(R.images.gui.maps.icons.detachment.ranks.c_160x118.dyn(detachment.rankIconName)())
    model.setPointsAvailable(detachment.freePoints)
    model.setMasteryLevel(R.strings.detachment.eliteLevel.num(detDescr.masteryLevel)())
    detachmentInfo = model.detachmentInfo
    fillDetachmentShortInfoModel(detachmentInfo, detachment, fillInstructors=False)
    if not detachment.hasMaxMasteryLevel:
        nextLevel = detachment.level if detachment.hasMaxLevel else detachment.level + 1
        detachmentInfo.setNextLevel(nextLevel)
        detachmentInfo.setNextLevelIconId(detachment.nextLevelIconID)
        detachmentInfo.setNextLevelIsElite(nextLevel >= detachment.progression.maxLevel)


def fillDetachmentPreviewInfo(model, detachment, gainedXP):
    detachmentInfo = model.detachmentInfo
    if detachment.hasMaxMasteryLevel:
        detachmentInfo.setExperienceOverflow(gainedXP)
        detachmentInfo.setGainLevels(LEVEL_NO_GAINED)
        return
    progression = detachment.progression
    detDescr = detachment.getDescriptor()
    maxRawLevel = progression.maxLevel + progression.maxMasteryLevel
    dirtyXP = detDescr.experience + gainedXP
    accumulatedXP = min(dirtyXP, progression.getLevelStartingXP(maxRawLevel))
    gainedLevel = progression.getRawLevelByXP(accumulatedXP)
    gainedDelta = max(gainedLevel - detDescr.rawLevel, LEVEL_NO_GAINED)
    detachmentInfo.setGainLevels(gainedDelta)
    nextLvlXP = progression.getLevelStartingXP(min(gainedLevel + 1, maxRawLevel))
    gainedLvlXP = progression.getLevelStartingXP(gainedLevel)
    eps = (nextLvlXP - gainedLvlXP) / PROGRESS_MAX
    normalizedLvlXP = accumulatedXP - gainedLvlXP
    roundGainedXP = gainedDelta and normalizedLvlXP <= eps
    lowerEdgeLvl = gainedLevel - int(roundGainedXP)
    upperEdgeLvl = lowerEdgeLvl + 1
    upperEdgeXP = progression.getLevelStartingXP(upperEdgeLvl)
    detachmentInfo.setNextLevel(min(progression.maxLevel, upperEdgeLvl))
    detachmentInfo.setNextLevelIsElite(upperEdgeLvl >= progression.maxLevel)
    detachmentInfo.setNextLevelIconId(progression.getLevelIconByXP(upperEdgeXP))
    if gainedXP:
        accumulatedXP = upperEdgeXP if roundGainedXP else accumulatedXP
        lowerEdgeXP = progression.getLevelStartingXP(lowerEdgeLvl)
        lvlRangeXP = upperEdgeXP - lowerEdgeXP
        deltaXPProgress = 1.0 - float(upperEdgeXP - accumulatedXP) / lvlRangeXP
        currentXPProgress = detachment.currentXPProgress
        detachmentInfo.setProgressValue(deltaXPProgress * PROGRESS_MAX)
        detachmentInfo.setProgressDeltaFrom(currentXPProgress * PROGRESS_MAX)
    else:
        currentXPProgress = detachment.currentXPProgress
        detachmentInfo.setProgressValue(currentXPProgress * PROGRESS_MAX)
        detachmentInfo.setProgressDeltaFrom(PROGRESS_DELTA_UNCHANGED)


def hasDetachmentInCurrentVehicle():
    currentVehicle = g_currentVehicle.item
    return currentVehicle.getLinkedDetachmentID() != NO_DETACHMENT_ID if currentVehicle else False


def getRecoveryTerms(detachment, detachmentSettings):
    expDate = detachment.expDate
    dissolveTime = expDate - detachmentSettings.holdInRecycleBinTerm * SECONDS_IN_DAY
    freeExpTime = dissolveTime + detachmentSettings.specialRestoreTerm * SECONDS_IN_DAY
    now = time.time()
    fullTerm = int((expDate - now) / SECONDS_IN_DAY)
    freeTerm = int((freeExpTime - now) / SECONDS_IN_DAY)
    paidTerm = fullTerm - freeTerm
    return (fullTerm, freeTerm, paidTerm)


def getTankmanResIcon(tankman):
    lobbyContext = dependency.instance(ILobbyContext)
    itemsCache = dependency.instance(IItemsCache)
    iconName = _trimImageExt(tankman.icon).replace('-', '_')
    if tankman.skinID != NO_CREW_SKIN_ID and lobbyContext.getServerSettings().isCrewSkinsEnabled():
        skinItem = itemsCache.items.getCrewSkin(tankman.skinID)
        iconName = _trimImageExt(getCrewSkinIconSmallWithoutPath(skinItem.getIconID(), False))
    return R.images.gui.maps.icons.tankmen.icons.big.dyn(iconName)()


def fillRecruitModel(model, tankman, desc, endRestoreTime=0):
    lobbyContext = dependency.instance(ILobbyContext)
    itemsCache = dependency.instance(IItemsCache)

    def _createSkill(idd, iconName, isAllocate, isPerk, skillPercent=0):
        skill = SkillModel()
        skill.setId(idd)
        skill.setIcon(iconName)
        skill.setIsAllocated(isAllocate)
        skill.setSkillPercent(skillPercent)
        skill.setType(SkillConstants.SKILL if not isPerk else SkillConstants.ABILITY)
        return skill

    if tankman.skinID != NO_CREW_SKIN_ID and lobbyContext.getServerSettings().isCrewSkinsEnabled():
        skinItem = itemsCache.items.getCrewSkin(tankman.skinID)
        model.setHasCrewSkin(True)
        icon = _trimImageExt(getCrewSkinIconSmallWithoutPath(skinItem.getIconID(), False))
        model.setIcon(replaceHyphenToUnderscore(icon))
        model.setName(localizedFullName(skinItem))
    else:
        model.setName(tankman.fullUserName)
        model.setIcon(replaceHyphenToUnderscore(_trimImageExt(tankman.icon)))
    model.setId(tankman.invID)
    model.setDescription(desc)
    model.setNation(nations.NAMES[tankman.nationID])
    model.setSpecialization(tankman.role)
    if tankman.isDismissed:
        model.setState(RecruitConstants.DISMISSED)
    elif tankman.isInTank:
        model.setState(RecruitConstants.ON_VEHICLE)
    else:
        model.setState(RecruitConstants.IN_BARRACK)
    vehicle = itemsCache.items.getVehicle(tankman.vehicleInvID)
    if vehicle is not None:
        if vehicle.isInBattle:
            model.setStatus(RecruitConstants.IN_BATTLE)
        elif vehicle.isInUnit:
            model.setStatus(RecruitConstants.IN_PLATOON)
    conversion = settings_globals.g_conversion
    instructorSettings, _ = conversion.getInstructorForTankman(tankman.descriptor)
    if instructorSettings:
        model.setType(RecruitConstants.INSTRUCTOR)
    elif conversion.getDetachmentForTankman(tankman.descriptor):
        model.setType(RecruitConstants.LEADER)
    elif tankman.roleLevel < MAX_SKILL_LEVEL and not tankman.skills:
        model.setType(RecruitConstants.INEXPERIENCED)
    else:
        model.setType(RecruitConstants.DEFAULT)
    nativeVehicle = itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
    if nativeVehicle:
        model.setIsLocked(nativeVehicle.isCrewLocked)
    model.setEndRestoreTime(endRestoreTime)
    model.skills.clearItems()
    if tankman.roleLevel == MAX_SKILL_LEVEL and not tankman.skills or tankman.descriptor.lastSkillLevel == MAX_SKILL_LEVEL:
        model.skills.addViewModel(_createSkill(-1, '', False, False))
    for i, skill in enumerate(tankman.skills):
        model.skills.addViewModel(_createSkill(i, skill.name, True, skill.isPerk, skill.level))

    count, lastNewSkillLevel = tankman.newSkillCount
    if lastNewSkillLevel != MAX_SKILL_LEVEL:
        count = max(count - 1, 0)
    start = len(tankman.skills)
    end = start + count
    for j in xrange(start, end):
        model.skills.addViewModel(_createSkill(j, '', False, False))

    return


def getSlotPriceData(slotIndex, detInvID, itemsCache=None):
    if itemsCache is None:
        itemsCache = dependency.instance(IItemsCache)
    actualExpandMoney = getDetachmentVehicleSlotMoney(detInvID, slotIndex, default=False)
    currency = actualExpandMoney.getCurrency(byWeight=True)
    money = itemsCache.items.stats.money.get(currency)
    actualPrice = actualExpandMoney.get(currency)
    isEnoughActual = actualPrice <= money
    defaultExpandMoney = getDetachmentVehicleSlotMoney(detInvID, slotIndex, default=True)
    if defaultExpandMoney is not None:
        defaultPrice = defaultExpandMoney.get(currency)
        isEnoughDefault = defaultPrice <= money
        hasDiscount = actualPrice < defaultPrice
        return {'hasDiscount': hasDiscount,
         'isEnoughActual': isEnoughActual,
         'currency': currency,
         'actualPrice': actualPrice,
         'isEnoughDefault': isEnoughDefault,
         'defaultPrice': defaultPrice,
         'shortage': actualPrice - money}
    else:
        return {'hasDiscount': False,
         'isEnoughActual': isEnoughActual,
         'currency': currency,
         'actualPrice': actualPrice,
         'shortage': actualPrice - money}


def fillVehicleSlotPriceModel(model, slotIndex, detInvID, itemsCache=None):
    priceData = getSlotPriceData(slotIndex, detInvID, itemsCache)
    model.setValue(int(priceData['actualPrice']))
    model.setIsEnough(priceData['isEnoughActual'])
    model.setType(priceData['currency'])
    model.setHasDiscount(priceData['hasDiscount'])


def getDetachmentPriceGroups(default):
    itemsCache = dependency.instance(IItemsCache)
    return itemsCache.items.shop.defaults.detachmentPriceGroups if default else itemsCache.items.shop.detachmentPriceGroups


def getPriceGroupByDetachmentInvID(detachmentInvID):
    detachmentCache = dependency.instance(IDetachmentCache)
    detachment = detachmentCache.getDetachment(detachmentInvID)
    return detachment.progression.priceGroup


def getDetachmentVehicleSlotMoney(detachmentInvID, slotIndex, default):
    priceGroups = getDetachmentPriceGroups(default)
    if priceGroups is None:
        return
    else:
        detPriceGroup = getPriceGroupByDetachmentInvID(detachmentInvID)
        vehSlotPrices = priceGroups[detPriceGroup][DetachmentOperations.UNLOCK_VEHICLE_SLOT]
        slotIndex += 1
        return Money(**vehSlotPrices[slotIndex])


def getSpecializeOption(detachmentInvID, specializeOptionID, default=False):
    priceGroups = getDetachmentPriceGroups(default)
    if priceGroups is None:
        return
    else:
        detPriceGroup = getPriceGroupByDetachmentInvID(detachmentInvID)
        specOption = priceGroups[detPriceGroup][DetachmentOperations.SPECIALIZE_VEHICLE_SLOT]
        return specOption[specializeOptionID]


def getSpecializeOptionMoney(detachment, specOptionDict, paymentOptionID, useLevelDiscount=True):
    money = Money(**specOptionDict)
    currency = money.getCurrency(byWeight=True)
    price = money.get(currency)
    if useLevelDiscount:
        paymentType = SPECIALIZATION_PAYMENT_OPTION_TO_TYPE[paymentOptionID]
        xp = detachment.experience
        progrSpecOption = detachment.progression.getSpecializationOptionByXP(paymentType, xp)
        progressionDiscountMult = 1.0 - float(progrSpecOption.discount) / 100
        price *= progressionDiscountMult
    return (currency, int(price))


def getDetachmentRestorePrice(detachmentInvID, specialTerm, default=False):
    priceGroups = getDetachmentPriceGroups(default) or getDetachmentPriceGroups(False)
    detPriceGroup = getPriceGroupByDetachmentInvID(detachmentInvID)
    restorePrice = priceGroups[detPriceGroup][DetachmentOperations.RESTORE][specialTerm]
    return Money(**restorePrice)


@dependency.replace_none_kwargs(detachmentCache=IDetachmentCache)
def getDropSkillsPrice(detInvID, detachmentCache=None):
    detachment = detachmentCache.getDetachment(detInvID)
    priceGroup = detachment.progression.priceGroup
    currentPriceGroup = getDetachmentPriceGroups(False)
    defaultPriceGroup = getDetachmentPriceGroups(True) or currentPriceGroup
    defaultPrices = defaultPriceGroup[priceGroup][DetachmentOperations.DROP_SKILL]
    currentPrices = currentPriceGroup[priceGroup][DetachmentOperations.DROP_SKILL]
    progressionOption = detachment.progression.getDropSkillDiscountByXP(detachment.experience)
    progressionDiscount = progressionOption.discount
    isFirstDrop = detachment.dropSkillDiscounted
    detDescr = detachment.getDescriptor()
    if isFirstDrop and progressionOption.firstDropEnable:
        paymentOption = DropSkillPaymentOption.FIRST
    else:
        paymentOption = DropSkillPaymentOption.NEXT if detDescr.getDropSkillPaymentOption()[1] == DropSkillPaymentOption.NEXT else DropSkillPaymentOption.DEFAULT
    defaultDropCost = Money(**defaultPrices[DropSkillPaymentOption.DEFAULT]) if isFirstDrop else Money(**defaultPrices[paymentOption])
    currentDropCost = Money(**currentPrices[paymentOption])
    if paymentOption != DropSkillPaymentOption.FIRST and progressionDiscount:
        currentDropCost -= currentDropCost * progressionDiscount / 100
    return (isFirstDrop, currentDropCost, defaultDropCost)


@dependency.replace_none_kwargs(detachmentCache=IDetachmentCache)
def getFirstDropSkillsPrice(detInvID, detachmentCache=None):
    detachment = detachmentCache.getDetachment(detInvID)
    priceGroup = detachment.progression.priceGroup
    currentPriceGroup = getDetachmentPriceGroups(False)
    defaultPriceGroup = getDetachmentPriceGroups(True) or currentPriceGroup
    defaultPrices = defaultPriceGroup[priceGroup][DetachmentOperations.DROP_SKILL]
    currentPrices = currentPriceGroup[priceGroup][DetachmentOperations.DROP_SKILL]
    defaultDropCost = Money(**defaultPrices[DropSkillPaymentOption.DEFAULT])
    currentDropCost = Money(**currentPrices[DropSkillPaymentOption.FIRST])
    currency = currentDropCost.getCurrency()
    discountPercent = int(round(100 * (1.0 - float(currentDropCost.get(currency)) / defaultDropCost.get(currency)))) if currentDropCost.get(currency) else 100
    return (currentDropCost, discountPercent)


def hasCrewTrainedForVehicle(vehicleCD):
    items = dependency.instance(IItemsCache).items
    vehicle = items.getItemByCD(vehicleCD)
    vehDetInvID = vehicle.getLinkedDetachmentID()
    if vehDetInvID != NO_DETACHMENT_ID:
        return True
    detachmentCache = dependency.instance(IDetachmentCache)
    detachments = detachmentCache.getDetachments()
    return any((det.canUseVehicle(vehicleCD) for det in detachments.itervalues()))


def getVisibleCrewWidgetName():
    if not g_currentVehicle.isPresent():
        return ''
    return HANGAR_ALIASES.CREW if g_currentVehicle.hasOldCrew() else HANGAR_ALIASES.DETACHMENT_WIDGET


def getBestDetachmentForVehicle(vehicle):
    detachmentCache = dependency.instance(IDetachmentCache)
    criteria = REQ_CRITERIA.DETACHMENT.NATIONS([vehicle.nationID]) | ~REQ_CRITERIA.DETACHMENT.DEMOBILIZE
    detachments = [ det for det in detachmentCache.getDetachments(criteria=criteria).itervalues() if canAssignDetachmentToVehicle(det, vehicle) == CanAssignResult.OK ]
    return max(detachments, key=lambda d: (d.level, d.currentXPProgress)) if detachments else None


def getRecruitsForMobilization(vehicle, vehTypes=None):
    criteria = REQ_CRITERIA.TANKMAN.ACTIVE | REQ_CRITERIA.NATIONS([vehicle.nationID])
    if vehTypes:
        criteria |= REQ_CRITERIA.TANKMAN.NATIVE_VEH_TYPE(vehTypes)
    itemsCache = dependency.instance(IItemsCache)
    recruits = itemsCache.items.getTankmen(criteria)
    return removeUnsuitableRecruits(recruits, vehicle)


def removeUnsuitableRecruits(recruits, vehicle):
    vehicleCriteria = REQ_CRITERIA.EMPTY
    if not vehicle.isOnlyForBattleRoyaleBattles:
        vehicleCriteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
    if not vehicle.isOnlyForEventBattles:
        vehicleCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    if not vehicle.isCrewLocked:
        vehicleCriteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
    itemsCache = dependency.instance(IItemsCache)
    suitableRecruits = itemsCache.items.removeUnsuitableTankmen(recruits.itervalues(), vehicleCriteria)
    return suitableRecruits
