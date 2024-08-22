# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/qualification_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.qualification_tooltip_view_model import QualificationTooltipViewModel
from gui.impl.pub import ViewImpl

class QualificationTooltip(ViewImpl):
    __slots__ = ('_qualificationIndex', '_roleName', '_isBonusQualification', '_isFemale')

    def __init__(self, qualificationIndex, roleName, isBonusQualification, isFemale):
        self._roleName = roleName
        self._isFemale = isFemale
        self._qualificationIndex = qualificationIndex
        self._isBonusQualification = isBonusQualification
        settings = ViewSettings(R.views.lobby.crew.tooltips.QualificationTooltip(), model=QualificationTooltipViewModel())
        super(QualificationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(QualificationTooltip, self).getViewModel()

    def _onLoading(self):
        with self.viewModel.transaction() as vm:
            vm.setRoleName(self._roleName)
            vm.setIsFemale(self._isFemale)
            vm.setQualificationIndex(self._qualificationIndex + 1)
            vm.setIsBonusQualification(self._isBonusQualification)
