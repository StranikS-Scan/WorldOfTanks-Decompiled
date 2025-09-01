# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/platoon/wt_platoon_members_view.py
from enum import Enum
from helpers import i18n
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_members_view import EventMembersView
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS

class _PrebattleTypes(Enum):
    WHITE_TIGER = 'whiteTiger'


class WhiteTigerMembersView(EventMembersView):
    _prebattleType = _PrebattleTypes.WHITE_TIGER
    _layoutID = R.views.white_tiger.lobby.platoon.MembersWindow()

    def _setNoBonusInformation(self, model):
        model.noBonusPlaceholder.setIcon(R.images.white_tiger.gui.maps.icons.battleTypes.c_64x64.white_tiger())

    def _getTitle(self):
        return backport.text(R.strings.white_tiger_lobby.platoon.wt_squad())

    def _getActionButtonStateInfo(self):
        result = self._platoonCtrl.getPrbEntity().canPlayerDoAction()
        actionButtonStateVO = SquadActionButtonStateVO(self._platoonCtrl.getPrbEntity())
        isEnabled = actionButtonStateVO['isEnabled']
        onlyReadinessText = actionButtonStateVO.isReadinessTooltip()
        simpleState = actionButtonStateVO.getSimpleState()
        toolTipData = i18n.makeString(actionButtonStateVO['toolTipData'] + '/body')
        if result.restriction == UNIT_RESTRICTION.VEHICLE_NOT_VALID:
            simpleState = backport.text(R.strings.white_tiger_lobby.platoon.simpleState.wrongVehicle())
            toolTipData = ''
        elif result.restriction in [UNIT_RESTRICTION.MODE_NO_BATTLES, UNIT_RESTRICTION.MODE_NOT_AVAILABLE]:
            simpleState = backport.text(R.strings.white_tiger_lobby.platoon.simpleState.notAvailable())
            toolTipData = ''
        return (isEnabled,
         onlyReadinessText,
         simpleState,
         toolTipData)

    def _setPlayerData(self, accID, isWTREnabled, slotData, playerData, slotModel):
        super(WhiteTigerMembersView, self)._setPlayerData(accID, isWTREnabled, slotData, playerData, slotModel)
        playerStatus = slotData.get('playerStatus', PLAYER_GUI_STATUS.NORMAL)
        slotModel.setIsInBattle(playerStatus == PLAYER_GUI_STATUS.BATTLE)
        slotModel.setPrebattleType(self._prebattleType)
        isOffline = playerData.get('isOffline', False)
        if playerStatus != PLAYER_GUI_STATUS.READY and playerStatus != PLAYER_GUI_STATUS.BATTLE and not isOffline:
            slotModel.setInfoText(backport.text(R.strings.white_tiger_lobby.platoon.unit.message.vehicleNotSelected()))
