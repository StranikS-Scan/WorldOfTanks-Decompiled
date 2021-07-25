# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/detachment/progression_record.py
from bisect import bisect_right
from collections import OrderedDict, defaultdict
import typing
from crew2.settings_locator import Crew2Settings
from items import _xml
from items.components.detachment_constants import DetachmentMaxValues, CREW2_BADGE_IDS, SpecializationPaymentType
if typing.TYPE_CHECKING:
    import ResMgr
DiscountOption = typing.NamedTuple('DiscountOption', (('enable', bool), ('discount', int)))

class SpecializationOption(DiscountOption):
    pass


class DropSkillOption(object):
    __slots__ = ('discount', 'firstDropEnable', 'levelStart', 'levelEnd')

    def __init__(self, discount, firstDropEnable, levelStart, levelEnd):
        self.discount = discount
        self.firstDropEnable = firstDropEnable
        self.levelStart = levelStart
        self.levelEnd = levelEnd


ProgressionState = typing.NamedTuple('ProgressionState', (('level', int),
 ('rank', str),
 ('badgeLevel', int),
 ('autoPerks', dict),
 ('instructorSlots', int),
 ('vehicleSlots', int),
 ('schoolDiscount', typing.Optional[int]),
 ('academyDiscount', typing.Optional[int])))

