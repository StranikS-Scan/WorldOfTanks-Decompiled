# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/tooltips/simple_tooltip.py
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.pub.tooltip_window import SimpleTooltipContent

def createSimpleTooltip(parent, event, header='', body=''):
    window = DecoratedTooltipWindow(parent=parent, content=SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), body=body, header=header))
    window.load()
    window.move(event.mouse.positionX, event.mouse.positionY)
    return window
