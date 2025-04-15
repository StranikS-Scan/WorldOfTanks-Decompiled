# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/icon/icon_set.py
import typing
from gui.impl.dialogs.dialog_template_tooltip import DialogTemplateTooltip
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.sub_views.icon_set_view_model import IconSetViewModel, IconPositionLogicEnum
from gui.impl.gen.view_models.views.dialogs.sub_views.icon_view_model import IconViewModel
from gui.impl.gen_utils import INVALID_RES_ID
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
if typing.TYPE_CHECKING:
    from typing import List, Optional
    from frameworks.wulf import Array

def _addIconResIdsToViewModelArray(source, target):
    if source:
        for resID in source:
            if resID != INVALID_RES_ID:
                iconVM = IconViewModel()
                iconVM.setPath(resID)
                target.addViewModel(iconVM)


class IconSet(ViewImpl):
    __slots__ = ('__tooltip',)
    _VIEW_MODEL = IconSetViewModel

    def __init__(self, iconResID, backgroundResIDList=None, overlayResIDList=None, layoutID=None, iconPositionLogic=IconPositionLogicEnum.CENTREDANDTHROUGHCONTENT.value, isBottomPushingDown=True, tooltip=None):
        settings = ViewSettings(layoutID or R.views.dialogs.sub_views.icon.IconSet())
        viewModel = settings.model = self._VIEW_MODEL()
        settings.kwargs = {'iconResID': iconResID,
         'backgroundResIDList': backgroundResIDList,
         'overlayResIDList': overlayResIDList,
         'iconPositionLogic': iconPositionLogic,
         'isBottomPushingDown': isBottomPushingDown}
        super(IconSet, self).__init__(settings)
        self.__tooltip = tooltip or DialogTemplateTooltip()
        self.__tooltip.initialize(viewModel.tooltip)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            if self.__tooltip.tooltipFactory is not None:
                return self.__tooltip.tooltipFactory()
        return super(IconSet, self).createToolTipContent(event, contentID)

    def _onLoading(self, iconResID, backgroundResIDList, overlayResIDList, iconPositionLogic, isBottomPushingDown, *args, **kwargs):
        super(IconSet, self)._onLoading(*args, **kwargs)
        viewModel = self.getViewModel()
        viewModel.setIsBottomPushingDown(isBottomPushingDown)
        viewModel.setIconPositionLogic(iconPositionLogic)
        if iconResID != INVALID_RES_ID:
            viewModel.icon.setPath(iconResID)
        _addIconResIdsToViewModelArray(backgroundResIDList, viewModel.getBackgrounds())
        _addIconResIdsToViewModelArray(overlayResIDList, viewModel.getOverlays())

    def _finalize(self):
        self.__tooltip.dispose()
        self.__tooltip = None
        super(IconSet, self)._finalize()
        return

    def _addIconResIdsToViewModelArray(self, source, target):
        if source:
            for resID in source:
                if resID != INVALID_RES_ID:
                    iconVM = IconViewModel()
                    iconVM.setPath(resID)
                    target.addViewModel(iconVM)
