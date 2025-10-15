# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/progress_token_tooltip.py
from frameworks.wulf import ViewSettings
from portal.gui.impl.gen.view_models.views.lobby.tooltips.progress_token_tooltip_model import ProgressTokenTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class ProgressTokenTooltip(ViewImpl):
    __slots__ = ('_isToken', '_isCompleted', '_currentPoints', '_nextLevelPoints')

    def __init__(self, isToken, isComplete, currentPoints, nextLevelPoints):
        settings = ViewSettings(R.views.portal.lobby.tooltips.ProgressTokenTooltip())
        settings.model = ProgressTokenTooltipModel()
        self._isToken = isToken
        self._isCompleted = isComplete
        self._currentPoints = currentPoints
        self._nextLevelPoints = nextLevelPoints
        super(ProgressTokenTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ProgressTokenTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ProgressTokenTooltip, self)._onLoading(*args, **kwargs)
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            self.__fillModel(vm)

    def __fillModel(self, model):
        model.setIsTokenTooltip(self._isToken)
        model.setInProgress(True)
        model.setIsCompleted(self._isCompleted)
        model.setCurrentPoints(self._currentPoints)
        model.setNextLevelPoints(self._nextLevelPoints)
