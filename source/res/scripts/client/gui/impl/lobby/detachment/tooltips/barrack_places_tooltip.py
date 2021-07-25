# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/barrack_places_tooltip.py
from frameworks.wulf import ViewSettings
from goodies.goodie_constants import RECERTIFICATION_FORM_ID
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.barrack_places_tooltip_model import BarrackPlacesTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.goodies import IGoodiesCache
from helpers import dependency

class BarrackPlacesTooltip(ViewImpl):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.BarrackPlacesTooltip())
        settings.model = BarrackPlacesTooltipModel()
        super(BarrackPlacesTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BarrackPlacesTooltip, self).getViewModel()

    def _onLoading(self):
        super(BarrackPlacesTooltip, self)._onLoading()
        self.__updatePersonalInfo()

    def __updatePersonalInfo(self):
        with self.viewModel.transaction() as vm:
            activeGoodies = self.goodiesCache.getRecertificationForms(REQ_CRITERIA.DEMOUNT_KIT.IN_ACCOUNT)
            recertificationForms = activeGoodies.get(RECERTIFICATION_FORM_ID)
            formsCount = recertificationForms.count if recertificationForms else 0
            vm.setFormsCount(formsCount)
