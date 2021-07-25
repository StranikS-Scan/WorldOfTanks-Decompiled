# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/points_info_tooltip_view.py
from helpers import dependency
from items.components.detachment_constants import POINTS_PER_LEVEL, NO_DETACHMENT_ID
from skeletons.gui.detachment import IDetachmentCache
from crew2 import settings_globals
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.points_info_tooltip_model import PointsInfoTooltipModel
from gui.impl.pub import ViewImpl
from uilogging.detachment.loggers import DynamicGroupTooltipLogger

class PointInfoTooltipView(ViewImpl):
    __slots__ = ('__state', '__isClickable', '__detDescr', '__freePoints')
    detachmentCache = dependency.descriptor(IDetachmentCache)
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, layoutID, isClickable=False, state=PointsInfoTooltipModel.DEFAULT, detachmentID=NO_DETACHMENT_ID, detachmentDescr=None, freePoints=True, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = PointsInfoTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__state = state
        self.__isClickable = isClickable
        if detachmentID != NO_DETACHMENT_ID:
            self.__detDescr = self.detachmentCache.getDetachment(detachmentID).getDescriptor()
        else:
            self.__detDescr = detachmentDescr
        self.__freePoints = freePoints
        super(PointInfoTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PointInfoTooltipView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PointInfoTooltipView, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(PointInfoTooltipView, self)._finalize()

    def _onLoading(self):
        super(PointInfoTooltipView, self)._onLoading()
        self.__fillModel()

    def __fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setState(self.__state)
            vm.setIsClickable(self.__isClickable)
            detDescr = self.__detDescr
            if detDescr:
                vm.setPoints(detDescr.level - detDescr.getBuildLevel() if self.__freePoints else 0)
                vm.setMaximumPoints(detDescr.progression.maxLevel)
            vm.setPointsPerLevel(POINTS_PER_LEVEL)
            vm.setBonusPoints(settings_globals.g_instructorSettingsProvider.classes.maxBonusPoints)
