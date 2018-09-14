# Embedded file name: scripts/client/tutorial/gui/Scaleform/battle/layout.py
import weakref
from account_helpers.AccountSettings import AccountSettings
from gui import DEPTH_OF_Aim
from gui.Scaleform.Flash import Flash
from gui.app_loader import g_appLoader
from gui.battle_control import g_sessionProvider
from helpers import i18n
from helpers.aop import Aspect
from tutorial.control.battle.functional import IDirectionIndicator
from tutorial.control import g_tutorialWeaver
from tutorial.gui.Scaleform.battle.legacy import ScaleformLayout
from tutorial.logger import LOG_CURRENT_EXCEPTION, LOG_MEMORY, LOG_ERROR

class _DirectionIndicator(Flash, IDirectionIndicator):
    __SWF_FILE_NAME = 'DirectionIndicator.swf'
    __FLASH_CLASS = 'WGDirectionIndicatorFlash'
    __FLASH_MC_NAME = 'directionalIndicatorMc'
    __FLASH_SIZE = (680, 680)

    def __init__(self):
        Flash.__init__(self, self.__SWF_FILE_NAME, self.__FLASH_CLASS, [self.__FLASH_MC_NAME])
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.movie.scaleMode = 'NoScale'
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.flashSize = self.__FLASH_SIZE
        self.component.relativeRadius = 0.5
        self.__dObject = getattr(self.movie, self.__FLASH_MC_NAME, None)
        return

    def __del__(self):
        LOG_MEMORY('DirectionIndicator deleted')

    def setShape(self, shape):
        if self.__dObject:
            self.__dObject.setShape(shape)

    def setDistance(self, distance):
        if self.__dObject:
            self.__dObject.setDistance(distance)

    def setPosition(self, position):
        self.component.position3D = position

    def track(self, position):
        self.active(True)
        self.component.visible = True
        self.component.position3D = position

    def remove(self):
        self.__dObject = None
        self.close()
        return


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


def normalizePlayerName(pName):
    if pName.startswith('#battle_tutorial:'):
        pName = i18n.makeString(pName)
    return pName


class BattleLayout(ScaleformLayout):

    def __init__(self, swf):
        super(BattleLayout, self).__init__(swf)
        self.__dispatcher = None
        return

    def _resolveGuiRoot(self):
        proxy = None
        try:
            app = g_appLoader.getDefBattleApp()
            if not app:
                return
            proxy = weakref.proxy(app)
            self._guiRef = weakref.ref(app)
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

    def _getDirectionIndicator(self):
        indicator = None
        try:
            indicator = _DirectionIndicator()
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

        return indicator

    def init(self):
        result = super(BattleLayout, self).init()
        if result:
            g_sessionProvider.getCtx().setNormalizePlayerName(normalizePlayerName)
            g_tutorialWeaver.weave('gui.app_loader', '_AppLoader', '^showBattle$', aspects=(ShowBattleAspect,))
            g_tutorialWeaver.weave('gui.Scaleform.Minimap', 'Minimap', '^getStoredMinimapSize|storeMinimapSize$', aspects=(MinimapDefaultSizeAspect(self.uiHolder),))
        return result

    def show(self):
        g_appLoader.showBattle()

    def clear(self):
        if self._guiRef is not None and self._guiRef() is not None:
            if self._movieView is not None:
                self._movieView.clearStage()
        return

    def fini(self, isItemsRevert = True):
        g_sessionProvider.getCtx().resetNormalizePlayerName()
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.dispossessUI()
            dispatcher.clearGUI()
        super(BattleLayout, self).fini(isItemsRevert=isItemsRevert)
        return

    def getSceneID(self):
        return 'Battle'

    def showMessage(self, text, lookupType = None):
        self.uiHolder.call('battle.VehicleMessagesPanel.ShowMessage', [lookupType, text, 'green'])

    def getGuiRoot(self):
        try:
            root = g_appLoader.getDefBattleApp()
        except AttributeError:
            LOG_CURRENT_EXCEPTION()
            root = None

        return root

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
