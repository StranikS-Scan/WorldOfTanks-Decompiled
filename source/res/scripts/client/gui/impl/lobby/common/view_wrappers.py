# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/view_wrappers.py
from functools import wraps
from gui.impl import backport
from gui.impl.gen import R

def createBackportTooltipDecorator():

    def decorator(method):

        @wraps(method)
        def wrapper(self, event, *args, **kwargs):
            if event.contentID != R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                return method(self, event, *args, **kwargs)
            else:
                tooltipData = self.getTooltipData(event)
                if tooltipData is None:
                    return
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                if window is None:
                    return
                window.load()
                return window

        return wrapper

    return decorator
