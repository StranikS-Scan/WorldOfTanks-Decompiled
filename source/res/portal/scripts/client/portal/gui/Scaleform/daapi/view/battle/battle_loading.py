# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/battle_loading.py
from portal.gui.Scaleform.daapi.view.meta.PortalBattleLoadingMeta import PortalBattleLoadingMeta
from gui.impl import backport
from gui.impl.gen import R
import random

class PortalBattleLoading(PortalBattleLoadingMeta):

    def __init__(self, _=None):
        super(PortalBattleLoading, self).__init__()
        self.__tipsHeader = None
        self.__tips = None
        return

    def _populate(self):
        self.__readTips()
        super(PortalBattleLoading, self)._populate()

    def _setTipsInfo(self):
        tip = random.choice(self.__tips)
        self.as_setTipsS([self.__tipsHeader, tip])

    def _addArenaTypeData(self):
        pass

    def __readTips(self):
        res = R.strings.portal_event.battle.loadingScreen
        self.__tipsHeader = backport.text(res.tipsHeader())
        self.__tips = [ backport.text(descriptionResId()) for _, descriptionResId in res.tips.items() ]
