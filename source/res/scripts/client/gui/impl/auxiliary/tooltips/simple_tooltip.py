# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/tooltips/simple_tooltip.py
import typing
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.tooltips.simple_icon_tooltip_model import HeaderType
from gui.impl.lobby.common.tooltips.simple_icon_tooltip_view import SimpleIconTooltipView
from gui.impl.pub.tooltip_window import SimpleTooltipContent
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewEvent

def createSimpleTooltip(parent, event, header='', body=''):
    window = DecoratedTooltipWindow(parent=parent, content=SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), body=body, header=header))
    window.load()
    window.move(event.mouse.positionX, event.mouse.positionY)
    return window


def createSimpleIconTooltip(event):
    return SimpleIconTooltipView(event.getArgument('header', ''), event.getArgument('body', ''), event.getArgument('icon', ''), event.getArgument('headerType', HeaderType.NORMAL))
