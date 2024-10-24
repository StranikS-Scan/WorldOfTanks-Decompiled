# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/model_setters.py
from typing import TYPE_CHECKING
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_tankman_skill_model import CrewWidgetTankmanSkillModel, SkillType
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanCardState, TankmanRole, TankmanLocation, TankmanKind
from gui.impl.lobby.crew.crew_helpers.skill_helpers import isTmanSkillIrrelevant, getTmanNewSkillCount
from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog_utils import getIconBackground
from helpers import dependency, time_utils
from items.tankmen import MAX_SKILL_LEVEL
from skeletons.gui.shared import IItemsCache
from skill_formatters import SkillLvlFormatter
if TYPE_CHECKING:
    from gui.shared.gui_items.Tankman import Tankman

def setTankmanModel(tm, tman, tmanNativeVeh, tmanVeh=None, compVeh=None, requiredRole=None):
    if tman is None:
        return
    else:
        tdescr = tman.descriptor
        tm.setTankmanID(tman.invID)
        tm.setIconName(tman.getExtensionLessIconWithSkin())
        tm.setRole(TankmanRole(tdescr.role))
        tm.setFullUserName(tman.getFullUserNameWithSkin())
        tm.setTankmanKind(TankmanKind.TANKMAN)
        tm.setSpecializationLevel(tdescr.roleLevel)
        tm.setHasSpecializationLevelPenalty(False)
        if compVeh:
            if compVeh.isWotPlus or requiredRole != tdescr.role and requiredRole is not None:
                tm.setHasSpecializationLevelPenalty(False)
            else:
                tm.setHasSpecializationLevelPenalty(compVeh.compactDescr != tmanNativeVeh.compactDescr and not (compVeh.isPremium and tmanNativeVeh.type == compVeh.type))
        tm.setIsInSkin(tman.isInSkin)
        tm.setLocation(TankmanLocation.DISMISSED if tman.isDismissed else (TankmanLocation.INTANK if tman.isInTank else TankmanLocation.INBARRACKS))
        tm.setIsMainActionDisabled(tman.isLockedByVehicle())
        newSkillsCount, lastNewSkillLvl = getTmanNewSkillCount(tman)
        lastSkillLvl = CrewConstants.DONT_SHOW_LEVEL
        if newSkillsCount > 0:
            lastSkillLvl = lastNewSkillLvl.intSkillLvl
        elif tman.earnedSkillsCount > 0:
            lastSkillLvl = tdescr.lastSkillLevel
        tm.setLastSkillLevel(lastSkillLvl)
        if tmanVeh:
            if tmanVeh.isInBattle or tmanVeh.isDisabled or tmanVeh.isInPrebattle:
                tm.setCardState(TankmanCardState.DISABLED)
            if tmanVeh.isInBattle or tmanVeh.isDisabled:
                tm.setDisableIcon(R.images.gui.maps.icons.vehicleStates.battle())
                tm.setDisableReason(R.strings.crew.common.inBattle())
            elif tmanVeh.isInPrebattle:
                tm.setDisableIcon(R.images.gui.maps.icons.vehicleStates.inPrebattle())
                tm.setDisableReason(R.strings.crew.common.inPrebattle())
            fillVehicleInfo(tm.vehicleInfo, tmanVeh)
        if tmanNativeVeh:
            fillVehicleInfo(tm.tankmanVehicleInfo, tmanNativeVeh, separateIGRTag=True)
        return


def setFreeSkillsToTmanModel(sm, tman):
    for skill in tman.freeSkills:
        sm.addViewModel(getCrewWidgetTmanSkillModel(tman, skill))


def setRecruiteFreeSkillsToTmanModel(sm, tman, wrapper):
    for skill in tman.freeSkills:
        sm.addViewModel(getCrewWidgetTmanSkillModel(tman, wrapper(skill.name, skillLevel=skill.level), isFreeSkill=True))


