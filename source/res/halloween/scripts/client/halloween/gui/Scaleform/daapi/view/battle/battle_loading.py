# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/battle_loading.py
import random
from helpers import dependency
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.Scaleform.daapi.view.meta.HWBattleLoadingMeta import HWBattleLoadingMeta
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
_R_IMAGES = R.images.halloween.gui.maps.icons.battleLoading.tips
_R_STRINGS = R.strings.hw_tips.loading

class BattleLoading(HWBattleLoadingMeta, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, _=None):
        super(BattleLoading, self).__init__()
        self._battleCtx = None
        self._arenaVisitor = None
        return

    def startControl(self, battleCtx, arenaVisitor):
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor

    def stopControl(self):
        self._battleCtx = None
        self._arenaVisitor = None
        return

    def updateSpaceLoadProgress(self, progress):
        self.as_updateProgressS(progress)

    def _populate(self):
        super(BattleLoading, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_LOADING, cursorVisible=True, enableAiming=False)
        g_eventBus.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self.as_setDataS(self._getData())

    def _dispose(self):
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        self.sessionProvider.removeArenaCtrl(self)
        g_eventBus.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        super(BattleLoading, self)._dispose()

    def _getData(self):
        index = random.randint(0, R.strings.hw_tips.loading.title.length() - 1)
        return {'currentPageIndex': index,
         'pages': self._getPages()}

    def _getPages(self):
        return [ {'title': backport.text(_R_STRINGS.title.num(i, default=R.invalid)()),
         'titlePart': backport.text(_R_STRINGS.title_part.num(i, default=R.invalid)()),
         'description': backport.text(_R_STRINGS.description.num(i, default=R.invalid)()),
         'background': backport.image(_R_IMAGES.dyn('halloween_{id}'.format(id=i), default=R.invalid)())} for i in xrange(1, R.strings.hw_tips.loading.title.length() + 1) ]

    def __handleBattleLoading(self, event):
        if not event.ctx['isShown']:
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
