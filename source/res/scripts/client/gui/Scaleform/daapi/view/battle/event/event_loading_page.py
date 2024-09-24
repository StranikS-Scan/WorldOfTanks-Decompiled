# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_loading_page.py
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.meta.EventLoadingMeta import EventLoadingMeta
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
PATH_BACKGROUNDS = '../maps/icons/event/loading/{0}_{1}.png'
LINKAGE_BACKGROUNDS = '{0}Page{1}UI'

class EventLoadingPage(EventLoadingMeta, IArenaLoadController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, settings):
        super(EventLoadingPage, self).__init__()
        self._tutorialPages = settings.get('tutorialPages', [])

    def _populate(self):
        super(EventLoadingPage, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        g_playerEvents.onDisconnected += self._onDisconnected
        listSmall = []
        listBig = []
        for pageId in self._tutorialPages:
            listSmall.append(self._getTutorialPageVO(pageId, False))
            listBig.append(self._getTutorialPageVO(pageId, True))

        self.as_setDataS({'lessonPagesSmallData': listSmall,
         'lessonPagesBigData': listBig,
         'navigationButtonsVisible': len(listSmall) > 1})

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        super(EventLoadingPage, self)._dispose()
        g_playerEvents.onDisconnected -= self._onDisconnected

    def updateSpaceLoadProgress(self, progress):
        self.as_updateProgressS(progress)

    def _onDisconnected(self):
        self.destroy()

    @staticmethod
    def _getTutorialPageVO(pageId, bigSize):
        pathBackgroundSize = 'big' if bigSize else 'small'
        linkageBackgroundSize = 'Big' if bigSize else 'Small'
        voSettings = {'background': PATH_BACKGROUNDS.format(pageId, pathBackgroundSize),
         'rendererLinkage': LINKAGE_BACKGROUNDS.format(pageId, linkageBackgroundSize)}
        return voSettings
