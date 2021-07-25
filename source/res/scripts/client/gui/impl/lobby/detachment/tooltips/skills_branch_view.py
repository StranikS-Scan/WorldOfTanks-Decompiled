# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/skills_branch_view.py
from collections import defaultdict
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.skills_branch_model import SkillsBranchModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.perk_model import PerkModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.ultimate_perk_model import UltimatePerkModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.perk import PerkGUI
from helpers.dependency import descriptor
from skeletons.gui.shared import IItemsCache
from skeletons.gui.detachment import IDetachmentCache
from uilogging.detachment.loggers import DynamicGroupTooltipLogger

class SkillsBranchTooltipView(ViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    uiLogger = DynamicGroupTooltipLogger()
    __slots__ = ('__detachmentID', '__branchID', '__vehIntCD', '__bonusPerks')

    def __init__(self, detachmentID, branchID, vehIntCD=None, bonusPerks=None):
        self.__detachmentID = detachmentID
        self.__branchID = branchID
        self.__vehIntCD = vehIntCD
        self.__bonusPerks = bonusPerks if bonusPerks is not None else {}
        settings = ViewSettings(R.views.lobby.detachment.tooltips.SkillsBranchTooltip())
        settings.model = SkillsBranchModel()
        super(SkillsBranchTooltipView, self).__init__(settings)
        return

    def _onLoading(self, *args, **kwargs):
        super(SkillsBranchTooltipView, self)._onLoading()
        detachment = self.__detachmentCache.getDetachment(self.__detachmentID)
        detDescr = detachment.getDescriptor()
        build = detDescr.build
        perksMatrix = detDescr.getPerksMatrix()
        matrixBranch = perksMatrix.branches[self.__branchID]
        with self.viewModel.transaction() as vm:
            vm.setName(R.strings.item_types.abilities.dyn(matrixBranch.name)())
            vm.setDescription(R.strings.item_types.abilities.dyn(matrixBranch.description)())
            vm.setIcon(R.images.gui.maps.icons.detachment.icons.branch.c_48x48.dyn(matrixBranch.icon + '_active')())
            vehicle = None
            if self.__vehIntCD:
                vehicle = self.__itemsCache.items.getItemByCD(self.__vehIntCD)
            bonusPerks = self.__bonusPerks
            instructorBonuses = defaultdict(int)
            perksWithOvercaps = set()
            for _, perkID, bonus, overcap in detachment.getPerksInstructorInfluence(bonusPerks=bonusPerks, vehicle=vehicle):
                instructorBonuses[perkID] += bonus
                if overcap:
                    perksWithOvercaps.add(perkID)

            boosterBonuses = defaultdict(int)
            for _, perkID, bonus, overcap in detachment.getPerksBoosterInfluence(bonusPerks=bonusPerks, vehicle=vehicle):
                boosterBonuses[perkID] += bonus
                if overcap:
                    perksWithOvercaps.add(perkID)

            perksIDs = sorted(perksMatrix.getNonUltimatePerksInBranch(self.__branchID))
            branchPoints = 0
            perksList = vm.getPerksList()
            for perkID in perksIDs:
                perk = PerkGUI(perkID)
                perkModel = PerkModel()
                perkModel.setId(perkID)
                perkModel.setName(perk.name)
                perkModel.setIcon(perk.icon)
                perkModel.setIsOvercapped(perkID in perksWithOvercaps)
                perkPoints = build.get(perkID, 0)
                branchPoints += perkPoints
                perkModel.setPoints(perkPoints)
                perkModel.setTempPoints(self.__bonusPerks.get(perkID, 0))
                matrixPerk = perksMatrix.perks[perkID]
                perkModel.setMaxPoints(matrixPerk.max_points)
                if perkID in instructorBonuses:
                    perkModel.setInstructorPoints(instructorBonuses[perkID])
                if perkID in boosterBonuses:
                    perkModel.setBoosterPoints(boosterBonuses[perkID])
                perkModel.setState(PerkModel.STATE_OPENED)
                perksList.addViewModel(perkModel)

            ultimatePerksIDs = sorted(perksMatrix.getUltimatePerksInBranch(self.__branchID))
            ultimateList = vm.getUltimateList()
            ultimateSelected = False
            ultimatePerksAreUnlocked = branchPoints >= matrixBranch.ultimate_threshold
            if ultimatePerksAreUnlocked:
                ultimateSelected = any((perkID for perkID in ultimatePerksIDs if build.get(perkID, 0)))
            for perkID in ultimatePerksIDs:
                perk = PerkGUI(perkID)
                ultimateModel = UltimatePerkModel()
                ultimateModel.setId(perkID)
                ultimateModel.setName(perk.name)
                ultimateModel.setIcon(perk.icon)
                perkPoints = build.get(perkID, 0)
                if ultimateSelected:
                    state = UltimatePerkModel.STATE_SELECTED if perkPoints else UltimatePerkModel.STATE_LOCKED
                else:
                    state = UltimatePerkModel.STATE_OPENED if ultimatePerksAreUnlocked else UltimatePerkModel.STATE_LOCKED
                ultimateModel.setSavedState(state)
                ultimateList.addViewModel(ultimateModel)

        return

    def _initialize(self, *args, **kwargs):
        super(SkillsBranchTooltipView, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(SkillsBranchTooltipView, self)._finalize()

    @property
    def viewModel(self):
        return super(SkillsBranchTooltipView, self).getViewModel()
