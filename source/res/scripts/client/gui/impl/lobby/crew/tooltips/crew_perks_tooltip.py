# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/crew_perks_tooltip.py
import copy
import json
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_booster_model import CrewPerksTooltipBoosterModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_model import CrewPerksTooltipModel, BoosterType
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Tankman import getTankmanSkill, crewMemberRealSkillLevel, tankmanPersonalSkillLevel, getBattleBooster, isSkillLearnt
from gui.shared.skill_parameters.skills_packers import g_skillPackers, packBase
from gui.shared.tooltips.advanced import SKILL_MOVIES
from helpers import dependency
from items.components import perks_constants
from items.tankmen import getSkillsConfig, MAX_SKILL_LEVEL, SEPARATE_SKILLS, MAX_SKILLS_EFFICIENCY, generateCompactDescr, COMMON_SKILLS, MAX_SKILLS_EFFICIENCY_XP
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from gui.shared.gui_items.Vehicle import sortCrew
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Tankman import Tankman, TankmanSkill
    from items.readers.skills_readers import SkillDescrsArg
    from gui.shared.gui_items.Vehicle import Vehicle

class CrewPerksTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __slots__ = ('_skillName', '_tankman', '_tankmanVehicle', '_skill', '_descrArgs', '_skillLevel', '_skillBooster', '_isCommonExtraAvailable', '_showAdditionalInfo', '_isTmanTrainedVeh', '_isFakeSkill', '_isFakeSkillLvl', '_isCmpSkill')

    def __init__(self, skillName, tankmanId, skillLevel=None, isCommonExtraAvailable=False, showAdditionalInfo=True, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.crew.tooltips.CrewPerksTooltip(), args=args, kwargs=kwargs)
        settings.model = CrewPerksTooltipModel()
        skillCustomisation = kwargs.get('skillCustomisation', None)
        self._skillName = skillName
        self._isCommonExtraAvailable = isCommonExtraAvailable
        self._showAdditionalInfo = showAdditionalInfo
        self._isFakeSkill = False
        self._isFakeSkillLvl = False
        self._isCmpSkill = False
        self._tankman = self._itemsCache.items.getTankman(int(tankmanId)) if tankmanId else None
        self._tankmanVehicle = self._getVehicle()
        self._isTmanTrainedVeh = not self._tankmanVehicle or self._tankman.descriptor.isOwnVehicleOrPremium(self._tankmanVehicle.descriptor.type)
        self._skillBooster = getBattleBooster(self._tankmanVehicle, self._skillName)
        self._skill = getTankmanSkill(self._skillName, tankman=self._tankman, skillCustomisation=skillCustomisation)
        self._descrArgs = getSkillsConfig().getSkill(self._skillName).uiSettings.descrArgs
        self._skillLevel = self._getSkillLevel(skillLevel, self._isIrrelevant())
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

    def _getSkillLevel(self, skillLevel=None, onlyPersonal=False):
        if skillLevel > 0:
            self._isCmpSkill = True
            return skillLevel
        if not self._skill.isAlreadyEarned and not self._isIrrelevant():
            if self._tankman and 0 <= self._tankman.currentVehicleSkillsEfficiency < MAX_SKILLS_EFFICIENCY and not self._skillBooster:
                skilledTman = self._getTmanWithSkill()
                if skilledTman:
                    self._isFakeSkill = True
                    if onlyPersonal or not skilledTman.isInTank or self._isPersonalSkillLevelNeeded():
                        return tankmanPersonalSkillLevel(skilledTman, self._skillName, booster=self._skillBooster, withIncrease=False)
                    newVehicle = self._getVehicleWithSkilledTman(skilledTman, self._skill.name)
                    return crewMemberRealSkillLevel(newVehicle, self._skill.name, commonWithIncrease=False)
            else:
                return MAX_SKILL_LEVEL
        if self._isIrrelevant():
            maxSkillsEffTman = self._getMaxSkillsEffAndLikeOwnVehTman()
            if maxSkillsEffTman:
                if onlyPersonal or not maxSkillsEffTman.isInTank or self._isPersonalSkillLevelNeeded():
                    realSkillLevel = tankmanPersonalSkillLevel(maxSkillsEffTman, self._skillName, booster=self._skillBooster, withIncrease=False)
                else:
                    newVehicle = self._getVehicleWithSkilledTman(maxSkillsEffTman)
                    realSkillLevel = crewMemberRealSkillLevel(newVehicle, self._skill.name, commonWithIncrease=False)
                if realSkillLevel > 0:
                    return realSkillLevel
                return MAX_SKILL_LEVEL
        if self._tankman and (self._isTmanTrainedVeh or self._skillBooster):
            if onlyPersonal or not self._tankman.isInTank or self._skillName in SEPARATE_SKILLS:
                realSkillLevel = tankmanPersonalSkillLevel(self._tankman, self._skillName, booster=self._skillBooster)
            else:
                realSkillLevel = crewMemberRealSkillLevel(self._tankmanVehicle, self._skill.name, commonWithIncrease=True)
            if realSkillLevel > 0:
                return realSkillLevel
        self._isFakeSkillLvl = True
        return MAX_SKILL_LEVEL

    def _isPersonalSkillLevelNeeded(self):
        return self._skillName in SEPARATE_SKILLS or self._skillName not in COMMON_SKILLS and self._skillName not in perks_constants.AVG_LVL_PERKS

    def _isIrrelevant(self):
        return self._tankman and not self._skill.isEnable

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setIcon(self._skill.bigIconPath)
            vm.setTitle(self._skill.userName)
            vm.setLevel(self._skillLevel)
            vm.setSkillType(self._skill.typeName)
            vm.setIsCommonExtraAvailable(self._isCommonExtraAvailable)
            vm.setIsAdvancedTooltipEnable(bool(SKILL_MOVIES.get(self._skill.name, None)))
            isZeroPerk, isIrrelevant = (self._tankman and self._skill.name in self._tankman.freeSkillsNames, self._isIrrelevant()) if self._showAdditionalInfo else (False, False)
            vm.setIsZeroPerk(isZeroPerk)
            vm.setIsIrrelevant(isIrrelevant)
            skillEfficiency = self._tankman.currentVehicleSkillsEfficiency if self._tankman else MAX_SKILLS_EFFICIENCY
            if self._skill.name in perks_constants.SKIP_SE_PERKS or isIrrelevant:
                skillEfficiency = MAX_SKILLS_EFFICIENCY
            vm.setEfficiency(skillEfficiency)
            vm.setBoosterType(self._getBoosterType())
            self.fillCurrentLvlInfo(vm, skillEfficiency)
        return

    def fillCurrentLvlInfo(self, vm, skillEfficiency):
        boosters = vm.getBoosters()
        boosters.clear()
        skillPacker = g_skillPackers.get(self._skillName, packBase)
        skillParams = skillPacker(self._descrArgs, self._skillLevel, isSkillAlreadyEarned=True if self._isFakeSkill else self._skill.isAlreadyEarned, lowEfficiency=skillEfficiency < MAX_SKILLS_EFFICIENCY, isTmanTrainedVeh=self._isTmanTrainedVeh, hasBooster=self._skillBooster is not None, customValues=dict(((name, lambda b=self._skillBooster, n=name: b if b and hasattr(b, n) else None) for name, _ in self._descrArgs)) if self._skillName in g_skillPackers else None)
        keyArgs = skillParams.get('keyArgs', {})
        kpiArgs = skillParams.get('kpiArgs', [])
        for kpiValue, kpiText, impact in kpiArgs:
            booster = CrewPerksTooltipBoosterModel()
            booster.setValue(kpiValue)
            booster.setText(kpiText)
            booster.setImpact(impact)
            boosters.addViewModel(booster)

        vm.setDescription(self._skill.currentLvlDescription if self._isCmpSkill or self._skillBooster and not self._isIrrelevant() or self._skillLevel > 0 and not self._isFakeSkillLvl and self._skill.isAlreadyEarned or self._skill.name in perks_constants.SKIP_SE_PERKS else self._skill.maxLvlDescription)
        descrKwargs = json.dumps(keyArgs)
        vm.setDescriptionKwargs(descrKwargs)
        return

    def _getTmanWithSkill(self):
        tmanDescr = self._tankman.descriptor
        skills = tmanDescr.skills[:]
        if not skills:
            skills.append(self._skill.name)
            lastSkillLevel = MAX_SKILL_LEVEL
        else:
            skills.insert(0, self._skill.name)
            lastSkillLevel = tmanDescr.lastSkillLevel
        skilledTman = self._itemsFactory.createTankman(generateCompactDescr(tmanDescr.getPassport(), tmanDescr.vehicleTypeID, tmanDescr.role, tmanDescr.roleLevel, skills, lastSkillLevel, skillsEfficiencyXP=tmanDescr.skillsEfficiencyXP), vehicle=self._tankmanVehicle, vehicleSlotIdx=self._tankman.vehicleSlotIdx)
        return skilledTman

    def _getMaxSkillsEffAndLikeOwnVehTman(self):
        tmanDescr = self._tankman.descriptor
        vehicleTypeID = tmanDescr.vehicleTypeID
        if self._tankmanVehicle:
            _, vehicleTypeID = self._tankmanVehicle.descriptor.type.id
        skilledTman = self._itemsFactory.createTankman(generateCompactDescr(tmanDescr.getPassport(), vehicleTypeID, tmanDescr.role, tmanDescr.roleLevel, tmanDescr.skills[:], tmanDescr.lastSkillLevel, skillsEfficiencyXP=MAX_SKILLS_EFFICIENCY_XP), vehicle=self._tankmanVehicle, vehicleSlotIdx=self._tankman.vehicleSlotIdx)
        return skilledTman

    def _getVehicleWithSkilledTman(self, skilledTman, skillName=''):
        newVehicle = copy.copy(self._tankmanVehicle)
        if skillName in COMMON_SKILLS:
            newVehicle.crew = newVehicle.getCrewWithSkill(skillName)
        else:
            crewItems = list()
            skilledTmanDescr = self._tankman.descriptor
            for slotIdx, tman in newVehicle.crew:
                if tman and tman.descriptor.role == skilledTmanDescr.role:
                    crewItems.append((slotIdx, skilledTman))
                    continue
                crewItems.append((slotIdx, tman))

            newVehicle.crew = sortCrew(crewItems, self._tankmanVehicle.descriptor.type.crewRoles)
        return newVehicle

    def _getBoosterType(self):
        if self._skillBooster and not self._isIrrelevant():
            if isSkillLearnt(self._skillName, self._tankmanVehicle) or self._skillName in perks_constants.SKIP_SE_PERKS:
                return BoosterType.EXTRA
            return BoosterType.ORDINARY
        return BoosterType.NONE
