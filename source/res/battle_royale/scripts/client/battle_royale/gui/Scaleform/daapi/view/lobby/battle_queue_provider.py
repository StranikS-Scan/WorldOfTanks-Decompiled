# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/battle_queue_provider.py
from battle_royale.gui.constants import BattleRoyaleSubMode
import constants
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.battle_queue import RandomQueueProvider
from gui.impl.gen.view_models.views.battle_royale.battle_results.player_battle_type_status_model import BattleType
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
_SUBMODE_ID_TO_BATTLE_TYPE = {BattleRoyaleSubMode.SOLO_MODE_ID: BattleType.SOLO,
 BattleRoyaleSubMode.SOLO_DYNAMIC_MODE_ID: BattleType.RANDOMPLATOON,
 BattleRoyaleSubMode.SQUAD_MODE_ID: BattleType.PLATOON}

class BattleRoyaleQueueProvider(RandomQueueProvider):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def processQueueInfo(self, qInfo):
        playersCount = qInfo.get('players', 0)
        self._createCommonPlayerString(playersCount)
        modesData = []
        for mode in constants.BattleRoyaleMode.ALL:
            modesData.append({'type': backport.text(R.strings.menu.prebattle.battleRoyale.dyn(mode)()),
             'icon': backport.image(R.images.battle_royale.gui.maps.icons.battleQueue.dyn(mode)()),
             'count': qInfo.get(mode, 0)})

        self._proxy.as_setDPS(modesData)

    def getLayoutStr(self):
        pass

    def getAdditionalParams(self):
        battleType = _SUBMODE_ID_TO_BATTLE_TYPE[self.__battleRoyaleController.getCurrentSubModeID()].value
        iconPath = backport.image(R.images.battle_royale.gui.maps.icons.battleQueue.battleType.dyn(battleType)())
        return {'battleTypeIconPath': iconPath}
