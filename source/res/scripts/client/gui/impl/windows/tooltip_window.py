# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/windows/tooltip_window.py
from frameworks.wulf import Window, WindowFlags, View, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel
from gui.impl.gen.view_models.windows.tooltip_window_model import TooltipWindowModel
from gui.impl.windows.window_view import WindowView
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

class ToolTipWindow(Window):
    __slots__ = ()

    def __init__(self, event, content, parent):
        super(ToolTipWindow, self).__init__(wndFlags=WindowFlags.TOOL_TIP, decorator=WindowView(layoutID=R.views.tooltipWindow, viewModelClazz=TooltipWindowModel), content=content, parent=parent)
        self.toolTipModel.setX(event.mouse.positionX)
        self.toolTipModel.setY(event.mouse.positionY)

    @property
    def toolTipModel(self):
        return super(ToolTipWindow, self)._getDecoratorViewModel()


class SimpleToolTipWindow(ToolTipWindow):
    __slots__ = ()
    gui = dependency.descriptor(IGuiLoader)

    def __init__(self, event, parent):
        header = self.makeString(event.getArgument('header'))
        if event.hasArgument('body'):
            body = self.makeString(event.getArgument('body'))
        else:
            body = ''
        if event.hasArgument('note'):
            note = self.makeString(event.getArgument('note'))
        else:
            note = ''
        if event.hasArgument('alert'):
            alert = self.makeString(event.getArgument('alert'))
        else:
            alert = ''
        super(SimpleToolTipWindow, self).__init__(event, SimpleTooltipContent(header, body, note, alert), parent)

    @classmethod
    def makeString(cls, value):
        if not isinstance(value, basestring):
            value = cls.gui.resourceManager.getTranslatedText(int(value))
        return value


class SimpleTooltipContent(View):

    def __init__(self, header, body, note, alert):
        super(SimpleTooltipContent, self).__init__(R.views.simpleTooltipContent, ViewFlags.COMPONENT, SimpleTooltipContentModel, header, body, note, alert)

    @property
    def viewModel(self):
        return super(SimpleTooltipContent, self).getViewModel()

    def _initialize(self, header, body, note, alert):
        super(SimpleTooltipContent, self)._initialize()
        self.viewModel.hold()
        self.viewModel.setHeader(header)
        self.viewModel.setBody(body)
        self.viewModel.setNote(note)
        self.viewModel.setAlert(alert)
        self.viewModel.commit()
