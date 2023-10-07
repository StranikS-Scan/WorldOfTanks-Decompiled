# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/tooltip_window.py
from frameworks.wulf import WindowFlags, View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.advanced_animated_tooltip_content_model import AdvancedAnimatedTooltipContentModel
from gui.impl.gen.view_models.windows.advanced_tooltip_content_model import AdvancedTooltipContentModel
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel
from gui.impl.pub.window_impl import WindowImpl
from gui.impl.pub.window_view import WindowView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader

class ToolTipWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, event, content, parent):
        if event is not None and event.decoratorID:
            decorator = WindowView(layoutID=event.decoratorID)
        else:
            decorator = None
        super(ToolTipWindow, self).__init__(wndFlags=WindowFlags.TOOLTIP, decorator=decorator, content=content, parent=parent, areaID=R.areas.specific())
        return


class SimpleToolTipWindow(ToolTipWindow):
    __slots__ = ()
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, event, parent):
        header = self.makeString(event.getArgument('header', ''))
        body = self.makeString(event.getArgument('body', ''))
        note = self.makeString(event.getArgument('note', ''))
        alert = self.makeString(event.getArgument('alert', ''))
        super(SimpleToolTipWindow, self).__init__(event, SimpleTooltipContent(event.contentID, header, body, note, alert), parent)

    @classmethod
    def makeString(cls, value):
        if not isinstance(value, basestring):
            value = cls.__gui.resourceManager.getTranslatedText(int(value))
        return value


class SimpleTooltipContent(View):
    __slots__ = ()

    def __init__(self, contentID=R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), header='', body='', note='', alert=''):
        settings = ViewSettings(contentID)
        settings.model = SimpleTooltipContentModel()
        settings.args = (header,
         body,
         note,
         alert)
        super(SimpleTooltipContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SimpleTooltipContent, self).getViewModel()

    def _onLoading(self, header, body, note, alert):
        with self.viewModel.transaction() as tx:
            tx.setHeader(header)
            tx.setBody(body)
            tx.setNote(note)
            tx.setAlert(alert)


class AdvancedToolTipWindow(ToolTipWindow):
    __slots__ = ()

    def __init__(self, event, parent, normalContent, advancedContent):
        super(AdvancedToolTipWindow, self).__init__(event, AdvancedTooltipContent(normalContent, advancedContent), parent)


class AdvancedTooltipContent(View):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ()

    def __init__(self, normalContent, advancedContent):
        settings = ViewSettings(R.views.common.tooltip_window.advanced_tooltip_content.AdvandcedTooltipContent())
        settings.model = AdvancedTooltipContentModel()
        settings.args = (normalContent, advancedContent)
        super(AdvancedTooltipContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdvancedTooltipContent, self).getViewModel()

    def _onLoading(self, normalContent, advancedContent):
        super(AdvancedTooltipContent, self)._initialize()
        disableAnim = self._getDisableAnimFlag()
        self.viewModel.setShowAnim(not disableAnim)
        self.setChildView(R.dynamic_ids.tooltip.normal_content(), normalContent)
        self.setChildView(R.dynamic_ids.tooltip.advanced_content(), advancedContent)
        if not disableAnim:
            self._setDisableAnimFlag()

    def _getDisableAnimFlag(self):
        return self.__settingsCore.serverSettings.getDisableAnimTooltipFlag()

    def _setDisableAnimFlag(self):
        self.__settingsCore.serverSettings.setDisableAnimTooltipFlag()


class AdvancedAnimatedTooltipContent(View):
    __slots__ = ()

    def __init__(self, header='', body='', animation=''):
        settings = ViewSettings(R.views.common.tooltip_window.advanced_tooltip_content.AdvandcedAnimatedTooltipContent())
        settings.model = AdvancedAnimatedTooltipContentModel()
        settings.args = (header, body, animation)
        super(AdvancedAnimatedTooltipContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdvancedAnimatedTooltipContent, self).getViewModel()

    def _onLoading(self, header, body, animation):
        super(AdvancedAnimatedTooltipContent, self)._initialize()
        with self.viewModel.transaction() as tx:
            tx.setBody(body)
            tx.setHeader(header)
            tx.setAnimation(animation)
