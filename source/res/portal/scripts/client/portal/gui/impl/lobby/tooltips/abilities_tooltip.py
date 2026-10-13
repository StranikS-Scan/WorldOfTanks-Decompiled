# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/abilities_tooltip.py
from frameworks.wulf import ViewSettings
from portal.gui.impl.gen.view_models.views.lobby.tooltips.abilities_tooltip_model import AbilitiesTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from portal.skeletons.portal_event_controller import IPortalEventController

class AbilitiesTooltip(ViewImpl):
    __slots__ = ('_abilityName', '_level', '_learned')
    __portalController = dependency.descriptor(IPortalEventController)

    def __init__(self, name, learned=False, level=None):
        settings = ViewSettings(R.views.portal.lobby.tooltips.AbilitiesTooltip())
        settings.model = AbilitiesTooltipModel()
        self._abilityName = name
        self._level = level
        self._learned = learned
        super(AbilitiesTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AbilitiesTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(AbilitiesTooltip, self)._onLoading(*args, **kwargs)
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            vm.setName(self._abilityName)
            vm.setDuration(self.__portalController.getAbilityDuration(self._abilityName))
            vm.setReload(self.__portalController.getAbilityCooldown(self._abilityName))
            if self._level:
                vm.setLevel(self._level)
            if self._learned:
                vm.setLearned(self._learned)
