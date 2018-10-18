# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/battle_loading.py
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading
from gui.Scaleform.locale.EVENT import EVENT

class PveBattleLoading(BattleLoading):

    def _populate(self):
        super(PveBattleLoading, self)._populate()
        data = {'items': ({'descr': EVENT.LOADING_SCREEN_GAMEPLAY_TIPS_1}, {'descr': EVENT.LOADING_SCREEN_GAMEPLAY_TIPS_2}, {'descr': EVENT.LOADING_SCREEN_GAMEPLAY_TIPS_3}),
         'header': EVENT.LOADING_SCREEN_TITLE,
         'descr': EVENT.LOADING_SCREEN_DESCRIPTION}
        self.as_setEventInfoPanelDataS(data)
