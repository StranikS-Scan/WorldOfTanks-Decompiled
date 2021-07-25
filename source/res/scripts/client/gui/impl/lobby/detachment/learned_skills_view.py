# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/learned_skills_view.py
from collections import defaultdict
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.shared.event_dispatcher import showDetachmentViewById
from gui.shared.gui_items.perk import PerkGUI
from sound_constants import BARRACKS_SOUND_SPACE
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.gen.view_models.views.lobby.detachment.learned_skills_model import LearnedSkillsModel
from gui.impl.gen.view_models.views.lobby.detachment.skill_model import SkillModel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from skeletons.gui.shared import IItemsCache
from skeletons.gui.detachment import IDetachmentCache
from helpers.dependency import descriptor

class LearnedSkillsView(NavigationViewImpl):
    _CLOSE_IN_PREBATTLE = True
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    _itemsCache = descriptor(IItemsCache)
    _detachmentCache = descriptor(IDetachmentCache)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = LearnedSkillsModel()
        super(LearnedSkillsView, self).__init__(settings, True, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self._detachmentInvID = ctx['detInvID']

    @property
    def viewModel(self):
        return super(LearnedSkillsView, self).getViewModel()

    def _addListeners(self):
        super(LearnedSkillsView, self)._addListeners()
        g_clientUpdateManager.addCallback('inventory', self._onInventoryUpdate)
        self.viewModel.goToMatrix += self._goToMatrix

    def _removeListeners(self):
        g_clientUpdateManager.removeCallback('inventory', self._onInventoryUpdate)
        self.viewModel.goToMatrix -= self._goToMatrix
        super(LearnedSkillsView, self)._removeListeners()

    def _initModel(self, vm):
        super(LearnedSkillsView, self)._initModel(vm)
        self._fillModel(vm)

    def _onLoadPage(self, args=None):
        args['detInvID'] = self._detachmentInvID
        super(LearnedSkillsView, self)._onLoadPage(args)

    def _goToMatrix(self):
        showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_PERKS_MATRIX, {'detInvID': self._detachmentInvID}, self._navigationViewSettings.getPreviousViewSettings())

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.detachment.tooltips.PerkTooltip():
            perkID = event.getArgument('id')
            return PerkTooltip(perkID, detachmentInvID=self._detachmentInvID)
        return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', '')) if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip() else super(LearnedSkillsView, self).createToolTipContent(event, contentID)

    def _onInventoryUpdate(self, diff):
        if GUI_ITEM_TYPE.DETACHMENT in diff or GUI_ITEM_TYPE.INSTRUCTOR in diff:
            with self.viewModel.transaction() as model:
                self._fillModel(model)

    def _buildPerkList(self, perksMatrix):
        commonPerks = []
        talents = []
        for perkID, mPerk in perksMatrix.perks.iteritems():
            if mPerk.ultimate:
                talents.append((perkID, mPerk))
            commonPerks.append((perkID, mPerk))

        res = sorted(talents)
        res.extend(sorted(commonPerks))
        return res

    def _fillModel(self, model):
        detachment = self._detachmentCache.getDetachment(self._detachmentInvID)
        detachmentDescr = detachment.getDescriptor()
        build = detachmentDescr.build
        perkList = self._buildPerkList(detachmentDescr.getPerksMatrix())
        perksWithOvercaps = set()
        instructorBonuses = defaultdict(int)
        for _, perkID, bonus, overcap in detachment.getPerksInstructorInfluence():
            instructorBonuses[perkID] += bonus
            if overcap:
                perksWithOvercaps.add(perkID)

        boosterBonuses = defaultdict(int)
        for _, perkID, bonus, overcap in detachment.getPerksBoosterInfluence():
            boosterBonuses[perkID] += bonus
            if overcap:
                perksWithOvercaps.add(perkID)

        model.setTitle(R.strings.detachment.learnedSkills.title())
        skills = model.getSkillsList()
        for perkID, mPerk in perkList:
            level = build.get(perkID, 0)
            instructorLevels = instructorBonuses.get(perkID, 0)
            boosterLevels = boosterBonuses.get(perkID, 0)
            if not level and not instructorLevels and not boosterLevels:
                continue
            perk = PerkGUI(perkID, level + instructorLevels + boosterLevels)
            skillModel = SkillModel()
            skillModel.setId(perkID)
            skillModel.setTitle(perk.title)
            skillModel.setDescription(perk.getFormattedDescriptionBasedOnLvl())
            if perk.isUltimate:
                skillModel.setType(SkillModel.TALENTS)
            else:
                skillModel.setType(SkillModel.PERKS)
                skillModel.setSkillsCount(level)
                skillModel.setSkillsMaxCount(mPerk.max_points)
                skillModel.setInstructorPoints(instructorLevels)
                skillModel.setBoosterPoints(boosterLevels)
            skillModel.setCourse(perk.course)
            skillModel.setIcon(perk.icon)
            skillModel.setIsOvercapped(perkID in perksWithOvercaps)
            skills.addViewModel(skillModel)

        skills.invalidate()
