# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/detachment_preview_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_with_points_model import DetachmentWithPointsModel
from gui.impl.pub import ViewImpl
from gui.impl.auxiliary.detachment_helper import fillDetachmentWithPointsModel

class DetachmentPreviewTooltip(ViewImpl):
    __slots__ = ('__vehicle', '__detDescr', '__instrDescrs', '__skinID')

    def __init__(self, vehicle, detDescr, instrDescrs, skinID, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.DetachmentPreviewTooltip())
        settings.model = DetachmentWithPointsModel()
        super(DetachmentPreviewTooltip, self).__init__(settings)
        self.__vehicle = vehicle
        self.__detDescr = detDescr
        self.__instrDescrs = instrDescrs
        self.__skinID = skinID
        settings.args = args
        settings.kwargs = kwargs

    @property
    def viewModel(self):
        return super(DetachmentPreviewTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DetachmentPreviewTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            fillDetachmentWithPointsModel(model, self.__detDescr, self.__skinID, self.__instrDescrs, self.__vehicle)
