# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/detachment.py
import typing
from constants import VEHICLE_CLASSES
from debug_utils import LOG_WARNING
from gui.shared.gui_items.gui_item import GUIItem, HasStrCD
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from helpers import i18n
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE
from items import ITEM_TYPE_NAMES, detachment_customization
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.components.detachment_components import PerkBonusApplier
from items.components.detachment_constants import DetachmentSlotType, DropSkillPaymentOption, DetachmentLockMaskBits, NO_DETACHMENT_ID, RewardTypes
from items.detachment import DetachmentDescr
from crew2 import settings_globals
from crew2.crew2_consts import BOOL_TO_GENDER, GENDER
from skeletons.gui.lobby_context import ILobbyContext
from nations import NAMES
from skeletons.gui.detachment import IDetachmentCache, IDetachementStates
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from gui.shared.gui_items.instructor import Instructor
    from gui.shared.gui_items.Vehicle import Vehicle
    from items.components.detachment_components import PerkApplyItem

class InstructorsInfluenceOnPerk(object):
    __slots__ = ('instructor', 'points', 'overcap')

    def __init__(self, instructor, points, overcap):
        self.instructor = instructor
        self.points = points
        self.overcap = overcap


class Detachment(GUIItem):
    __slots__ = ('__descriptor', '_skinID', '_invID', '_vehInvID', '_crewImageName', '_itemTypeID', '_itemTypeName', '_expDate', '_cmdrPortraitIconName', '_cmdrPortrait', '_cmdrFirstName', '_cmdrSecondName')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __detachmentsStates = dependency.descriptor(IDetachementStates)

    def __init__(self, strCompactDescr, proxy=None, invID=NO_DETACHMENT_ID, vehInvID=-1, skinID=NO_CREW_SKIN_ID):
        super(Detachment, self).__init__(strCD=HasStrCD(strCompactDescr))
        self.__descriptor = None
        self._invID = invID
        self._vehInvID = vehInvID
        self._crewImageName = self.__getCrewImageName()
        self._itemTypeID = GUI_ITEM_TYPE.DETACHMENT
        self._itemTypeName = ITEM_TYPE_NAMES[self.itemTypeID]
        self._skinID = skinID
        if proxy is not None and proxy.inventory.isSynced():
            if self._skinID == NO_CREW_SKIN_ID:
                self._skinID = proxy.inventory.getEquippedCrewSkinID(invID)
            self._expDate = self.__detachmentsStates.states.getDetachmentExpDate(self._invID)
        else:
            self._expDate = None
        self._cmdrFirstName = self._getCmdrFirstName()
        self._cmdrSecondName = self._getCmdrSecondName()
        self._cmdrPortraitIconName = self._getCmdrPortraitIconName()
        self._cmdrPortrait = self._getCmdrPortrait()
        return

    def getDescriptor(self):
        if self.__descriptor is None:
            self.__descriptor = DetachmentDescr.createByCompDescr(self.strCD)
        return self.__descriptor

    @property
    def build(self):
        return self.getDescriptor().build

    @property
    def autoPerks(self):
        return self.getDescriptor().autoPerks

    @property
    def perksMatrix(self):
        return self.getDescriptor().getPerksMatrix()

    @property
    def invID(self):
        return self._invID

    @property
    def nationID(self):
        return self.getDescriptor().nationID

    @property
    def skinID(self):
        return self._skinID

    @property
    def hasSkin(self):
        return self._skinID != NO_CREW_SKIN_ID

    @property
    def vehInvID(self):
        return self._vehInvID

    @property
    def isInTank(self):
        return self._vehInvID > 0

    @property
    def isInRecycleBin(self):
        return bool(self._expDate)

    @property
    def expDate(self):
        return self._expDate

    @property
    def cmdrGender(self):
        return BOOL_TO_GENDER[self.getDescriptor().isFemale]

    @property
    def rankRecord(self):
        rank = self.getDescriptor().rank
        return settings_globals.g_commanderSettings.ranks.getRankRecord(self.nationID, rank)

    @property
    def levelIconID(self):
        return self.getDescriptor().levelIcon

    @property
    def nextLevelIconID(self):
        return self.progression.getLevelIconByXP(self.progression.getLevelStartingXP(self.rawLevel + 1))

    @property
    def rawLevel(self):
        return self.getDescriptor().rawLevel

    @property
    def level(self):
        return self.getDescriptor().level

    @property
    def freePoints(self):
        detDescr = self.getDescriptor()
        return detDescr.level - detDescr.getBuildLevel()

    @property
    def masteryLevel(self):
        return self.getDescriptor().masteryLevel

    @property
    def masteryName(self):
        progression = R.strings.detachment.progressionLevel
        masteryName = progression.commanderUnique() if self.uniqueCmdrIcon else progression.commander()
        return masteryName if not self.hasMaxLevel else progression.elite.num(self.masteryLevel)()

    @property
    def eliteTitle(self):
        return R.strings.detachment.eliteLevel.num(self.masteryLevel)() if self.hasMaxLevel else R.invalid()

    @property
    def hasMaxLevel(self):
        return self.getDescriptor().hasMaxLevel

    @property
    def hasMaxMasteryLevel(self):
        return self.getDescriptor().hasMaxMasteryLevel

    @property
    def badgeID(self):
        return self.getDescriptor().progression.badgeID

    @property
    def itemTypeID(self):
        return self._itemTypeID

    @property
    def itemTypeName(self):
        return self._itemTypeName

    @property
    def canCustomizeCommander(self):
        return not self.getDescriptor().getLockMaskBit(DetachmentLockMaskBits.COMMANDER_CUSTOMIZATION)

    @property
    def cmdrPortraitIconName(self):
        return self._cmdrPortraitIconName

    def _getCmdrPortraitIconName(self):
        unique = self.uniqueCmdrIcon
        if unique is not None:
            return unique
        elif self.hasSkin:
            return detachment_customization.g_cache.crewSkins().skins[self._skinID].iconID
        else:
            nationID = self.nationID
            cmdrPortraitID = self.getDescriptor().cmdrPortraitID
            gender = self.cmdrGender
            portrait = settings_globals.g_characterProperties.getPortraitByID(nationID, cmdrPortraitID, gender)
            return portrait

    @property
    def cmdrPortrait(self):
        return self._cmdrPortrait

    def getPerks(self, bonusPerks=None, vehicle=None, comparableInstructors=None, history=None):
        states = self.__detachmentsStates.states
        bonusCollection = []
        states.collectInstructorBonuses(bonusCollection, self.getDescriptor(), comparableInstructors or [])
        if vehicle:
            bonusCollection.extend(vehicle.battleBoosters.collectPerkBonuses())
        else:
            states.collectBoosterBonuses(bonusCollection, self.vehInvID)
        return states.getAbilitiesFromCollection(self.invID, bonusCollection, bonusPerks, history)

    def getPerksBoosterInfluence(self, bonusPerks=None, vehicle=None, comparableInstructors=None):
        return self._getPerksInfluence([PerkBonusApplier.BOOSTER], bonusPerks, vehicle, comparableInstructors)

    def getPerksInstructorInfluence(self, bonusPerks=None, vehicle=None, comparableInstructors=None):
        return self._getPerksInfluence([PerkBonusApplier.INSTRUCTOR], bonusPerks, vehicle, comparableInstructors)

    def getPerksInstructorByIDInfluence(self, instrInvID, bonusPerks=None, vehicle=None, comparableInstructors=None):
        perksInfluence = self._getPerksInfluence([PerkBonusApplier.INSTRUCTOR], bonusPerks, vehicle, comparableInstructors)
        return [ (perkID, points, overcaps) for instrID, perkID, points, overcaps in perksInfluence if instrID == instrInvID ]

    def getPerkBoosterInfluence(self, perkID, bonusPerks=None, vehicle=None, comparableInstructors=None):
        return self._getPerkInfluence(perkID, [PerkBonusApplier.BOOSTER], bonusPerks, vehicle, comparableInstructors)

    def getPerkInstructorInfluence(self, perkID, bonusPerks=None, vehicle=None, comparableInstructors=None):
        return self._getPerkInfluence(perkID, [PerkBonusApplier.INSTRUCTOR], bonusPerks, vehicle, comparableInstructors)

    def _getPerksInfluence(self, applierTypes, bonusPerks, vehicle, comparableInstructors=None):
        history = []
        self.getPerks(bonusPerks, vehicle, comparableInstructors, history)
        return [ (item.id,
         item.perkID,
         item.bonus,
         item.overcap) for item in history if item.type in applierTypes ]

    def _getPerkInfluence(self, perkID, applierTypes, bonusPerks, vehicle, comparableInstructors=None):
        history = []
        self.getPerks(bonusPerks, vehicle, comparableInstructors, history)
        return [ (item.id, item.bonus, item.overcap) for item in history if item.type in applierTypes and item.perkID == perkID ]

    def _getCmdrPortrait(self):
        portraitName = self._cmdrPortraitIconName
        missingUniqueIcon = False
        missingTrueCommanderIcon = False
        missingTrueSkinIcon = False
        if self.uniqueCmdrIcon is not None:
            portraitR = R.images.gui.maps.icons.commanders.unique.c_260x220.dyn(portraitName)
            if portraitR.exists():
                return portraitR()
            missingUniqueIcon = True
        elif self.hasSkin:
            portraitR = R.images.gui.maps.icons.commanders.c_290x300.crewSkins.dyn(portraitName)
            if portraitR.exists():
                return portraitR()
            missingTrueSkinIcon = True
            portraitR = R.images.gui.maps.icons.tankmen.icons.big.crewSkins.dyn(portraitName)
        else:
            portraitR = R.images.gui.maps.icons.commanders.c_290x300.dyn(portraitName)
            if portraitR.exists():
                return portraitR()
            missingTrueCommanderIcon = True
            portraitR = R.images.gui.maps.icons.tankmen.icons.big.dyn(portraitName)
        if portraitR.exists():
            if missingTrueCommanderIcon:
                LOG_WARNING('Commander icon "{}" substituted with tankman icon'.format(portraitName))
            elif missingTrueSkinIcon:
                LOG_WARNING('Commander skin icon "{}" substituted with tankman skin icon'.format(portraitName))
            return portraitR()
        else:
            if missingUniqueIcon:
                LOG_WARNING('Unique detachment icon "{}" not found'.format(portraitName))
            elif missingTrueCommanderIcon:
                LOG_WARNING('Commander icon "{}" not found'.format(portraitName))
            elif missingTrueSkinIcon:
                LOG_WARNING('Commander skin icon "{}" not found'.format(portraitName))
            return R.images.gui.maps.icons.instructors.c_290x300.siluet_man() if self.cmdrGender == GENDER.MALE else R.images.gui.maps.icons.instructors.c_290x300.siluet_woman()

    @property
    def cmdrFirstName(self):
        return self._cmdrFirstName

    def _getCmdrFirstName(self):
        nationID = self.nationID
        if self.hasSkin:
            return backport.textRes(detachment_customization.g_cache.crewSkins().skins[self._skinID].firstNameID)()
        firstNameID = self.getDescriptor().cmdrFirstNameID
        gender = self.cmdrGender
        firstNameKey = settings_globals.g_characterProperties.getFirstNameByID(nationID, firstNameID, gender)
        return backport.textRes(firstNameKey)()

    @property
    def cmdrSecondName(self):
        return self._cmdrSecondName

    def _getCmdrSecondName(self):
        if self.hasSkin:
            return backport.textRes(detachment_customization.g_cache.crewSkins().skins[self._skinID].lastNameID)()
        nationID = self.nationID
        secondNameID = self.getDescriptor().cmdrSecondNameID
        gender = self.cmdrGender
        secondNameKey = settings_globals.g_characterProperties.getSecondNameByID(nationID, secondNameID, gender)
        return backport.textRes(secondNameKey)()

    @property
    def leaderName(self):
        return ' '.join((name for name in map(backport.text, (self._cmdrFirstName, self._cmdrSecondName)) if name))

    @property
    def crewName(self):
        presets = settings_globals.g_detachmentSettings.presets
        preset = presets.getDetachmentPresetByID(self.getDescriptor().presetID)
        dynAccessor = R.strings.detachment.presetName.dyn(preset.name)
        return backport.text(dynAccessor()) if dynAccessor else ''

    @property
    def cmdrFullName(self):
        crewName = self.crewName
        return crewName if crewName else self.leaderName

    @property
    def crewImage(self):
        imageR = R.images.gui.maps.icons.commanders.members.c_440x220.dyn(self._crewImageName)
        return imageR() if imageR.exists() else R.images.gui.maps.icons.detachment.crew.crew_members_dark()

    def __getCrewImageName(self):
        preset = settings_globals.g_detachmentSettings.presets.getDetachmentPresetByID(self.getDescriptor().presetID)
        return self.nationName if preset is None else preset.image or self.nationName

    @property
    def uniqueCmdrIcon(self):
        preset = settings_globals.g_detachmentSettings.presets.getDetachmentPresetByID(self.getDescriptor().presetID)
        return preset.image if preset is not None else None

    @property
    def rankName(self):
        fullRankName = self.rankRecord.name
        return i18n.makeString(fullRankName)

    @property
    def rankIconName(self):
        rankIcon = self.rankRecord.icon
        rankIcon = rankIcon.replace('-', '_')
        rankIcon = rankIcon.split('.')[0]
        return rankIcon

    @property
    def rankIcon(self):
        return R.images.gui.maps.icons.detachment.ranks.c_95x60.dyn(self.rankIconName)()

    @property
    def experience(self):
        return self.getDescriptor().experience

    @property
    def currentXPProgress(self):
        return self.getDescriptor().getCurrentLevelXPProgress()

    @property
    def classID(self):
        return self.getDescriptor().classID

    @property
    def classType(self):
        return VEHICLE_CLASSES[self.classID]

    @property
    def classTypeUnderscore(self):
        return replaceHyphenToUnderscore(self.classType)

    @property
    def nationName(self):
        return NAMES[self.nationID]

    @property
    def progression(self):
        return self.getDescriptor().progression

    def getInstructorsIDs(self, skipNone=False, skipDuplicated=False):
        return list(self.getDescriptor().iterSlots(DetachmentSlotType.INSTRUCTORS, skipNone=skipNone, skipDuplicated=skipDuplicated))

    def getMaxInstructorsCount(self):
        return self.getDescriptor().maxInstructorsCount

    def getVehicleCDs(self):
        return list(self.vehicleSlots)

    def canUseVehicle(self, vehicleCD):
        return vehicleCD in self.vehicleSlots

    @property
    def vehicleSlots(self):
        return self.getDescriptor().iterSlots(DetachmentSlotType.VEHICLES)

    @property
    def maxVehicleSlots(self):
        return self.getDescriptor().maxVehicleSlots

    @property
    def vehicleSlotsCount(self):
        return self.getDescriptor().getSlotsCount(DetachmentSlotType.VEHICLES)

    @property
    def instructorSlotsCount(self):
        return self.getDescriptor().getSlotsCount(DetachmentSlotType.INSTRUCTORS)

    @property
    def dropSkillPaymentOption(self):
        return self.getDescriptor().getDropSkillPaymentOption()[1]

    @property
    def dropSkillDiscounted(self):
        return self.getDescriptor().getDropSkillPaymentOption()[1] != DropSkillPaymentOption.DEFAULT

    @property
    def isGarbage(self):
        return self.getDescriptor().isGarbage

    @property
    def isCrewLocked(self):
        vehicle = self.__itemsCache.items.getVehicle(self.vehInvID)
        return vehicle and vehicle.isCrewLocked

    @property
    def isRestorable(self):
        return not (self.isGarbage or self.isCrewLocked)

    def getDetachmentFlagIcon(self):
        return backport.image(R.images.gui.maps.icons.detachment.main.nation.dyn(self.nationName)())

    def getInstructorUnlockLevels(self):
        return self.getDescriptor().progression.instructorUnlockLevels

    def getVehicleSlotUnlockLevels(self):
        return self.getDescriptor().progression.vehicleSlotUnlockLevels

    def isSellsDailyLimitReached(self):
        if not self.__lobbyContext.getServerSettings().isDetachmentSellsDailyLimitEnabled():
            return False
        return False if self.isGarbage else not self.__itemsCache.items.stats.detachmentSellsLeft

    def getRewardsDiff(self, oldDetachment, accountBadgeLevel=0):
        if oldDetachment:
            prevState = oldDetachment.getDescriptor().progressionState
        else:
            prevState = self.progression.getStateByXP(-1)
        rewards = self.getDescriptor().getProgressionRewards(prevState)
        if rewards[RewardTypes.BADGE_LEVEL] <= accountBadgeLevel:
            rewards[RewardTypes.BADGE_LEVEL] = None
        return rewards

    @property
    def currentRewards(self):
        emptyState = self.progression.getStateByXP(-1)
        return self.getDescriptor().getProgressionRewards(emptyState)

    @property
    def futureRewards(self):
        nextMilestoneXP = self.progression.getLevelStartingXP(self.nextMilestoneLevel)
        nextMilestoneState = self.progression.getStateByXP(nextMilestoneXP)
        return self.getDescriptor().getProgressionRewards(None, nextMilestoneState)

    @property
    def nextMilestoneLevel(self):
        return self.progression.getNextMilestoneLevel(self.rawLevel)

    @property
    def milestone(self):
        return self.progression.getMilestone(self.rawLevel)