class ProgressionRecord(object):
    __slots__ = ('_ID', '_priceGroupID', '_badgeID', '_levels', '_maxLevel', '_instructorUnlockLevels', '_vehicleSlotUnlockLevels', '_milestones', '_xpToRank', '_xpToBadgeLevel', '_xpToAutoPerks', '_xpToSpecializationOption', '_xpToDropSkillOption', '_xpToLevelIcon', '_firstPaidSpecializationLevel')

    def __init__(self, xmlCtx, section, settingsLocator):
        self._ID = None
        self._priceGroupID = None
        self._badgeID = None
        self._levels = []
        self._maxLevel = None
        self._instructorUnlockLevels = []
        self._vehicleSlotUnlockLevels = []
        self._milestones = []
        self._xpToRank = OrderedDict()
        self._xpToBadgeLevel = OrderedDict()
        self._xpToAutoPerks = defaultdict(OrderedDict)
        self._xpToSpecializationOption = defaultdict(OrderedDict)
        self._xpToDropSkillOption = OrderedDict()
        self._xpToLevelIcon = OrderedDict()
        self._load(xmlCtx, section, settingsLocator)
        self._firstPaidSpecializationLevel = self._findFirstPaidSpecializationLevel()
        self._validate(xmlCtx, settingsLocator)
        return

    def getRawLevelByXP(self, xp):
        return bisect_right(self._levels, xp)

    def getRankByXP(self, xp):
        return self._getValueByXP(self._xpToRank, xp)

    def getBadgeLevelByXP(self, xp):
        return self._getValueByXP(self._xpToBadgeLevel, xp, 0)

    def getLevelIconByXP(self, xp):
        return self._getValueByXP(self._xpToLevelIcon, xp)

    def getAutoPerksByXP(self, xp):
        perks = {}
        for perkID, xpToPerkLevel in self._xpToAutoPerks.iteritems():
            perkLevel = self._getValueByXP(xpToPerkLevel, xp)
            if perkLevel:
                perks[perkID] = perkLevel

        return perks

    def getSpecializationOptionByXP(self, paymentType, xp):
        defaultOption = SpecializationOption(False, 0)
        return self._getValueByXP(self._xpToSpecializationOption[paymentType], xp, defaultOption)

    def getSpecializationDiscountByXP(self, paymentType, xp):
        option = self.getSpecializationOptionByXP(paymentType, xp)
        return option.discount if option.enable else None

    def getDropSkillDiscountByXP(self, xp):
        return self._getValueByXP(self._xpToDropSkillOption, xp, DropSkillOption(0, False, 0, 0))

    def getStateByXP(self, xp):
        rawLevel = self.getRawLevelByXP(xp)
        return ProgressionState(level=min(rawLevel, self.maxLevel), rank=self.getRankByXP(xp), badgeLevel=self.getBadgeLevelByXP(xp), autoPerks=self.getAutoPerksByXP(xp), instructorSlots=bisect_right(self.instructorUnlockLevels, rawLevel), vehicleSlots=bisect_right(self.vehicleSlotUnlockLevels, rawLevel), schoolDiscount=self.getSpecializationDiscountByXP(SpecializationPaymentType.SILVER, xp), academyDiscount=self.getSpecializationDiscountByXP(SpecializationPaymentType.GOLD, xp))

    def getLevelStartingXP(self, rawLevel):
        return self._levels[rawLevel - 1] if 0 < rawLevel <= len(self._levels) else None

    def getMilestone(self, rawLevel):
        return bisect_right(self._milestones, rawLevel)

    def getNextMilestoneLevel(self, rawLevel):
        milestone = self.getMilestone(rawLevel)
        return self._milestones[milestone] if milestone < len(self._milestones) else 0

    @property
    def ID(self):
        return self._ID

    @property
    def priceGroup(self):
        return self._priceGroupID

    @property
    def badgeID(self):
        return self._badgeID

    @property
    def maxLevel(self):
        return self._maxLevel

    @property
    def maxMasteryLevel(self):
        return len(self._levels) - self._maxLevel

    @property
    def instructorUnlockLevels(self):
        return self._instructorUnlockLevels

    @property
    def vehicleSlotUnlockLevels(self):
        return self._vehicleSlotUnlockLevels

    @property
    def firstPaidSpecializationLevel(self):
        return self._firstPaidSpecializationLevel

    @staticmethod
    def _getValueByXP(xpToValue, xp, default=None):
        xpSteps = xpToValue.keys()
        i = bisect_right(xpSteps, xp)
        return xpToValue[xpSteps[i - 1]] if i > 0 else default

    def _load(self, xmlCtx, section, settingsLocator):
        self._ID = _xml.readInt(xmlCtx, section, 'id', 1, DetachmentMaxValues.PROGRESSION_ID)
        layoutCtx = (xmlCtx, 'layout[id={}]'.format(self._ID))
        self._priceGroupID = _xml.readPositiveInt(layoutCtx, section, 'priceGroupID')
        self._badgeID = _xml.readIntOrNone(layoutCtx, section, 'badgeID')
        prevXPForDropSkill = 0
        levelsSection = _xml.getSubsection(layoutCtx, section, 'levels')
        for levelSection in levelsSection.values():
            xp = _xml.readInt(layoutCtx, levelSection, 'xp')
            self._levels.append(xp)
            level = len(self._levels)
            levelCtx = (layoutCtx, 'level[xp={}]'.format(xp))
            if _xml.readBool(levelCtx, levelSection, 'milestone', False):
                self._milestones.append(level)
            maxLevel = _xml.readIntOrNone(levelCtx, levelSection, 'maxLevel')
            if maxLevel:
                if self._maxLevel:
                    _xml.raiseWrongXml(levelCtx, '', 'Progression must have exact one maxLevel')
                if maxLevel != level:
                    _xml.raiseWrongXml(levelCtx, '', 'Invalid maxLevel ({} != {})'.format(maxLevel, level))
                self._maxLevel = level
            instructorSlots = _xml.readIntOrNone(levelCtx, levelSection, 'instructorSlots')
            if instructorSlots:
                self._instructorUnlockLevels.extend([level] * instructorSlots)
            vehicleSlots = _xml.readIntOrNone(levelCtx, levelSection, 'vehicleSlots')
            if vehicleSlots:
                self._vehicleSlotUnlockLevels.extend([level] * vehicleSlots)
            rank = _xml.readStringOrNone(levelCtx, levelSection, 'rank')
            if rank:
                if not settingsLocator.commanderSettings.ranks.isValidRank(rank):
                    _xml.raiseWrongXml(levelCtx, '', 'Invalid rank {}'.format(rank))
                self._xpToRank[xp] = rank
            badgeLevel = _xml.readIntOrNone(levelCtx, levelSection, 'badgeLevel')
            if badgeLevel:
                self._xpToBadgeLevel[xp] = badgeLevel
            levelIcon = _xml.readStringOrNone(levelCtx, levelSection, 'levelIcon')
            if levelIcon:
                self._xpToLevelIcon[xp] = levelIcon
            autoPerks = self._readAutoPerks(levelCtx, levelSection, 'autoPerks')
            for perkID, perkLevel in autoPerks.iteritems():
                self._xpToAutoPerks[perkID][xp] = perkLevel

            specializationOptions = self._readSpecializationOptions(levelCtx, levelSection)
            for paymentType, option in specializationOptions.iteritems():
                self._xpToSpecializationOption[paymentType][xp] = option

            dropSkillOption = self._readDropSkill(levelCtx, levelSection)
            if dropSkillOption is not None:
                self._xpToDropSkillOption[xp] = dropSkillOption
                dropSkillOption.levelStart = level
                if prevXPForDropSkill in self._xpToDropSkillOption:
                    self._xpToDropSkillOption[prevXPForDropSkill].levelEnd = level - 1
                    prevXPForDropSkill = xp

        if prevXPForDropSkill:
            self._xpToDropSkillOption[prevXPForDropSkill].levelEnd = len(self._levels)
        return

    @staticmethod
    def _readAutoPerks(xmlCtx, section, subsectionName=''):
        perks = {}
        perksSection = section[subsectionName] or {}
        for perkSection in perksSection.values():
            perkID = _xml.readPositiveInt(xmlCtx, perkSection, 'id')
            perkLevel = _xml.readPositiveInt(xmlCtx, perkSection, 'level')
            perks[perkID] = perkLevel

        return perks

    @staticmethod
    def _readSpecializationOptions(xmlCtx, section, subsectionName=''):
        options = {}
        optionsSection = section[subsectionName] or {}
        for tagName, optionSection in optionsSection.items():
            if tagName == 'specializationPriceType':
                typeKey = _xml.readString(xmlCtx, optionSection, 'type').upper()
                paymentType = SpecializationPaymentType[typeKey].value
                if paymentType in options:
                    msg = 'specializationPriceOption {} is duplicated'
                    _xml.raiseWrongXml(xmlCtx, 'specializationPriceType', msg.format(paymentType))
                enable = _xml.readBool(xmlCtx, optionSection, 'enable')
                discount = _xml.readIntOrNone(xmlCtx, optionSection, 'discount') or 0
                options[paymentType] = SpecializationOption(enable, discount)

        return options

    @staticmethod
    def _readDropSkill(xmlCtx, section, subsectionName='', level=0):
        optionsSection = section[subsectionName] or {}
        for tagName, optionSection in optionsSection.items():
            if tagName == 'dropSkill':
                firstDropEnable = _xml.readBool(xmlCtx, optionSection, 'firstDropEnable')
                discount = _xml.readIntOrNone(xmlCtx, optionSection, 'discount') or 0
                return DropSkillOption(discount, firstDropEnable, 0, 0)

        return None

    def _validate(self, xmlCtx, settingsLocator):
        layoutCtx = (xmlCtx, 'layout[id={}]'.format(self._ID))
        self._validateLevels(layoutCtx)
        self._validateInstructors(layoutCtx, settingsLocator.detachmentSettings.maxInstructorSlots)
        self._validateAutoPerks(layoutCtx)
        self._validateBadge(layoutCtx)

    def _validateLevels(self, xmlCtx):
        if not self._levels or self._levels[0] != 0:
            _xml.raiseWrongXml(xmlCtx, '', 'Progression must start from XP 0')
        if not self._xpToRank.get(0):
            _xml.raiseWrongXml(xmlCtx, '', 'Progression must have a rank at XP 0')
        if not self._maxLevel:
            _xml.raiseWrongXml(xmlCtx, '', 'Progression must have exact one maxLevel')
        prevXP = -1
        for xp in self._levels:
            if xp <= prevXP:
                _xml.raiseWrongXml(xmlCtx, 'level[xp={}]'.format(xp), 'XP is not greater than previous value')
            prevXP = xp

    def _validateInstructors(self, xmlCtx, maxInstructorSlots):
        instructorSlots = len(self._instructorUnlockLevels)
        if instructorSlots > maxInstructorSlots:
            msg = 'Too much unlocked instructors ({} > {})'
            _xml.raiseWrongXml(xmlCtx, '', msg.format(instructorSlots, maxInstructorSlots))
        for level in self._instructorUnlockLevels:
            if level > self._maxLevel:
                msg = 'Instructor unlock level {} is greater than max level {}'
                _xml.raiseWrongXml(xmlCtx, '', msg.format(level, self._maxLevel))

    def _validateAutoPerks(self, xmlCtx):
        for perkID, xpToPerkLevel in self._xpToAutoPerks.iteritems():
            prevPerkLevel = 0
            for xp, perkLevel in xpToPerkLevel.iteritems():
                if perkLevel < prevPerkLevel:
                    msg = 'Auto-perk {} level {} is less than previous value'
                    _xml.raiseWrongXml(xmlCtx, 'level[xp={}]'.format(xp), msg.format(perkID, perkLevel))
                prevPerkLevel = perkLevel

    def _validateBadge(self, xmlCtx):
        if self._badgeID not in CREW2_BADGE_IDS:
            _xml.raiseWrongXml(xmlCtx, '', 'Invalid badgeID {}'.format(self._badgeID))
        prevBadgeLevel = 0
        for xp, badgeLevel in self._xpToBadgeLevel.iteritems():
            if badgeLevel < prevBadgeLevel:
                msg = 'badgeLevel {} is less than previous value'
                _xml.raiseWrongXml(xmlCtx, 'level[xp={}]'.format(xp), msg.format(badgeLevel))
            prevBadgeLevel = badgeLevel

    def _findFirstPaidSpecializationXP(self):
        for xpToOption in self._xpToSpecializationOption.itervalues():
            for xp, specOption in xpToOption.iteritems():
                if specOption.discount < 100:
                    return xp

        return None

    def _findFirstPaidSpecializationLevel(self):
        xp = self._findFirstPaidSpecializationXP()
        return None if xp is None else self.getRawLevelByXP(xp)
