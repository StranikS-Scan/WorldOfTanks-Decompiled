# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/tooltip_window.py
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from frameworks.wulf import Window, WindowFlags, View, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.advanced_animated_tooltip_content_model import AdvancedAnimatedTooltipContentModel
from gui.impl.gen.view_models.windows.advanced_tooltip_content_model import AdvancedTooltipContentModel
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel
from gui.impl.gen.view_models.windows.tooltip_window_model import TooltipWindowModel
from gui.impl.pub.window_view import WindowView
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.account_helpers.settings_core import ISettingsCore

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
        header = self.makeString(event.getArgument('header', ''))
        body = self.makeString(event.getArgument('body', ''))
        note = self.makeString(event.getArgument('note', ''))
        alert = self.makeString(event.getArgument('alert', ''))
        super(SimpleToolTipWindow, self).__init__(event, SimpleTooltipContent(header, body, note, alert), parent)

    @classmethod
    def makeString(cls, value):
        if not isinstance(value, basestring):
            value = cls.gui.resourceManager.getTranslatedText(int(value))
        return value


class SimpleTooltipContent(View):

    def __init__(self, header='', body='', note='', alert=''):
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


class AdvancedToolTipWindow(ToolTipWindow):
    __slots__ = ()

    def __init__(self, event, parent, normalContent, advancedContent):
        super(AdvancedToolTipWindow, self).__init__(event, AdvancedTooltipContent(normalContent, advancedContent), parent)


class AdvancedTooltipContent(View):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ()

    def __init__(self, normalContent, advancedContent):
        super(AdvancedTooltipContent, self).__init__(R.views.advandcedTooltipContent, ViewFlags.COMPONENT, AdvancedTooltipContentModel, normalContent, advancedContent)

    @property
    def viewModel(self):
        return super(AdvancedTooltipContent, self).getViewModel()

    def _initialize(self, normalContent, advancedContent):
        super(AdvancedTooltipContent, self)._initialize()
        disableAnim = self._getDisableAnimFlag()
        self.viewModel.hold()
        self.viewModel.setNormalContent(normalContent)
        self.viewModel.setAdvancedContent(advancedContent)
        self.viewModel.setShowAnim(not disableAnim)
        self.viewModel.commit()
        if not disableAnim:
            self._setDisableAnimFlag()

    def _getDisableAnimFlag(self):
        serverSettings = self.__settingsCore.serverSettings
        return serverSettings.getUIStorage().get(UI_STORAGE_KEYS.DISABLE_ANIMATED_TOOLTIP) == 1

    def _setDisableAnimFlag(self):
        serverSettings = self.__settingsCore.serverSettings
        serverSettings.saveInUIStorage({UI_STORAGE_KEYS.DISABLE_ANIMATED_TOOLTIP: 1})


class AdvancedAnimatedTooltipContent(View):
    __slots__ = ()

    def __init__(self, header='', body='', animation=''):
        super(AdvancedAnimatedTooltipContent, self).__init__(R.views.advandcedAnimatedTooltipContent, ViewFlags.COMPONENT, AdvancedAnimatedTooltipContentModel, header, body, animation)

    @property
    def viewModel(self):
        return super(AdvancedAnimatedTooltipContent, self).getViewModel()

    def _initialize(self, header, body, animation):
        super(AdvancedAnimatedTooltipContent, self)._initialize()
        self.viewModel.hold()
        self.viewModel.setBody(body)
        self.viewModel.setHeader(header)
        self.viewModel.setAnimation(animation)
        self.viewModel.commit()
