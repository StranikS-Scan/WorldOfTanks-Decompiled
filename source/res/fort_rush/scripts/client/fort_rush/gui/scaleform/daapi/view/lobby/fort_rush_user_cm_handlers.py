# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/lobby/fort_rush_user_cm_handlers.py
from __future__ import absolute_import
import adisp
from fort_rush.gui.fort_rush_gui_constants import PREBATTLE_ACTION_NAME
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from fort_rush_common.fort_rush_constants import PREBATTLE_TYPE
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.rally.UnitUserCMHandler import UnitUserCMHandler
from gui.Scaleform.daapi.view.lobby.lobby_constants import USER
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import PrbAction
from helpers import dependency
from shared_utils import findFirst
CREATE_FORT_RUSH_SQUAD = 'createFortRushSquad'

@adisp.adisp_process
@dependency.replace_none_kwargs(ctrl=IFortRushBattleController)
def createFortRushSquadHandler(cm, ctrl=None):
    if not ctrl.isEventPrbActive():
        action = PrbAction(PREBATTLE_ACTION_NAME.FORT_RUSH_SQUAD, accountsToInvite=[cm.databaseID])
        yield ctrl.prbDispatcher.doSelectAction(action, fadeCtx={'layer': WindowLayer.OVERLAY,
         'waitForLayoutReady': R.views.fort_rush.mono.lobby.hangar()})
    else:
        arenaUniqueID = getattr(cm, 'arenaUniqueID', None)
        cm.doSelect(PREBATTLE_ACTION_NAME.FORT_RUSH_SQUAD, (cm.databaseID,), extData={'arenaUniqueID': arenaUniqueID})
    return


@dependency.replace_none_kwargs(ctrl=IFortRushBattleController)
def fortRushSquadOptionBuilder(cm, options, userCMInfo, ctrl=None):
    if userCMInfo.isIgnored or cm.isSquadCreator() or cm.prbDispatcher is None or userCMInfo.isBot or isinstance(cm, UnitUserCMHandler):
        return options
    else:
        if ctrl.isAvailable() and not cm.isSquadAlreadyCreated(PREBATTLE_TYPE.FORT_RUSH):
            canCreate = not cm.prbEntity.isInQueue()
            item = cm.makeItem(CREATE_FORT_RUSH_SQUAD, backport.text(R.strings.menu.contextMenu.createFortRushSquad()), optInitData={'enabled': canCreate,
             'textColor': 13347959})
            squadItem = findFirst(lambda it: it['id'] == USER.CREATE_SQUAD, options)
            inviteItem = findFirst(lambda it: it['id'] == USER.INVITE, options)
            copyToClipboardItem = findFirst(lambda it: it['id'] == USER.COPY_TO_CLIPBOARD, options)
            if squadItem:
                options.insert(options.index(squadItem) + 1, item)
            elif inviteItem:
                options.insert(options.index(inviteItem), item)
            elif copyToClipboardItem:
                options.insert(options.index(copyToClipboardItem) + 1, item)
        return options
