# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_loading_page.py
from PlayerEvents import g_playerEvents
from gui.impl import backport
from gui.impl.gen import R
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
        defaultValues = {}
        isHunter = True
        for index in range(len(self._tutorialPages)):
            if self._tutorialPages[index].startswith('eventBoss'):
                isHunter = False
            key = 'header' + str(index + 1)
            text = key + 'Text'
            defaultValues[key + 'AutoSize'] = 'left'
            if isHunter:
                defaultValues[text] = backport.text(R.strings.event.loading.hunter.header.dyn('c_' + str(index + 1))())
            defaultValues[text] = backport.text(R.strings.event.loading.boss.header.dyn('c_' + str(index + 1))())

        for pageId in self._tutorialPages:
            smallProps = self._getTutorialPageVO(pageId, False)
            smallProps.update(defaultValues)
            bigProps = self._getTutorialPageVO(pageId, True)
            bigProps.update(defaultValues)
            listSmall.append(smallProps)
            listBig.append(bigProps)

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
