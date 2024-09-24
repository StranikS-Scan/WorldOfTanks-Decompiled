# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/crew_perks_additional_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_additional_tooltip_model import CrewPerksAdditionalTooltipModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_model import BoosterType
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Tankman import getTankmanSkill, isSkillLearnt, SKILL_EFFICIENCY_UNTRAINED, getBattleBooster
from gui.shared.tooltips.advanced import SKILL_MOVIES
from helpers import dependency
from items.components import perks_constants
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Tankman import Tankman, TankmanSkill
    from gui.shared.gui_items.Vehicle import Vehicle

class CrewPerksAdditionalTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_skillName', '_tankman', '_tankmanVehicle', '_skill', '_skillBooster')

    def __init__(self, skillName=None, tankmanId=None):
        settings = ViewSettings(R.views.lobby.crew.tooltips.CrewPerksAdditionalTooltip())
        settings.model = CrewPerksAdditionalTooltipModel()
        self._skillName = skillName
        self._tankman = self._itemsCache.items.getTankman(int(tankmanId)) if tankmanId else None
        self._tankmanVehicle = self._getVehicle()
        self._skill = getTankmanSkill(self._skillName, tankman=self._tankman)
        self._skillBooster = getBattleBooster(self._tankmanVehicle, self._skillName)
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
        if not self._tankman:
            return False
        role = self._tankman.role
        for bonusRole, bonusSkills in self._tankman.bonusSkills.iteritems():
            for bonusSkill in bonusSkills:
                if bonusSkill and self._skill.name == bonusSkill.name:
                    role = bonusRole
                    break

        return not self._skill.isEnable or not self._skill.isRelevantForRole(role)
