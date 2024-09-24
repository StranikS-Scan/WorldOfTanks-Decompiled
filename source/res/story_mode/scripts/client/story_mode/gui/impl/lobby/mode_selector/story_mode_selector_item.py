# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/mode_selector/story_mode_selector_item.py
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem, getInfoPageKey
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from story_mode.account_settings import isWelcomeScreenSeen
from story_mode.gui.fade_in_out import UseStoryModeFading, UseHeaderNavigationImpossible
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.loggers import SelectorCardLogger
from story_mode_common.configs.story_mode_missions import missionsSchema
from story_mode_common.configs.story_mode_settings import settingsSchema
from wg_async import wg_async
_rMode = R.strings.sm_lobby.mode
MODE_SELECTOR_CARD_EVENT_PRIORITY = 40
EVENT_SUFFIX = '_event'

class StoryModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ('_uiLogger', '_storyModeCtrl')
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, oldSelectorItem):
        super(StoryModeSelectorItem, self).__init__(oldSelectorItem)
        self._uiLogger = SelectorCardLogger()

    def _setResourcesFolderName(self):
        folderName = self.modeName + self.eventSuffix
        if R.images.gui.maps.icons.mode_selector.mode.dyn(folderName).isValid():
            self.viewModel.setResourcesFolderName(folderName)

    def _getModeStringsRoot(self):
        return _rMode.dyn(self.modeName + self.eventSuffix)

    def _setModeDescription(self, modeStrings):
        description = modeStrings.dyn('callToAction')
        self.viewModel.setDescription(backport.text(description()) if description.exists() else '')

    def _getPositionByModeName(self):
        settings = settingsSchema.getModel()
        return (ModeSelectorColumns.COLUMN_2, MODE_SELECTOR_CARD_EVENT_PRIORITY) if settings is not None and settings.isModeSelectorCardBig else super(StoryModeSelectorItem, self)._getPositionByModeName()

    @wg_async
    def handleClick(self):
        self._uiLogger.logSelfClick()
        super(StoryModeSelectorItem, self).handleClick()
        if self._storyModeCtrl.isNewNeededForNewbies():
            self._storyModeCtrl.setNewForNewbiesSeen()
        if not self.viewModel.getIsSelected():
            yield self.animateSelection()

    @UseHeaderNavigationImpossible()
    @UseStoryModeFading(layer=WindowLayer.TOP_SUB_VIEW, hide=False)
    def animateSelection(self):
        pass

    def handleInfoPageClick(self):
        self._uiLogger.logInfoClick()
        url = self._urlProcessing(GUI_SETTINGS.lookup(getInfoPageKey(self.modeName)))
        showBrowserOverlayView(url, VIEW_ALIAS.STORY_MODE_WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def _isNewLabelVisible(self):
        missionsSettings = missionsSchema.getModel()
        return True if missionsSettings is not None and missionsSettings.isEventEnabled and not isWelcomeScreenSeen() or self._storyModeCtrl.isNewNeededForNewbies() else super(StoryModeSelectorItem, self)._isNewLabelVisible()

    @property
    def eventSuffix(self):
        settings = settingsSchema.getModel()
        return EVENT_SUFFIX if settings is not None and settings.isModeSelectorCardBig else ''
