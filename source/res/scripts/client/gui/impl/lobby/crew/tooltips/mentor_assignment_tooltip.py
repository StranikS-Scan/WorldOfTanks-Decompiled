# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/mentor_assignment_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.mentor_assignment_tooltip_model import MentorAssignmentTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class MentorAssignmentTooltip(ViewImpl):
    __slots__ = ('sourceTmanID', 'targetTmanID')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, sourceTmanID, targetTmanID, *args, **kwargs):
        self.sourceTmanID = sourceTmanID
        self.targetTmanID = targetTmanID
        settings = ViewSettings(R.views.lobby.crew.tooltips.MentorAssignmentTooltip(), args=args, kwargs=kwargs)
        settings.model = MentorAssignmentTooltipModel()
        super(MentorAssignmentTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MentorAssignmentTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MentorAssignmentTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        sourceTman = self._itemsCache.items.getTankman(self.sourceTmanID)
        targetTman = self._itemsCache.items.getTankman(self.targetTmanID)
        with self.viewModel.transaction() as vm:
            vm.setFullName(sourceTman.getFullUserNameWithSkin())
            vm.setHasFreeSkills(targetTman.freeSkillsCount > 0)
