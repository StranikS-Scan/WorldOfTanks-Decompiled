# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/rewards.py
import typing
from crew2 import settings_globals
from gui.impl.backport import textRes
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.new_level_rewards_constants import NewLevelRewardsConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.reward_model import RewardModel
from gui.shared.gui_items import KPI
from gui.shared.items_parameters.functions import buildKpiDict
from items.components.detachment_constants import RewardTypes
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment
TRAINING = 'training'
SCHOOL = 'school'
ACADEMY = 'academy'

class BaseReward(object):
    __slots__ = ('_detachment', '_isConversionProcess', '_rewardValue', '_model')
    _type = ''
    _icon = R.invalid()
    _value = 0
    _extraValue = ''
    _title = R.invalid()
    _extraTitle = R.invalid()

    def __init__(self, detachment, rewardValue, isConversionProcess=False):
        self._detachment = detachment
        self._isConversionProcess = isConversionProcess
        self._rewardValue = rewardValue
        self._model = None
        if self._isValidInput:
            self._initModel()
        return

    @property
    def model(self):
        if not self._isValidOutput:
            return None
        else:
            if not self._model:
                self._model = RewardModel()
                self._model.setType(self._type)
                self._model.setIcon(self._icon)
                self._model.setValue(self._value)
                self._model.setExtraValue(self._extraValue)
                self._model.setTitle(self._title)
                self._model.setExtraTitle(self._extraTitle)
            return self._model

    @property
    def _isValidInput(self):
        return bool(self._rewardValue)

    @property
    def _isValidOutput(self):
        return self._isValidInput

    def _initModel(self):
        pass


class RankReward(BaseReward):
    _type = NewLevelRewardsConstants.RANK

    def _initModel(self):
        nationID = self._detachment.nationID
        rank = self._rewardValue
        rankRecord = settings_globals.g_commanderSettings.ranks.getRankRecord(nationID, rank)
        rankIconName = rankRecord.icon.split('.')[0].replace('-', '_')
        self._icon = R.images.gui.maps.icons.detachment.ranks.c_80x80.dyn(rankIconName)()
        self._value = nationID
        self._extraValue = rank
        self._title = R.strings.detachment.levelBadgeTooltip.gradeLevel()
        self._extraTitle = textRes(rankRecord.name.replace('-', '_'))()


class BadgeReward(BaseReward):
    _type = NewLevelRewardsConstants.BADGE

    def _initModel(self):
        badgeID = self._detachment.badgeID
        badgeLevel = self._rewardValue
        badgeIcon = 'badge_{ID}_{level}'.format(ID=badgeID, level=badgeLevel)
        self._icon = R.images.gui.maps.icons.library.badges.c_80x80.dyn(badgeIcon)()
        self._value = badgeID
        self._extraValue = str(badgeLevel)
        self._title = R.strings.detachment.levelBadgeTooltip.badge()
        self._extraTitle = R.strings.detachment.progressionLevel.elite.dyn('c_{}'.format(badgeLevel - 1))()


class SkillPointsReward(BaseReward):
    _type = NewLevelRewardsConstants.SKILL_POINT

    @property
    def _isValidOutput(self):
        return bool(self._value)

    def _initModel(self):
        if self._isConversionProcess:
            self._value = self._detachment.freePoints
        else:
            self._value = self._rewardValue


class CrewMasteryReward(BaseReward):
    _type = NewLevelRewardsConstants.VEHICLE_PROFICIENCY

    @property
    def _isValidOutput(self):
        return bool(self._value)

    def _initModel(self):
        prevPerks, nextPerks = self._rewardValue
        prevCrewMastery = buildKpiDict(prevPerks).getFactor(KPI.Name.CREW_MASTERY)
        nextCrewMastery = buildKpiDict(nextPerks).getFactor(KPI.Name.CREW_MASTERY)
        self._icon = R.images.gui.maps.icons.detachment.tooltips.levelBadge.medium.vehicle_proficiency()
        self._value = int(round(nextCrewMastery - prevCrewMastery))
        self._extraValue = str(int(round(prevCrewMastery)))
        self._title = R.strings.detachment.levelBadgeTooltip.vehicleProficiency()


class VehicleSlotsReward(BaseReward):
    _type = NewLevelRewardsConstants.VEHICLE_SLOT

    @property
    def _isValidOutput(self):
        return bool(self._value)

    def _initModel(self):
        vehicleSlotsDiff, vehicleSlotsCount = self._rewardValue
        slotIconName = 'vehicle_slot_empty_{}'.format(vehicleSlotsCount)
        self._icon = R.images.gui.maps.icons.detachment.tooltips.levelBadge.medium.dyn(slotIconName)()
        self._value = vehicleSlotsDiff
        self._extraValue = str(vehicleSlotsCount)
        self._title = R.strings.detachment.levelBadgeTooltip.vehicleSlot()


class InstructorSlotsReward(BaseReward):
    _type = NewLevelRewardsConstants.INSTRUCTOR_SLOT

    @property
    def _isValidOutput(self):
        return bool(self._value)

    def _initModel(self):
        instructorSlotsDiff, instructorSlotsCount = self._rewardValue
        slotIconName = 'instructor_slot_{}'.format(instructorSlotsCount)
        self._icon = R.images.gui.maps.icons.detachment.tooltips.levelBadge.medium.dyn(slotIconName)()
        self._value = instructorSlotsDiff
        self._extraValue = str(instructorSlotsCount)
        self._title = R.strings.detachment.levelBadgeTooltip.instructorSlot()


class SchoolDiscountReward(BaseReward):
    _type = NewLevelRewardsConstants.PROGRESSION_DISCOUNT

    def _initModel(self):
        self._icon = R.images.gui.maps.icons.detachment.tooltips.levelBadge.reroll_75()
        self._value = self._rewardValue
        self._title = R.strings.detachment.levelBadgeTooltip.rerollBase()
        self._extraValue = SCHOOL


class AcademyDiscountReward(BaseReward):
    _type = NewLevelRewardsConstants.PROGRESSION_DISCOUNT

    def _initModel(self):
        discount = self._rewardValue
        isFree = discount >= 100
        if isFree:
            self._icon = R.images.gui.maps.icons.detachment.tooltips.levelBadge.reroll_free()
            self._title = R.strings.detachment.levelBadgeTooltip.rerollFree()
            self._extraValue = TRAINING
        else:
            self._icon = R.images.gui.maps.icons.detachment.tooltips.levelBadge.reroll_100()
            self._value = discount
            self._title = R.strings.detachment.levelBadgeTooltip.rerollBase()
            self._extraValue = ACADEMY


REWARD_TYPES = {RewardTypes.RANK: RankReward,
 RewardTypes.BADGE_LEVEL: BadgeReward,
 RewardTypes.SKILL_POINTS: SkillPointsReward,
 RewardTypes.AUTO_PERKS: CrewMasteryReward,
 RewardTypes.SCHOOL_DISCOUNT: SchoolDiscountReward,
 RewardTypes.ACADEMY_DISCOUNT: AcademyDiscountReward,
 RewardTypes.VEHICLE_SLOTS: VehicleSlotsReward,
 RewardTypes.INSTRUCTOR_SLOTS: InstructorSlotsReward}
