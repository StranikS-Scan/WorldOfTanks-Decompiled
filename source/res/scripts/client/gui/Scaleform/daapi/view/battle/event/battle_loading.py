# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/battle_loading.py
from gui.Scaleform.daapi.view.battle.shared.battle_loading import isBattleLoadingShowed, _setBattleLoading
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.FestivalRaceBattleLoadingMeta import FestivalRaceBattleLoadingMeta
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class EventBattleLoading(FestivalRaceBattleLoadingMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def _setTipsInfo(self):
        arenaDP = self._battleCtx.getArenaDP()
        if not isBattleLoadingShowed():
            self.as_setTipTitleS(backport.text(R.strings.festival.festival.loading.map()))
            self.as_setTipS(backport.text(R.strings.festival.festival.loading.gametype()))
            arenaHint = arenaDP.getPersonalDescription().arenaHint
            if len(arenaHint) > 1:
                self.as_setHintS(backport.text(arenaHint[0].name()), backport.text(arenaHint[0].descr(), **arenaHint[1]))
            else:
                self.as_setHintS(backport.text(arenaHint[0].name()), backport.text(arenaHint[0].descr()))
            self.as_setAddIconS([backport.image(R.images.gui.maps.icons.festival.adds.restele_logo()), backport.image(R.images.gui.maps.icons.festival.adds.intel_logo()), backport.image(R.images.gui.maps.icons.festival.adds.razer_logo())])
            _setBattleLoading(True)
