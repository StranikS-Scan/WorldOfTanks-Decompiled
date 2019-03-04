# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/hints_manager.py
import logging
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from tutorial import settings
from tutorial.control.functional import FunctionalConditions
from tutorial.data.hints import HintProps
from tutorial.data.client_triggers import ClientTriggers
from tutorial.doc_loader.parsers import HintsParser
from tutorial.gui.Scaleform.hints.proxy import HintsProxy
_logger = logging.getLogger(__name__)
HINT_SHOWN_STATUS = 1
_DESCRIPTOR_PATH = '{0:>s}/once-only-hints.xml'.format(settings.DOC_DIRECTORY)

class HintsManager(object):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('_data', '_gui', '__activeHints', '__hintsWithClientTriggers')

    def __init__(self):
        super(HintsManager, self).__init__()
        self._data = None
        self._gui = None
        self.__activeHints = {}
        self.__hintsWithClientTriggers = None
        return

    def start(self):
        self.__loadHintsData()
        if self._data.getHintsCount() == 0:
            return False
        else:
            self._gui = HintsProxy()
            self._gui.init()
            self._gui.loadConfig(self._data.getGuiFilePath())
            self.__hintsWithClientTriggers = None
            self.__setTriggeredComponents()
            self._gui.onHintClicked += self.__onGUIInput
            self._gui.onHintItemFound += self.__onItemFound
            self._gui.onHintItemLost += self.__onItemLost
            self._gui.onVisibleChanged += self.__onItemVisibleChanged
            self._gui.onEnabledChanged += self.__onItemEnabledChanged
            return True

    def stop(self):
        if self._data is not None:
            self._data = None
        hintsIDs = self.__activeHints.keys()
        for itemID in hintsIDs:
            self.__hideHint(itemID)

        if self._gui is not None:
            self._gui.fini()
        self._gui = None
        self.__hintsWithClientTriggers = None
        return

    def __loadHintsData(self):
        _logger.debug('Hints are loading')
        shownHints = self.__settingsCore.serverSettings.getOnceOnlyHintsSettings()
        shownHints = [ key for key, value in shownHints.iteritems() if value == HINT_SHOWN_STATUS ]
        self._data = HintsParser.parse(_DESCRIPTOR_PATH, shownHints)

    def __setTriggeredComponents(self):
        self.__hintsWithClientTriggers = ClientTriggers()
        self.__hintsWithClientTriggers.setStates(self._data.getHints())
        if self._gui.app is not None:
            self._gui.app.tutorialManager.setHintsWithClientTriggers(self.__hintsWithClientTriggers)
        return

    def __showHint(self, hint):
        text = hint['text']
        uniqueID = hintID = hint['hintID']
        props = HintProps(uniqueID, hintID, hint['itemID'], text, hasBox=True, arrow=hint['arrow'], padding=None, updateRuntime=hint['updateRuntime'], checkViewArea=hint['checkViewArea'])
        actionType = hint.get('ignoreOutsideClick')
        self._gui.showHint(props, actionType)
        self.__activeHints[hint['itemID']] = hint
        return

    def __hideHint(self, itemID):
        if itemID in self.__activeHints:
            hintID = self.__getActiveHintIdByItemId(itemID)
            self._gui.hideHint(hintID)
            del self.__activeHints[itemID]

    def __onGUIInput(self, event):
        itemID = event.getTargetID()
        if itemID in self.__activeHints:
            hintID = self.__getActiveHintIdByItemId(itemID)
            self.__hideHint(itemID)
            self.__stopOnceOnlyHint(itemID, hintID)
            if self._data.getHintsCount() == 0:
                self.stop()

    def __onItemFound(self, itemID):
        if itemID not in self.__activeHints:
            hints = self._data.hintsForItem(itemID)
            for hint in hints:
                if not self.__hintsWithClientTriggers.checkState(itemID):
                    continue
                if self.__checkConditions(hint):
                    if itemID not in self.__activeHints:
                        self.__showHint(hint)
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
                    self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({hintID: HINT_SHOWN_STATUS})
                    self._data.markAsShown(itemID, hintID)

            return

    @staticmethod
    def __checkConditions(hint):
        conditions = hint['conditions']
        return True if conditions is None else FunctionalConditions(conditions).allConditionsOk()
