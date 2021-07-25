# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/loading_page.py
from gui.Scaleform.daapi.view.meta.MapsTrainingBattleLoadingMeta import MapsTrainingBattleLoadingMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_HTML_TEMPLATE_PATH = 'html_templates:mapsTraining/loadingScreen'

class MapsTrainingLoadingPage(MapsTrainingBattleLoadingMeta, IArenaLoadController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(MapsTrainingLoadingPage, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_LOADING, cursorVisible=True, enableAiming=False)
        g_eventBus.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        backgrounds = [ backport.image(R.images.gui.maps.icons.mapsTraining.dyn('tip_bg_0{}'.format(i))()) for i in range(1, 5) ]
        self.as_setDataS({'backgrounds': backgrounds})
        pageData = [ self.__getPageConfig(pageNum) for pageNum in range(1, 5) ]
        self.as_setDataPageS(pageData)

    @staticmethod
    def __getPageConfig(pageNum):
        pageData = {'rendererLinkage': 'MapsTrainingLoading{}PageBigUI'.format(pageNum),
         'header1Text': backport.text(R.strings.maps_training.loadingScreen.num(pageNum).title()),
         'header1AutoSize': 'center',
         'description1Text': backport.text(R.strings.maps_training.loadingScreen.num(pageNum).description()),
         'description1AutoSize': 'center'}
        return pageData

    def _dispose(self):
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        self.sessionProvider.removeArenaCtrl(self)
        g_eventBus.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        super(MapsTrainingLoadingPage, self)._dispose()

    def updateSpaceLoadProgress(self, progress):
        self.as_updateProgressS(progress)

    def __handleBattleLoading(self, event):
        if not event.ctx['isShown']:
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
