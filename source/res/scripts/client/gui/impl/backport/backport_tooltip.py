# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/backport/backport_tooltip.py
from collections import namedtuple
from frameworks.wulf import ViewFlags, ViewModel, Window, WindowFlags
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
_STATE_TYPE_INFO = 'INFO'
TooltipData = namedtuple('TooltipData', ('tooltip', 'isSpecial', 'specialAlias', 'specialArgs'))

def createTooltipData(tooltip=None, isSpecial=False, specialAlias=None, specialArgs=None):
    return TooltipData(tooltip, isSpecial, specialAlias, specialArgs)


class _BackportTooltipContent(ViewImpl):
    appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, tooltipData):
        super(_BackportTooltipContent, self).__init__(R.views.backportTooltipContent(), ViewFlags.VIEW, ViewModel, tooltipData)

    def _initialize(self, tooltipData):
        super(_BackportTooltipContent, self)._initialize()
        toolTipMgr = self.appLoader.getApp().getToolTipMgr()
        if toolTipMgr is not None:
            if tooltipData.isSpecial:
                toolTipMgr.onCreateTypedTooltip(tooltipData.specialAlias, tooltipData.specialArgs, _STATE_TYPE_INFO)
            else:
                toolTipMgr.onCreateComplexTooltip(tooltipData.tooltip, _STATE_TYPE_INFO)
        return

    def _finalize(self):
        toolTipMgr = self.appLoader.getApp().getToolTipMgr()
        if toolTipMgr is not None:
            toolTipMgr.hide()
        return


class BackportTooltipWindow(Window):
    __slots__ = ()

    def __init__(self, tooltipData, parent):
        super(BackportTooltipWindow, self).__init__(wndFlags=WindowFlags.TOOLTIP, decorator=None, content=_BackportTooltipContent(tooltipData), parent=parent)
        return
