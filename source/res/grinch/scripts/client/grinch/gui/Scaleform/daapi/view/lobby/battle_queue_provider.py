# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/lobby/battle_queue_provider.py
import constants
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.battle_queue import QueueProvider
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from grinch.skeletons.battle_controller import IGrinchController
_HTMLTEMP_PLAYERSLABEL = 'html_templates:lobby/queue/playersLabel'

class GrinchQueueProvider(QueueProvider):
    __grinchCtrl = dependency.descriptor(IGrinchController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def processQueueInfo(self, qInfo):
        info = dict(qInfo)
        if 'classes' in info:
            vClasses = info['classes']
            vClassesLen = len(vClasses)
        else:
            vClasses = []
            vClassesLen = 0
        self._createCommonPlayerString(sum(vClasses))
        if vClassesLen:
            vClassesData = []
            for vehCD in self.__grinchCtrl.getConfig()['vehicles']:
                item = self.__itemsCache.items.getItemByCD(vehCD)
                idx = constants.VEHICLE_CLASS_INDICES[item.type]
                vClassesData.append({'type': item.userName,
                 'icon': backport.image(R.images.grinch.gui.maps.icons.battleQueue.dyn(item.type)()),
                 'count': vClasses[idx] if idx < vClassesLen else 0})

            self._proxy.as_setDPS(vClassesData)
        self._proxy.as_showStartS(self._isStartButtonDisplayed(vClasses))

    def getTankIcon(self, vehicle):
        return backport.image(R.images.grinch.gui.maps.icons.battleQueue.dyn(vehicle.type)())

    def getTitle(self, guiType):
        return backport.text(R.strings.mode_selector.mode.grinch.title())

    def getLayoutStr(self):
        pass

    @staticmethod
    def _isStartButtonDisplayed(vClasses):
        return False

    def _createCommonPlayerString(self, playerCount):
        self._proxy.flashObject.as_setPlayers(makeHtmlString(_HTMLTEMP_PLAYERSLABEL, 'players', {'count': playerCount}))
