# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/battle/layout.py
import weakref
from account_helpers.AccountSettings import AccountSettings
from constants import ARENA_GUI_TYPE
from gui.Scaleform.daapi.view.battle.legacy.indicators import createDirectIndicator
from gui.app_loader import g_appLoader
from gui.battle_control import g_sessionProvider
from gui.battle_control.arena_info import player_format
from helpers import i18n
from helpers.aop import Aspect
from tutorial.control import g_tutorialWeaver
from tutorial.gui.Scaleform.battle.legacy import ScaleformLayout
from tutorial.logger import LOG_CURRENT_EXCEPTION, LOG_ERROR

class ShowBattleAspect(Aspect):

    def __init__(self):
        super(ShowBattleAspect, self).__init__()
        self.__skipFirstInvoke = True

    def atCall(self, cd):
        if self.__skipFirstInvoke:
            self.__skipFirstInvoke = False
            cd.avoid()


class MinimapDefaultSizeAspect(Aspect):

    def __init__(self, uiHolder):
        super(MinimapDefaultSizeAspect, self).__init__()
        minimap = getattr(uiHolder, 'minimap', None)
        if minimap:
            setSize = getattr(minimap, 'onSetSize', None)
            if setSize and callable(setSize):
                try:
                    setSize(0, AccountSettings.getSettingsDefault('minimapSize'))
                except TypeError:
                    LOG_CURRENT_EXCEPTION()

            else:
                LOG_ERROR('Minimap method "onSetSize" is not found', minimap)
        return

    def atCall(self, cd):
        if cd.function.__name__ == 'storeMinimapSize':
            cd.avoid()

    def atReturn(self, cd):
        result = cd.returned
        if cd.function.__name__ == 'getStoredMinimapSize':
            result = AccountSettings.getSettingsDefault('minimapSize')
            cd.change()
        return result


class TutorialFullNameFormatter(player_format.PlayerFullNameFormatter):

    @staticmethod
    def _normalizePlayerName(name):
        if name.startswith('#battle_tutorial:'):
            name = i18n.makeString(name)
        return name


class MinimapDelerator(object):
    __slots__ = ('__gui', '__entriesIDs', '__weakref__')

    def __init__(self, gui):
        super(MinimapDelerator, self).__init__()
        self.__gui = gui
        self.__entriesIDs = {}

    def clear(self):
        self.__gui = None
        self.__entriesIDs.clear()
        return

    def addTarget(self, markerID, position):
        minimap = self._getComponent()
        if minimap is None:
            return False
        elif markerID in self.__entriesIDs:
            return False
        else:
            entryID = minimap.addBackEntry(markerID, 'tutorialTarget', position[:], 'blue')
            self.__entriesIDs[markerID] = entryID
            return True

    def delTarget(self, markerID):
        if markerID not in self.__entriesIDs:
            return False
        else:
            minimap = self._getComponent()
            if minimap is None:
                return False
            minimap.removeBackEntry(self.__entriesIDs[markerID])
            return True

    def _getComponent(self):
        try:
            return self.__gui().minimap
        except AttributeError:
            LOG_ERROR('GUI component is not found')
            return None

        return None


class BattleLayout(ScaleformLayout):

    def __init__(self, swf):
        super(BattleLayout, self).__init__(swf)
        self.__dispatcher = None
        self.__minimap = None
        return

    def _resolveGuiRoot(self):
        proxy = None
        try:
            app = g_appLoader.getDefBattleApp()
            if not app:
                return
            proxy = weakref.proxy(app)
            self._guiRef = weakref.ref(app)
            self.__minimap = MinimapDelerator(self._guiRef)
            dispatcher = self.getDispatcher()
            if dispatcher is not None and proxy is not None:
                dispatcher.populateUI(proxy)
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

        return proxy

    def _setMovieView(self, movie):
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.findGUI(root=movie)
        super(BattleLayout, self)._setMovieView(movie)
        return

    def getDirectionIndicator(self):
        indicator = None
        try:
            indicator = createDirectIndicator()
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

        return indicator

    def init(self):
        result = super(BattleLayout, self).init()
        if result:
            g_sessionProvider.getCtx().setPlayerFullNameFormatter(TutorialFullNameFormatter())
            g_tutorialWeaver.weave('gui.app_loader', '_AppLoader', '^showBattle$', aspects=(ShowBattleAspect,))
            g_tutorialWeaver.weave('gui.Scaleform.Minimap', 'Minimap', '^getStoredMinimapSize|storeMinimapSize$', aspects=(MinimapDefaultSizeAspect(self.uiHolder),))
        return result

    def show(self):
        g_appLoader.showBattle()

    def clear(self):
        if self._guiRef is not None and self._guiRef() is not None and self._movieView is not None:
            self._movieView.clearStage()
        return

    def fini(self):
        if self.__minimap is not None:
            self.__minimap.clear()
            self.__minimap = None
        g_sessionProvider.getCtx().resetPlayerFullNameFormatter()
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.dispossessUI()
            dispatcher.clearGUI()
        super(BattleLayout, self).fini()
        return

    def getSceneID(self):
        pass

    def showMessage(self, text, lookupType=None):
        self.uiHolder.call('battle.VehicleMessagesPanel.ShowMessage', [lookupType, text, 'green'])

    def getMarkersManager(self):
        return getattr(self._guiRef(), 'markersManager', None)

    def getMinimapPlugin(self):
        return self.__minimap

    def setDispatcher(self, dispatcher):
        self.__dispatcher = dispatcher

    def getDispatcher(self):
        return self.__dispatcher

    def setTrainingPeriod(self, currentIdx, total):
        if self._movieView is not None:
            self._movieView.populateProgressBar(currentIdx, total)
        return

    def setTrainingProgress(self, mask):
        if self._movieView is not None:
            self._movieView.setTrainingProgressBar(mask)
        return

    def setChapterProgress(self, total, mask):
        if self._movieView is not None:
            self._movieView.setChapterProgressBar(total, mask)
        return
