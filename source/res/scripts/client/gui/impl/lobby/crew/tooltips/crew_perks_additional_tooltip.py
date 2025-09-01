# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/crew_perks_additional_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_additional_tooltip_model import CrewPerksAdditionalTooltipModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_model import BoosterType
from gui.impl.lobby.crew.crew_helpers import getTankmanCrewAssistOrderSets
from gui.impl.lobby.crew.crew_helpers.model_setters import setSkillProgressionModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Tankman import isSkillLearnt, SKILL_EFFICIENCY_UNTRAINED, getBattleBooster
from gui.shared.gui_items.tankman_skill import getTankmanSkill
from gui.shared.tooltips.advanced import SKILL_MOVIES
from helpers import dependency
from items.components import perks_constants
from items.components.skills_constants import SKILLS_BY_ROLES_ORDERED
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Tankman import Tankman
    from gui.shared.gui_items.tankman_skill import TankmanSkill
    from gui.shared.gui_items.Vehicle import Vehicle

class CrewPerksAdditionalTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __slots__ = ('_skillName', '_tankman', '_tankmanVehicle', '_skill', '_skillBooster', '_skillIdx', '_showCrewAssist')

    def __init__(self, skillName, skillRole, tankmanId=None, skillIdx=-1, showCrewAssist=False):
        settings = ViewSettings(R.views.lobby.crew.tooltips.CrewPerksAdditionalTooltip())
        settings.model = CrewPerksAdditionalTooltipModel()
        self._skillName = skillName
        self._tankman = self._itemsCache.items.getTankman(int(tankmanId)) if tankmanId else None
        self._tankmanVehicle = self._getVehicle()
        self._skill = getTankmanSkill(self._skillName, skillRole, tankman=self._tankman)
        self._skillIdx = skillIdx
        self._skillBooster = getBattleBooster(self._tankmanVehicle, self._skillName)
        self._showCrewAssist = showCrewAssist
        super(CrewPerksAdditionalTooltip, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CrewPerksAdditionalTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CrewPerksAdditionalTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setIconName(self._skill.extensionLessIconName)
            vm.setSkillType(self._skill.typeName)
            vm.setUserName(self._skill.userName)
            vm.setDescription(self._skill.altDescription)
            vm.setInfo(self._skill.altInfo)
            movieName = SKILL_MOVIES.get(self._skill.name, None)
            if movieName:
                vm.setAnimationName(movieName)
            isDisabled = self._tankman and self._tankman.currentVehicleSkillsEfficiency == SKILL_EFFICIENCY_UNTRAINED and self._getBoosterType() == BoosterType.NONE
            vm.setIsDisabled(isDisabled)
            vm.setIsIrrelevant(self._isIrrelevant())
            if self._skillIdx > -1:
                isZero = self._skill.name in self._tankman.freeSkillsNames
                if self._skill.skillRole == self._tankman.role and not isZero:
                    vm.setShowSkillProgression(True)
                    setSkillProgressionModel(vm=vm.skillProgression, tankman=self._tankman, skillIndex=self._skillIdx, isZero=isZero)
            if self._showCrewAssist:
                popularityListVM = vm.getPopularityList()
                popularityListVM.clear()
                if self._wotPlusCtrl.isCrewAssistEnabled():
                    tmanRoleForSkill = ''
                    if self._skillName in SKILLS_BY_ROLES_ORDERED[self._tankman.role]:
                        tmanRoleForSkill = self._tankman.role
                    else:
                        for bonusRole in self._tankman.bonusRoles():
                            if self._skillName in SKILLS_BY_ROLES_ORDERED[bonusRole]:
                                tmanRoleForSkill = bonusRole
                                break

                    orderSets = getTankmanCrewAssistOrderSets(self._tankman, tmanRoleForSkill)
                    hasCommonSet, hasLegendarySet = self._wotPlusCtrl.validateCrewAssistOrderSets(orderSets)
                    hideDataGuiIndicator = -1
                    commonSkillPopularity, legendSkillPopularity = orderSets.get(self._skillName, (hideDataGuiIndicator, hideDataGuiIndicator))
                    popularityListVM.addReal(commonSkillPopularity if hasCommonSet else hideDataGuiIndicator)
                    popularityListVM.addReal(legendSkillPopularity if hasLegendarySet else hideDataGuiIndicator)
                popularityListVM.invalidate()
        return

    def _getVehicle(self):
        if self._tankman is None:
            return
        else:
            return self._itemsCache.items.getVehicle(self._tankman.vehicleInvID) if self._tankman.isInTank else None

    def _getBoosterType(self):
        if self._skillBooster and not self._isIrrelevant():
            if isSkillLearnt(self._skillName, self._tankmanVehicle) or self._skillName in perks_constants.SKIP_SE_PERKS:
                return BoosterType.EXTRA
            return BoosterType.ORDINARY
        return BoosterType.NONE

    def _isIrrelevant(self):
        return False if not self._tankman else not self._skill.isEnable or not self._skill.isRelevant
