# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/mode_selector/story_mode_selector_item.py
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from story_mode.account_settings import isWelcomeScreenSeen
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.loggers import SelectorCardLogger
from story_mode_common.configs.story_mode_missions import missionsSchema
from story_mode_common.configs.story_mode_settings import settingsSchema
_rMode = R.strings.sm_lobby.mode
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
        return (settings.modeSelectorCardColumn, settings.modeSelectorCardPriority) if settings is not None else super(StoryModeSelectorItem, self)._getPositionByModeName()

    def handleClick(self):
        self._uiLogger.logSelfClick()
        super(StoryModeSelectorItem, self).handleClick()

    def handleInfoPageClick(self):
        self._uiLogger.logInfoClick()
        url = self._urlProcessing(GUI_SETTINGS.lookup(self._storyModeCtrl.storyModeInfoPageKey))
        showBrowserOverlayView(url, VIEW_ALIAS.STORY_MODE_WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def _isInfoIconVisible(self):
        return GUI_SETTINGS.lookup(self._storyModeCtrl.storyModeInfoPageKey) is not None

    def _isNewLabelVisible(self):
        missionsSettings = missionsSchema.getModel()
        return True if missionsSettings is not None and missionsSettings.isEventEnabled and not isWelcomeScreenSeen() or self._storyModeCtrl.isNewNeededForNewbies() else super(StoryModeSelectorItem, self)._isNewLabelVisible()

    @property
    def eventSuffix(self):
        missionsSettings = missionsSchema.getModel()
        return EVENT_SUFFIX if missionsSettings is not None and missionsSettings.isEventEnabled else ''
