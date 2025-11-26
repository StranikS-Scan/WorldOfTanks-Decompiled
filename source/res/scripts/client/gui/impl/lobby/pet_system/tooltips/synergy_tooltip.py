# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/tooltips/synergy_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pet_system.tooltips.synergy_tooltip_model import SynergyTooltipModel
from gui.impl.pub import ViewImpl
from gui.pet_system.pet_ui_settings import PetUISettings
from gui.pet_system.synergy_helper import SynergyItem

class SynergyTooltip(ViewImpl):

    def __init__(self, petID, *args, **kwargs):
        settings = ViewSettings(R.views.mono.pet_system.tooltips.synergy_tooltip())
        settings.model = SynergyTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__petID = petID
        super(SynergyTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SynergyTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(SynergyTooltip, self)._onLoading(*args, **kwargs)
        progress = SynergyItem.getSynergyProgression(self.__petID)
        with self.viewModel.transaction() as model:
            model.setProgress(int(float(progress.cPoints) / progress.maxPoints * 100))

    def _finalize(self):
        super(SynergyTooltip, self)._finalize()
        PetUISettings.setLastSeenSynergyLevel(self.__petID, SynergyItem.getSynergyLevel(self.__petID))
