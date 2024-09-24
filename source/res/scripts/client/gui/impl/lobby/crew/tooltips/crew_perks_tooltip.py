# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/crew_perks_tooltip.py
import copy
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_booster_model import CrewPerksTooltipBoosterModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_model import BoosterType, CrewPerksTooltipModel, PerkType
from gui.impl.lobby.crew.crew_helpers.skill_helpers import formatDescription, getMaxSkillsEffAndLikeOwnVehTman, getSkillDescription, getSkillParams, getTmanWithSkill, getVehicleWithSkilledTman
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Tankman import crewMemberRealSkillLevel, getBattleBooster, getTankmanSkill, isSkillLearnt, tankmanPersonalSkillLevel, SKILL_EFFICIENCY_UNTRAINED
from gui.shared.tooltips.advanced import SKILL_MOVIES
from helpers import dependency
from items import tankmen
from items.components import perks_constants
from items.components.skills_constants import UNLEARNABLE_SKILLS
from items.tankmen import MAX_SKILLS_EFFICIENCY, MAX_SKILL_LEVEL, getSkillsConfig
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Tankman import Tankman, TankmanSkill
    from items.readers.skills_readers import SkillDescrsArg
    from gui.shared.gui_items.Vehicle import Vehicle

class CrewPerksTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __slots__ = ('_skillName', '_tankman', '_tankmanVehicle', '_skill', '_descrArgs', '_skillLevel', '_skillBooster', '_showAdditionalInfo', '_isTmanTrainedVeh', '_isFakeSkill', '_isFakeSkillLvl', '_isCmpSkill', '_skillLevelWithoutEff', '_isBonus', '_isIrrelevant', '_isUntrained')

    def __init__(self, skillName, tankmanId, skillLevel=None, showAdditionalInfo=True, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.crew.tooltips.CrewPerksTooltip(), args=args, kwargs=kwargs)
        settings.model = CrewPerksTooltipModel()
        skillCustomisation = kwargs.get('skillCustomisation', None)
        self._skillName = skillName
        self._showAdditionalInfo = showAdditionalInfo
        self._isBonus = kwargs.get('isBonus', None)
        self._tankman = self._itemsCache.items.getTankman(int(tankmanId)) if tankmanId else None
        self._tankmanVehicle = self._getVehicle()
        self._isTmanTrainedVeh = not self._tankmanVehicle or self._tankman.descriptor.isOwnVehicleOrPremium(self._tankmanVehicle.descriptor.type)
        self._skillBooster = getBattleBooster(self._tankmanVehicle, self._skillName)
        self._skill = getTankmanSkill(self._skillName, tankman=self._tankman, skillCustomisation=skillCustomisation)
        self._isUntrained = self._tankman.currentVehicleSkillsEfficiency == SKILL_EFFICIENCY_UNTRAINED if self._tankman else False
        self._isIrrelevant = self._getIsIrrelevant()
        if self._skill.isLearnedAsMajor and self._skill.isLearnedAsBonus and self._isBonus:
            self._skill.setIsSkillActive(not self._isIrrelevant and self._isUntrained)
        self._descrArgs = getSkillsConfig().getSkill(self._skillName).uiSettings.descrArgs
        self._skillLevelWithoutEff = 0
        self._isFakeSkill = False
        self._isFakeSkillLvl = False
        self._isCmpSkill = False
        self.__initSkillData(skillLevel)
        self._skillLevelWithoutEff = self._skillLevelWithoutEff or self._skillLevel
        super(CrewPerksTooltip, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CrewPerksTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CrewPerksTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _getVehicle(self):
        if self._tankman is None:
            return
        else:
            return self._itemsCache.items.getVehicle(self._tankman.vehicleInvID) if self._tankman.isInTank else None

    def _getIsIrrelevant(self):
        if not self._tankman:
            return False
        else:
            if self._isBonus is None:
                role = self._getBonusRole() or self._tankman.role
            else:
                role = self._getBonusRole() if self._isBonus else self._tankman.role
            return not self._skill.isEnable or role and not self._skill.isRelevantForRole(role)

    def _getBonusRole(self):
        for bonusRole, bonusSkills in self._tankman.bonusSkills.iteritems():
            for bonusSkill in bonusSkills:
                if bonusSkill and self._skill.name == bonusSkill.name:
                    return bonusRole

        return None

    def _isGroupSkill(self):
        if not self._tankmanVehicle:
            return False
        if self._skill.typeName == PerkType.COMMON:
            return True
        rolesHasSkillCount = 0
        for _, roles in enumerate(self._tankmanVehicle.descriptor.type.crewRoles):
            for role in roles:
                if self._skill.name in tankmen.SKILLS_BY_ROLES.get(role, frozenset()):
                    rolesHasSkillCount += 1
                    if rolesHasSkillCount > 1:
                        return True

    def _isGroupSkillHasLowEff(self):
        if not self._tankmanVehicle:
            return False
        for _, tman in self._tankmanVehicle.crew:
            if tman and self._skill.name in tankmen.SKILLS_BY_ROLES.get(tman.descriptor.role, frozenset()):
                if tman.canUseSkillsInCurrentVehicle and not tman.isMaxCurrentVehicleSkillsEfficiency:
                    return True

        return False

    def _isGroupSkillHasUntrained(self):
        if not self._tankmanVehicle:
            return False
        for _, tman in self._tankmanVehicle.crew:
            if tman and self._skill.name in tankmen.SKILLS_BY_ROLES.get(tman.descriptor.role, frozenset()):
                if not tman.canUseSkillsInCurrentVehicle:
                    return True

        return False

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setIconName(self._skill.extensionLessIconName)
            vm.setUserName(self._skill.userName)
            vm.setLevel(self._skillLevelWithoutEff)
            vm.setRealLevel(self._skillLevel)
            vm.setSkillType(self._skill.typeName)
            isGroupSkill = self._isGroupSkill()
            vm.setIsGroupSkill(isGroupSkill)
            vm.setIsAnyMemberWithLowEfficiency(self._isGroupSkillHasLowEff() if isGroupSkill else False)
            vm.setIsAnyMemberUntrained(self._isGroupSkillHasUntrained() if isGroupSkill else False)
            vm.setIsAdvancedTooltipEnable(bool(SKILL_MOVIES.get(self._skill.name, None)))
            isZeroPerk, isIrrelevant = (self._tankman and self._skill.name in self._tankman.freeSkillsNames, self._isIrrelevant) if self._showAdditionalInfo else (False, False)
            vm.setIsZero(isZeroPerk)
            vm.setIsIrrelevant(isIrrelevant)
            skillEfficiency = self._tankman.currentVehicleSkillsEfficiency if self._tankman else MAX_SKILLS_EFFICIENCY
            if self._skill.name in perks_constants.SKIP_SE_PERKS or isIrrelevant:
                skillEfficiency = MAX_SKILLS_EFFICIENCY
            vm.setEfficiency(skillEfficiency)
            vm.setBoosterType(self._getBoosterType())
            self.fillCurrentLvlInfo(vm)
        return

    def fillCurrentLvlInfo(self, vm):
        boosters = vm.getBoosters()
        boosters.clear()
        skillParams = getSkillParams(self._tankman, self._tankmanVehicle, self._skillBooster, self._skill, self._skillName, self._skillLevel, self._isFakeSkill, self._isIrrelevant)
        keyArgs = skillParams.get('keyArgs', {})
        kpiArgs = skillParams.get('kpiArgs', [])
        for kpiValue, kpiText, impact in kpiArgs:
            booster = CrewPerksTooltipBoosterModel()
            booster.setValue(kpiValue)
            booster.setText(kpiText)
            booster.setImpact(impact)
            boosters.addViewModel(booster)

        vm.setDescription(formatDescription(getSkillDescription(self._tankman, self._skill, self._skillLevel, self._skillBooster, self._isCmpSkill, self._isFakeSkillLvl, self._isIrrelevant), keyArgs))

    def _getBoosterType(self):
        if self._skillBooster and not self._isIrrelevant:
            if isSkillLearnt(self._skillName, self._tankmanVehicle) or self._skillName in perks_constants.SKIP_SE_PERKS:
                return BoosterType.EXTRA
            return BoosterType.ORDINARY
        return BoosterType.NONE

    def __initSkillData(self, skillLevel):
        self._skillLevel = skillLevel
        skillBooster = getBattleBooster(self._tankmanVehicle, self._skillName)
        if self._skillLevel > 0:
            self._isCmpSkill = True
            return
        if self._skill.name in UNLEARNABLE_SKILLS:
            self._skillLevel = MAX_SKILL_LEVEL
            return
        if self.__handleHoverNewSkill(skillBooster):
            return
        if self.__handleHoverDisabledSkill(skillBooster):
            return
        self.__handleHoverLearnedSkill(skillBooster)

    def __handleHoverNewSkill(self, skillBooster):
        if not self._tankman:
            return False
        if self._skill.isEnable and self._skill.isLearned or self._isIrrelevant:
            return False
        if self._tankman.isMaxCurrentVehicleSkillsEfficiency and skillBooster:
            self._skillLevel = MAX_SKILL_LEVEL
            return True
        skilledTman = getTmanWithSkill(self._tankman, self._tankmanVehicle, self._skill, self._itemsFactory)
        if not skilledTman:
            return False
        self._isFakeSkill = True
        if not skilledTman.isInTank:
            self._skillLevel = tankmanPersonalSkillLevel(skilledTman, self._skillName, booster=skillBooster, withIncrease=False)
            return True
        newVehicle = getVehicleWithSkilledTman(skilledTman, self._tankman, self._tankmanVehicle, self._skill.name)
        self._skillLevel = crewMemberRealSkillLevel(newVehicle, self._skill.name, commonWithIncrease=False, skipIrrelevantState=True)
        return True

    def __handleHoverDisabledSkill(self, skillBooster):
        if not self._tankman:
            return False
        isRealUnrained = not self._skill.isSkillActive and self._isUntrained
        if isRealUnrained or self._isIrrelevant:
            realSkillLevel = 0
            calcLevel = not (isRealUnrained and not self._skillBooster) or self._isIrrelevant
            if calcLevel:
                withIncrease = isRealUnrained and self._skillBooster and not self._isIrrelevant
                maxSkillsEffTman = self._tankman if isRealUnrained and not self._isIrrelevant else getMaxSkillsEffAndLikeOwnVehTman(self._tankman, self._tankmanVehicle, self._itemsFactory, removeSkillCopies=self._isIrrelevant)
                if not maxSkillsEffTman:
                    return False
                if self._isIrrelevant or not maxSkillsEffTman.isInTank:
                    realSkillLevel = tankmanPersonalSkillLevel(maxSkillsEffTman, self._skillName, booster=skillBooster, withIncrease=withIncrease)
                else:
                    newVehicle = self._tankmanVehicle if isRealUnrained and not self._isIrrelevant else getVehicleWithSkilledTman(maxSkillsEffTman, self._tankman, self._tankmanVehicle)
                    realSkillLevel = crewMemberRealSkillLevel(newVehicle, self._skill.name, commonWithIncrease=withIncrease, shouldIncrease=withIncrease)
            self._isFakeSkillLvl = realSkillLevel <= 0
            self._skillLevel = realSkillLevel if realSkillLevel > 0 else MAX_SKILL_LEVEL
            return True

    def __handleHoverLearnedSkill(self, skillBooster):
        realSkillLevel = 0
        if self._tankman and (self._isTmanTrainedVeh or skillBooster):
            if not self._tankman.isInTank:
                realSkillLevel = tankmanPersonalSkillLevel(self._tankman, self._skillName, booster=skillBooster)
                if not self._tankman.isMaxCurrentVehicleSkillsEfficiency:
                    maxSkillsEffTman = getMaxSkillsEffAndLikeOwnVehTman(self._tankman, self._tankmanVehicle, self._itemsFactory)
                    if maxSkillsEffTman:
                        self._skillLevelWithoutEff = tankmanPersonalSkillLevel(maxSkillsEffTman, self._skillName, booster=skillBooster)
            else:
                realSkillLevel = crewMemberRealSkillLevel(self._tankmanVehicle, self._skill.name, commonWithIncrease=True)
                if any((tman and not tman.isMaxCurrentVehicleSkillsEfficiency for _, tman in self._tankmanVehicle.crew)):
                    perfectCrew = self._tankmanVehicle.getPerfectCrew()
                    idealCrewVehicle = copy.copy(self._tankmanVehicle)
                    idealCrewVehicle.crew = perfectCrew
                    self._skillLevelWithoutEff = crewMemberRealSkillLevel(idealCrewVehicle, self._skill.name, commonWithIncrease=True)
        if not realSkillLevel:
            multiplier = self._tankman.skillsEfficiency if self._tankman else 1
            realSkillLevel = MAX_SKILL_LEVEL * multiplier
            self._isFakeSkillLvl = True
        self._skillLevel = realSkillLevel
        return True
