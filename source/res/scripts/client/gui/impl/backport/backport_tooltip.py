# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/backport/backport_tooltip.py
from collections import namedtuple
from frameworks.wulf import ViewModel, Window, WindowFlags, WindowSettings, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.pub.window_view import WindowView
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
_STATE_TYPE_INFO = 'INFO'
TooltipData = namedtuple('TooltipData', ('tooltip', 'isSpecial', 'specialAlias', 'specialArgs', 'isWulfTooltip'))
TooltipData.__new__.__defaults__ = (None,
 False,
 None,
 None,
 False)

def createTooltipData(tooltip=None, isSpecial=False, specialAlias=None, specialArgs=None, isWulfTooltip=False):
    if specialArgs is None:
        specialArgs = ()
    return TooltipData(tooltip, isSpecial, specialAlias, specialArgs, isWulfTooltip)


def createAndLoadBackportTooltipWindow(parentWindow, tooltip=None, isSpecial=False, tooltipId=None, specialArgs=None):
    tooltipData = createTooltipData(tooltip=tooltip, isSpecial=isSpecial, specialAlias=tooltipId, specialArgs=specialArgs)
    window = BackportTooltipWindow(tooltipData, parentWindow)
    window.load()
    return window


def createBackportTooltipContent(specialAlias=None, specialArgs=None, isSpecial=True, tooltip=None, tooltipData=None):
    return _BackportTooltipContent(tooltipData or createTooltipData(tooltip, isSpecial, specialAlias, specialArgs or []))


class _BackportTooltipContent(ViewImpl):
    appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, tooltipData, event=None):
        settings = ViewSettings(R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent())
        settings.model = ViewModel()
        settings.args = (tooltipData, event)
        super(_BackportTooltipContent, self).__init__(settings)

    def _initialize(self, tooltipData, event=None):
        super(_BackportTooltipContent, self)._initialize()
        toolTipMgr = self.appLoader.getApp().getToolTipMgr()
        if toolTipMgr is not None:
            if tooltipData.isWulfTooltip:
                posX, posY = (0, 0) if not event else (event.mouse.positionX, event.mouse.positionY)
                toolTipMgr.onCreateWulfTooltip(tooltipData.specialAlias, tooltipData.specialArgs, posX, posY, parent=self.getParentWindow())
            elif tooltipData.isSpecial:
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

    def __init__(self, tooltipData, parent, event=None):
        settings = WindowSettings()
        settings.flags = WindowFlags.TOOLTIP
        settings.content = _BackportTooltipContent(tooltipData, event)
        settings.parent = parent
        super(BackportTooltipWindow, self).__init__(settings)


class DecoratedTooltipWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, content, parent=None, useDecorator=True):
        decorator = WindowView(layoutID=R.views.common.tooltip_window.tooltip_window.TooltipWindow()) if useDecorator else None
        super(DecoratedTooltipWindow, self).__init__(wndFlags=WindowFlags.TOOLTIP, decorator=decorator, content=content, parent=parent, areaID=R.areas.specific())
        return
