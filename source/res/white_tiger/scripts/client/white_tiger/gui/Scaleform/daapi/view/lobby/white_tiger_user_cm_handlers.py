# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/white_tiger_user_cm_handlers.py
import adisp
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.rally.UnitUserCMHandler import UnitUserCMHandler
from gui.Scaleform.daapi.view.lobby.lobby_constants import USER
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import PrbAction
from white_tiger.gui.white_tiger_gui_constants import PREBATTLE_ACTION_NAME
from white_tiger.gui.shared.event_dispatcher import showHangar
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger_common.wt_constants import PREBATTLE_TYPE
from helpers import dependency
from shared_utils import findFirst
CREATE_WHITE_TIGER_SQUAD = 'createWhiteTigerSquad'
EXCLUDE_CM_CLASS = (UnitUserCMHandler,)
HIGHLIGHT_COLOR = 13347959

@adisp.adisp_process
@dependency.replace_none_kwargs(ctrl=IWhiteTigerController)
def createWhiteTigerSquadHandler(cm, ctrl=None):
    if not ctrl.isEventPrbActive():
        action = PrbAction(PREBATTLE_ACTION_NAME.WHITE_TIGER_SQUAD, accountsToInvite=[cm.databaseID])
        result = yield ctrl.prbDispatcher.doSelectAction(action, fadeCtx={'layer': WindowLayer.OVERLAY,
         'waitForLayoutReady': R.views.white_tiger.mono.lobby.main()})
        if not result:
            return
        showHangar()
    else:
        cm.doSelect(PREBATTLE_ACTION_NAME.WHITE_TIGER_SQUAD, (cm.databaseID,))


@dependency.replace_none_kwargs(ctrl=IWhiteTigerController)
def whiteTigerSquadOptionBuilder(cm, options, userCMInfo, ctrl=None):
    if userCMInfo.isIgnored or cm.isSquadCreator() or cm.prbDispatcher is None or isinstance(cm, EXCLUDE_CM_CLASS):
        return options
    elif not ctrl.isAvailable():
        return options
    else:
        squadItem = findFirst(lambda it: it['id'] == USER.CREATE_SQUAD, options)
        inviteItem = findFirst(lambda it: it['id'] == USER.INVITE, options)
        userNameItem = findFirst(lambda it: it['id'] == USER.COPY_TO_CLIPBOARD, options)
        if not cm.isSquadAlreadyCreated(PREBATTLE_TYPE.WHITE_TIGER):
            wtSquadItem = cm.makeItem(CREATE_WHITE_TIGER_SQUAD, backport.text(R.strings.menu.contextMenu.createEventSquad()), optInitData={'enabled': not cm.prbEntity.isInQueue(),
             'textColor': HIGHLIGHT_COLOR})
            if squadItem:
                options.insert(options.index(squadItem) + 1, wtSquadItem)
            elif userNameItem:
                options.insert(options.index(userNameItem) + 1, wtSquadItem)
        elif inviteItem:
            enabled = userCMInfo.databaseID not in cm.prbEntity.getPlayers()
            inviteItem['initData'].update({'textColor': HIGHLIGHT_COLOR,
             'enabled': enabled})
        return options
