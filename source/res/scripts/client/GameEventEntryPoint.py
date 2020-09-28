# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/GameEventEntryPoint.py
from ClientSelectableObject import ClientSelectableObject
from adisp import process
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME

class GameEventEntryPoint(ClientSelectableObject):

    def onMouseClick(self):
        super(GameEventEntryPoint, self).onMouseClick()
        self.__doSelectAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE)

    @process
    def __doSelectAction(self, actionName):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            yield dispatcher.doSelectAction(PrbAction(actionName))
        return
