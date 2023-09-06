# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/animated_battle_hint.py
from logging import getLogger
from animated_hints.constants import HintType, EventAction, LOGGER_NAME
from animated_hints.events import HintActionEvent
from gui.Scaleform.daapi.view.meta.AnimatedBattleHintMeta import AnimatedBattleHintMeta
from gui.Scaleform.genConsts.BATTLE_TOP_HINT_CONSTS import BATTLE_TOP_HINT_CONSTS
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
HINT_TYPE_TO_FRAME = {HintType.Move: BATTLE_TOP_HINT_CONSTS.FRAME_WASD,
 HintType.MoveTurret: BATTLE_TOP_HINT_CONSTS.FRAME_MOUSE_MOVE,
 HintType.Shoot: BATTLE_TOP_HINT_CONSTS.FRAME_MOUSE_CLICK,
 HintType.SniperLevel0: BATTLE_TOP_HINT_CONSTS.FRAME_MOUSE_SCROLL,
 HintType.SniperOnDistance: BATTLE_TOP_HINT_CONSTS.FRAME_MOUSE_SCROLL,
 HintType.AdvancedSniper: BATTLE_TOP_HINT_CONSTS.FRAME_MOUSE_SCROLL,
 HintType.WeakPoints: BATTLE_TOP_HINT_CONSTS.FRAME_PENETRATION}
_logger = getLogger(LOGGER_NAME)

class AnimatedBattleHint(AnimatedBattleHintMeta):

    def __init__(self):
        super(AnimatedBattleHint, self).__init__()
        self.__hideCallback = None
        self.__hintType = None
        self.__message = None
        self.__completed = None
        self.__frameId = None
        self.__handlers = {EventAction.Show: self.__showHint,
         EventAction.Hide: self.__hideHint,
         EventAction.Complete: self.__completeHint,
         EventAction.Close: self.__closeHint,
         EventAction.SetPenetration: self.__setPenetration}
        return

    def animFinish(self):
        if self.__hideCallback is not None:
            self.__hideCallback()
            self.__hideCallback = None
        return

    def _populate(self):
        super(AnimatedBattleHint, self)._populate()
        g_eventBus.addListener(HintActionEvent.EVENT_TYPE, self.__onEvent, scope=EVENT_BUS_SCOPE.BATTLE)

    def _destroy(self):
        super(AnimatedBattleHint, self)._destroy()
        g_eventBus.removeListener(HintActionEvent.EVENT_TYPE, self.__onEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__handlers.clear()

    def __onEvent(self, event):
        handler = self.__handlers.get(event.action)
        if handler:
            handler(event.ctx)
        else:
            _logger.error('Unexpected event action received: action = %s, ctx = %s', event.action, event.ctx)

    def __setPenetration(self, ctx):
        self.as_setPenetrationS(ctx['penetrationType'], ctx['isColorBlind'])

    def __showHint(self, ctx):
        self.__hideCallback = ctx['hideCallback']
        self.__hintType = ctx['hintType']
        self.__frameId = HINT_TYPE_TO_FRAME.get(self.__hintType, BATTLE_TOP_HINT_CONSTS.FRAME_EMPTY)
        self.__message = ctx['message']
        self.__completed = ctx['completed']
        self.as_showHintS(self.__frameId, self.__message, self.__completed)

    def __completeHint(self, ctx):
        if self.__frameId is not None and self.__message is not None:
            self.as_showHintS(self.__frameId, self.__message, True)
        return

    def __hideHint(self, ctx):
        self.as_hideHintS()

    def __closeHint(self, ctx):
        self.as_closeHintS()
        self.__hideCallback = None
        return
