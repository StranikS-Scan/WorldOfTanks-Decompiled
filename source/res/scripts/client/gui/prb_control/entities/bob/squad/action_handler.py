# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/bob/squad/action_handler.py
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.settings import FUNCTIONAL_FLAG
from helpers import dependency
from skeletons.gui.game_control import IBobController

class BobSquadActionsHandler(SquadActionsHandler):
    bobCtrl = dependency.descriptor(IBobController)

    def executeInit(self, ctx):
        if not self.bobCtrl.isRegistered():
            SystemMessages.pushMessage(backport.text(R.strings.bob.systemMessage.squad.notRegistered()), type=SystemMessages.SM_TYPE.Error)
            return FUNCTIONAL_FLAG.UNDEFINED
        return super(BobSquadActionsHandler, self).executeInit(ctx)
