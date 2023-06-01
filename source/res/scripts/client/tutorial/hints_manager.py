# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/hints_manager.py
import logging
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.tutorial import ITutorialLoader
from tutorial import settings
from tutorial.control.context import GlobalStorage
from tutorial.control.functional import FunctionalConditions
from tutorial.data.client_triggers import ClientTriggers
from tutorial.data.hints import HintProps
from tutorial.doc_loader.parsers import HintsParser
from tutorial.gui.Scaleform.hints.proxy import HintsProxy
_logger = logging.getLogger(__name__)
HINT_SHOWN_STATUS = 1
_MAX_ACTIVE_HINTS = 1
_DESCRIPTOR_PATH = '{0:>s}/once-only-hints.xml'.format(settings.DOC_DIRECTORY)

class HintsManager(object):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __tutorialLoader = dependency.descriptor(ITutorialLoader)
    __slots__ = ('_data', '_gui', '__activeHints', '__postponedHints', '__hintsWithClientTriggers')

    def __init__(self):
        super(HintsManager, self).__init__()
        self._data = None
        self._gui = None
        self.__activeHints = {}
        self.__postponedHints = []
        self.__hintsWithClientTriggers = None
        return

    def start(self):
        self.__loadHintsData()
        if self._data.getHintsCount() == 0:
            return False
        else:
            self.__hintsWithClientTriggers = None
            self._gui = HintsProxy()
            self._gui.onGUILoaded += self.__onGUILoaded
            self._gui.onHintClicked += self.__onGUIInput
            self._gui.onHintItemFound += self.__onItemFound
            self._gui.onHintItemLost += self.__onItemLost
            self._gui.onVisibleChanged += self.__onItemVisibleChanged
            self._gui.onEnabledChanged += self.__onItemEnabledChanged
            self._gui.onUpdateTutorialHints += self.__onUpdateTutorialHints
            self._gui.onImportantHintShowing += self.__onImportantHintShowing
            GlobalStorage.onSetValue += self.__onConditionFlagChanged
            self.__startSettingsListening()
            self._gui.loadConfig(self._data.getGuiFilePath())
            self._gui.init()
            return True

    def stop(self):
        if self._data is not None:
            self._data = None
        self.__postponedHints = []
        hintsIDs = self.__activeHints.keys()
        for itemID in hintsIDs:
            self.__hideHint(itemID)

        if self._gui is not None:
            self._gui.fini()
        self._gui = None
        self.__hintsWithClientTriggers = None
        GlobalStorage.onSetValue -= self.__onConditionFlagChanged
        self.__stopSettingsListening()
        return

    def __loadHintsData(self):
        _logger.debug('Hints are loading')
        shownHints = self.__settingsCore.serverSettings.getOnceOnlyHintsSettings()
        shownHints = [ key for key, value in shownHints.iteritems() if value == HINT_SHOWN_STATUS ]
        self._data = HintsParser.parse(_DESCRIPTOR_PATH, shownHints)

    def __setTriggeredComponents(self):
        self.__hintsWithClientTriggers = ClientTriggers()
        self.__hintsWithClientTriggers.setStates(self._data.getHints())
        self.__tutorialLoader.gui.setHintsWithClientTriggers(self.__hintsWithClientTriggers)

    def __showHint(self, hint, silent=False):
        if len(self.__activeHints) >= _MAX_ACTIVE_HINTS:
            hintID = hint['itemID']
            if hintID and hintID not in self.__postponedHints and hintID not in self.__activeHints:
                self.__postponedHints.append(hintID)
            return
        else:
            text = hint['text']
            uniqueID = hintID = hint['hintID']
            props = HintProps(uniqueID, hintID, hint['itemID'], text, hasBox=hint['hasBox'], arrow=hint['arrow'], padding=None, updateRuntime=hint['updateRuntime'], hideImmediately=hint['hideImmediately'], checkViewArea=hint['checkViewArea'])
            actionType = hint.get('ignoreOutsideClick')
            isActive = self._gui.showHint(props, actionType, silent)
            if isActive:
                self.__activeHints[hint['itemID']] = hint
            return

    def __hideHint(self, itemID, hintID=''):
        if itemID in self.__activeHints:
            hintID = hintID or self.__getActiveHintIdByItemId(itemID)
            self._gui.hideHint(hintID)
            if itemID in self.__activeHints:
                del self.__activeHints[itemID]
        self.__tryPushPostponed()

    def __onGUILoaded(self):
        self.__setTriggeredComponents()

    def __onGUIInput(self, event):
        itemID = event.getTargetID()
        if itemID in self.__activeHints:
            hintID = self.__getActiveHintIdByItemId(itemID)
            self.__stopOnceOnlyHint(itemID, hintID)
            self.__hideHint(itemID)
            if self._data.getHintsCount() == 0:
                self.stop()

    def __onItemFound(self, itemID, silent=False):
        if itemID not in self.__activeHints:
            hints = self._data.hintsForItem(itemID)
            for hint in hints:
                if not self.__hintsWithClientTriggers.checkState(itemID):
                    continue
                if self.__checkConditions(hint):
                    if itemID not in self.__activeHints:
                        self.__showHint(hint, silent)
                        break

    def __onItemLost(self, itemID):
        if itemID in self.__activeHints:
            hint = self.__activeHints[itemID]
            if hint['equalActions']:
                self.__stopOnceOnlyHint(itemID, hint['hintID'])
            self.__hideHint(itemID)

    def __onItemVisibleChanged(self, event):
        self.__updateItemState(event)

    def __onItemEnabledChanged(self, event):
        self.__updateItemState(event)

    def __updateItemState(self, event):
        itemID = event.getTargetID()
        state = event.getStateName()
        newStateValue = event.getStateValue()
        componentsWithClientTriggers = self.__hintsWithClientTriggers.getNeededStates()
        if itemID not in componentsWithClientTriggers or state not in componentsWithClientTriggers[itemID]:
            return
        self.__hintsWithClientTriggers.updateRealState(itemID, state, newStateValue)
        if not self.__hintsWithClientTriggers.isStateChanged(itemID, state):
            return
        if self.__hintsWithClientTriggers.checkState(itemID):
            hints = self._data.hintsForItem(itemID)
            for hint in hints:
                self.__hintsWithClientTriggers.addActiveHint(itemID)
                if self.__checkConditions(hint):
                    self.__showHint(hint)

        else:
            self.__hintsWithClientTriggers.removeActiveHint(itemID)
            self.__hideHint(itemID)

    def __getActiveHintIdByItemId(self, itemID):
        return self.__activeHints[itemID]['hintID']

    def __stopOnceOnlyHint(self, itemID, hintID):
        if self._data is None:
            return
        else:
            hints = self._data.hintsForItem(itemID)
            for hint in hints:
                if hint['hintID'] == hintID:
                    self.__stopSettingsListening()
                    self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({hintID: HINT_SHOWN_STATUS})
                    self.__startSettingsListening()
                    self._data.markAsShown(itemID, hintID)

            return

    @staticmethod
    def __checkConditions(hint):
        conditions = hint['conditions']
        return True if conditions is None else FunctionalConditions(conditions).allConditionsOk()

    def __startSettingsListening(self):
        self.__settingsCore.onOnceOnlyHintsChanged += self.__onSettingsChanged

    def __stopSettingsListening(self):
        self.__settingsCore.onOnceOnlyHintsChanged -= self.__onSettingsChanged

    def __onSettingsChanged(self, diff):
        diffKeys = diff.viewkeys()
        if diffKeys & set(OnceOnlyHints.ALL()):
            self._data.markHintsAsShown(diffKeys)
            for itemID, hint in self.__activeHints.items():
                hintID = hint['hintID']
                if hintID in diffKeys:
                    self.__hideHint(itemID, hintID)

            if self._data.getHintsCount() == 0:
                self.stop()
                return

    def __onConditionFlagChanged(self, flag, value):
        changedFlagHints = set()
        for itemID, hints in self._data.getHints().iteritems():
            for hint in hints:
                conditions = hint['conditions']
                if conditions is not None:
                    for condition in conditions:
                        if condition.getID() == flag:
                            changedFlagHints.add((itemID, condition.isPositiveState()))
                            break

        for changedFlagHint, isPositiveState in changedFlagHints:
            if value:
                if isPositiveState:
                    self.__onItemFound(changedFlagHint, silent=True)
                else:
                    self.__onItemLost(changedFlagHint)
            if isPositiveState:
                self.__onItemLost(changedFlagHint)
            self.__onItemFound(changedFlagHint, silent=True)

        return

    def __onUpdateTutorialHints(self, targetID, state, arguments=''):
        filteredHints = []
        for itemID, hints in self._data.getHints().iteritems():
            for hint in hints:
                if self.__filterHintByConditions(hint.get('conditions'), self.__limitedUIFilter, targetID, arguments):
                    filteredHints.append((itemID, hint))
                    break

        for itemID, hint in filteredHints:
            if state:
                self.__onItemFound(itemID, silent=True)
            if not self.__checkConditions(hint):
                self.__onItemLost(itemID)

    def __filterHintByConditions(self, conditions, filterFunction, *args):
        if conditions is None:
            return False
        else:
            for condition in conditions:
                if condition.getID() is None:
                    return self.__filterHintByConditions(condition.getConditionList(), filterFunction, *args)
                if filterFunction(condition, *args):
                    return True

            return False

    def __onImportantHintShowing(self, state):
        if state is False:
            self.__tryPushPostponed()

    def __tryPushPostponed(self):
        if self.__postponedHints:
            self.__onItemFound(self.__postponedHints.pop(), silent=True)

    @staticmethod
    def __limitedUIFilter(condition, targetID, arguments=''):
        return True if condition.getID() == targetID and (not arguments or condition.getArguments() == arguments) else False
