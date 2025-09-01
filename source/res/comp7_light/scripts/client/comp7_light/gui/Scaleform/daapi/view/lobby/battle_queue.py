# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/lobby/battle_queue.py
from gui.Scaleform.daapi.view.lobby.battle_queue.battle_queue import RandomQueueProvider
from gui.impl import backport
from gui.impl.gen import R

class Comp7LightQueueProvider(RandomQueueProvider):

    def processQueueInfo(self, qInfo):
        info = dict(qInfo)
        allPlayersCount = info.get('players', 0)
        self._proxy.as_setDPS([{'type': backport.text(R.strings.menu.prebattle.playersLabel()),
          'icon': backport.image(R.images.comp7_light.gui.maps.icons.icons.playersTotalIcon()),
          'count': allPlayersCount,
          'highlight': False}])

    def getLayoutStr(self):
        pass

    def getIconPath(self, iconlabel):
        return backport.image(R.images.comp7_light.gui.maps.icons.battleTypes.c_136x136.comp7_light())

    def getTankInfoLabel(self):
        pass

    def getTankIcon(self, vehicle):
        pass

    def getTankName(self, vehicle):
        pass

    def needAdditionalInfo(self):
        return False

    def additionalInfo(self):
        pass
