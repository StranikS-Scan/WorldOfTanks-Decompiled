# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/mode_selector/story_mode_selector_item.py
from frameworks.wulf import WindowLayer
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from story_mode.gui.fade_in_out import UseStoryModeFading, UseHeaderNavigationImpossible
from story_mode.uilogging.story_mode.loggers import SelectorCardLogger
from wg_async import wg_async

class StoryModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ('_uiLogger',)

    def __init__(self, oldSelectorItem):
        super(StoryModeSelectorItem, self).__init__(oldSelectorItem)
        self._uiLogger = SelectorCardLogger()

    def _onInitializing(self):
        super(StoryModeSelectorItem, self)._onInitializing()
        self.viewModel.setDescription(backport.text(R.strings.sm_lobby.mode.story_mode.description()))
        self.viewModel.setStatusActive(backport.text(R.strings.sm_lobby.mode.story_mode.callToAction()))

    @wg_async
    def handleClick(self):
        self._uiLogger.logSelfClick()
        super(StoryModeSelectorItem, self).handleClick()
        if not self.viewModel.getIsSelected():
            yield self.animateSelection()

    @UseHeaderNavigationImpossible()
    @UseStoryModeFading(layer=WindowLayer.TOP_SUB_VIEW, hide=False)
    def animateSelection(self):
        pass

    def handleInfoPageClick(self):
        self._uiLogger.logInfoClick()
        super(StoryModeSelectorItem, self).handleInfoPageClick()
