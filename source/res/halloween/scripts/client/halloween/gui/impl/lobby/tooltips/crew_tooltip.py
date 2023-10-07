# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/crew_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.crew_tooltip_model import CrewTooltipModel
from skeletons.gui.game_control import IHalloweenController
from helpers import dependency
from items import tankmen
from shared_utils import findFirst

class CrewTooltip(ViewImpl):
    __slots__ = ('_phaseIndex',)
    _hwController = dependency.descriptor(IHalloweenController)

    def __init__(self, phaseIndex):
        settings = ViewSettings(R.views.halloween.lobby.tooltips.CrewTooltip())
        settings.model = CrewTooltipModel()
        super(CrewTooltip, self).__init__(settings)
        self._phaseIndex = phaseIndex

    @property
    def viewModel(self):
        return super(CrewTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CrewTooltip, self)._onLoading(*args, **kwargs)
        phase = self._hwController.phases.getPhaseByIndex(self._phaseIndex)
        if not phase:
            return
        tankmanTokenArgs = phase.getTmanTokenBonus().split(':')
        if not tankmanTokenArgs:
            return
        groupName = tankmanTokenArgs[3]
        group = findFirst(lambda g: g.name == groupName, tankmen.getNationGroups(0, isPremium=True).itervalues())
        roles = group.rolesList
        if not roles:
            return
        with self.getViewModel().transaction() as model:
            model.setCrewGroup(groupName)
            model.setCrewRole(roles[0])
