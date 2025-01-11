# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bob/battle_loading.py
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading
from gui.Scaleform.daapi.view.meta.BobBattleLoadingMeta import BobBattleLoadingMeta

class BobBattleLoading(BattleLoading, BobBattleLoadingMeta):

    def _populate(self):
        super(BobBattleLoading, self)._populate()
        bobCtrl = self.sessionProvider.dynamic.bob
        bobCtrl.onInited += self.__updateBloggerIDs
        if bobCtrl.isInited():
            self.__updateBloggerIDs()

    def _dispose(self):
        bobCtrl = self.sessionProvider.dynamic.bob
        if bobCtrl is not None:
            bobCtrl.onInited -= self.__updateBloggerIDs
        super(BobBattleLoading, self)._dispose()
        return

    def __updateBloggerIDs(self):
        bobCtrl = self.sessionProvider.dynamic.bob
        self.as_setBloggerIdsS(bobCtrl.getAllyBloggerID(), bobCtrl.getEnemyBloggerID())