def setSkillsToTmanModel(sm, tman, useOnlyFull=False):
    notFullEarnedSkillMdl = None
    for skill in tman.earnedSkills:
        skillMdl = getCrewWidgetTmanSkillModel(tman, skill, useOnlyFull)
        if skill.isMaxLevel:
            sm.addViewModel(skillMdl)
        notFullEarnedSkillMdl = skillMdl

    for _ in xrange(tman.newFreeSkillsCount):
        sm.addViewModel(getCrewWidgetTmanSkillModel(tman))

    if notFullEarnedSkillMdl:
        sm.addViewModel(notFullEarnedSkillMdl)
    else:
        newSkillsCount, _ = getTmanNewSkillCount(tman, useOnlyFull)
        for _ in xrange(newSkillsCount):
            sm.addViewModel(getCrewWidgetTmanSkillModel(tman))

    return


def setTmanSkillsModel(sm, tman, useOnlyFull=False):
    setFreeSkillsToTmanModel(sm, tman)
    setSkillsToTmanModel(sm, tman, useOnlyFull)


def getCrewWidgetTmanSkillModel(tman, skill=None, isFreeSkill=False):
    tsm = CrewWidgetTankmanSkillModel()
    if skill is None:
        tsm.setType(SkillType.NEW)
        return tsm
    else:
        tsm.setName(skill.name)
        tsm.setIcon(skill.extensionLessIconName)
        tsm.setType(SkillType.IRRELEVANT if not isFreeSkill and isTmanSkillIrrelevant(tman, skill) else (SkillType.LEARNED if skill.isMaxLevel else (SkillType.LEARNING if skill.level < MAX_SKILL_LEVEL else SkillType.LEARNED)))
        return tsm


def setReplacedTankmanModel(tm, tman, tmanNativeVeh):
    if tman is None:
        return
    else:
        tm.setFullUserName(tman.getFullUserNameWithSkin())
        tm.setRole(TankmanRole(tman.role))
        if tmanNativeVeh:
            tm.tankmanVehicleInfo.setVehicleName(tmanNativeVeh.descriptor.type.userString)
        return


def setRecruitTankmanModel(tm, recruitInfo):
    tm.setRecruitID(str(recruitInfo.getRecruitID()))
    if len(recruitInfo.getRoles()) > 1:
        tm.setRole(TankmanRole.ANY)
    elif recruitInfo.getRoles():
        tm.setRole(TankmanRole(recruitInfo.getRoles()[0]))
    tm.setFullUserName(recruitInfo.getFullUserName())
    iconName = recruitInfo.getDynIconName()
    tm.setIconName(iconName)
    tm.setRecruitGlowImage(getIconBackground(recruitInfo.getSourceID(), iconName))
    tm.setTankmanKind(TankmanKind.RECRUIT)
    tm.setHasVoiceover(bool(recruitInfo.getSpecialVoiceTag()))
    tman = recruitInfo.getFakeTankman()
    tm.setSpecializationLevel(tman.roleLevel)
    tankmanSkill = recruitInfo.getTankmanSkill()
    skills = tm.getSkills()
    setRecruiteFreeSkillsToTmanModel(skills, tman, tankmanSkill)
    setSkillsToTmanModel(skills, tman, useOnlyFull=True)
    newSkillsCount, lastSkillLevel = getTmanNewSkillCount(tman, useOnlyFull=True)
    if tman.earnedSkillsCount + newSkillsCount <= 0:
        lastSkillLevel = SkillLvlFormatter()
    tm.setLastSkillLevel(lastSkillLevel.intSkillLvl)
    tm.setLocation(TankmanLocation.INBARRACKS)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def setTankmanRestoreInfo(vm, itemsCache=None):
    tankmenRestoreConfig = itemsCache.items.shop.tankmenRestoreConfig
    freeDays = tankmenRestoreConfig.freeDuration / time_utils.ONE_DAY
    billableDays = tankmenRestoreConfig.billableDuration / time_utils.ONE_DAY - freeDays
    restoreCost = tankmenRestoreConfig.cost
    restoreLimit = tankmenRestoreConfig.limit
    vm.setFreePeriod(freeDays)
    vm.setPaidPeriod(billableDays)
    vm.setRecoverPrice(restoreCost.get(restoreCost.getCurrency(), 0))
    vm.setMembersBuffer(restoreLimit)
