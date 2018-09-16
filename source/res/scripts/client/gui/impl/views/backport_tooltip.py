# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/views/backport_tooltip.py
from collections import namedtuple
from frameworks.wulf import ViewFlags, ViewModel, Window, WindowFlags
from gui.impl.views.view_impl import ViewImpl
from gui.impl.gen import R
from gui.app_loader import g_appLoader
_STATE_TYPE_INFO = 'INFO'
TooltipData = namedtuple('TooltipData', ['tooltip',
 'isSpecial',
 'specialAlias',
 'specialArgs'])

class _BackportTooltipContent(ViewImpl):
    __slots__ = ()

    def __init__(self, tooltipData):
        super(_BackportTooltipContent, self).__init__(R.views.backportTooltipContent, ViewFlags.VIEW, ViewModel, tooltipData)

    def _initialize(self, tooltipData):
        super(_BackportTooltipContent, self)._initialize()
        toolTipMgr = g_appLoader.getApp().getToolTipMgr()
        if toolTipMgr is not None:
            if tooltipData.isSpecial:
                toolTipMgr.onCreateTypedTooltip(tooltipData.specialAlias, tooltipData.specialArgs, _STATE_TYPE_INFO)
            else:
                toolTipMgr.onCreateComplexTooltip(tooltipData.tooltip, _STATE_TYPE_INFO)
        return

    def _finalize(self):
        toolTipMgr = g_appLoader.getApp().getToolTipMgr()
        if toolTipMgr is not None:
            toolTipMgr.hide()
        return


class BackportTooltipWindow(Window):
    __slots__ = ()

    def __init__(self, tooltipData, parent):
        super(BackportTooltipWindow, self).__init__(wndFlags=WindowFlags.TOOL_TIP, decorator=None, content=_BackportTooltipContent(tooltipData), parent=parent)
        return
