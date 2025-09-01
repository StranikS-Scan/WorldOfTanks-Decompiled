# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/ls_user_cm_handlers.py
import adisp
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.rally.UnitUserCMHandler import UnitUserCMHandler
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import USER
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import PrbAction
from last_stand.gui.ls_gui_constants import PREBATTLE_ACTION_NAME
from last_stand.gui.shared.event_dispatcher import showHangar
from last_stand.skeletons.ls_controller import ILSController
from last_stand_common.last_stand_constants import PREBATTLE_TYPE
from helpers import dependency
from shared_utils import findFirst
CREATE_LS_SQUAD = 'createLSSquad'
EXCLUDE_CM_CLASS = (UnitUserCMHandler,)
HIGHLIGHT_COLOR = 13347959

@adisp.adisp_process
@dependency.replace_none_kwargs(ctrl=ILSController)
def createLSSquadHandler(cm, ctrl=None):
    if not ctrl.isEventPrb():
        action = PrbAction(PREBATTLE_ACTION_NAME.LAST_STAND_SQUAD, accountsToInvite=[cm.databaseID])
        result = yield ctrl.prbDispatcher.doSelectAction(action, fadeCtx={'layer': WindowLayer.OVERLAY,
         'waitForLayoutReady': R.views.last_stand.mono.lobby.hangar()})
        if not result:
            return
        showHangar()
    else:
        arenaUniqueID = getattr(cm, 'arenaUniqueID', None)
        cm.doSelect(PREBATTLE_ACTION_NAME.LAST_STAND_SQUAD, (cm.databaseID,), extData={'arenaUniqueID': arenaUniqueID})
    return


@dependency.replace_none_kwargs(ctrl=ILSController)
def lsSquadOptionBuilder(cm, options, userCMInfo, ctrl=None):
    if userCMInfo.isIgnored or cm.isSquadCreator() or cm.prbDispatcher is None or isinstance(cm, EXCLUDE_CM_CLASS):
        return options
    elif not ctrl.isAvailable():
        return options
    else:
        squadItem = findFirst(lambda it: it['id'] == USER.CREATE_SQUAD, options)
        inviteItem = findFirst(lambda it: it['id'] == USER.INVITE, options)
        userNameItem = findFirst(lambda it: it['id'] == USER.COPY_TO_CLIPBOARD, options)
        if not cm.isSquadAlreadyCreated(PREBATTLE_TYPE.LAST_STAND):
            lsSquadItem = cm.makeItem(CREATE_LS_SQUAD, backport.text(R.strings.last_stand_menu.contextMenu.createLastStandSquad()), optInitData={'enabled': not cm.prbEntity.isInQueue(),
             'textColor': HIGHLIGHT_COLOR})
            if squadItem:
                options.insert(options.index(squadItem) + 1, lsSquadItem)
            elif userNameItem:
                options.insert(options.index(userNameItem) + 1, lsSquadItem)
        elif inviteItem:
            enabled = userCMInfo.databaseID not in cm.prbEntity.getPlayers()
            inviteItem['initData'].update({'textColor': HIGHLIGHT_COLOR,
             'enabled': enabled})
        return options
