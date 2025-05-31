# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/battle_queue.py
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from gui.Scaleform.daapi.view.lobby.battle_queue import RandomQueueProvider
from gui.impl import backport

class FunRandomQueueProvider(RandomQueueProvider, FunAssetPacksMixin, FunSubModesWatcher):

    def getIconPath(self, iconlabel):
        return backport.image(self.getModeIconsResRoot().battle_type.c_136x136.fun_random())

    def getTitle(self, guiType):
        return self.__getTitle() or self.getModeUserName()

    def processQueueInfo(self, qInfo):
        super(FunRandomQueueProvider, self).processQueueInfo(qInfo or {})

    @hasDesiredSubMode()
    def _doRequestQueueInfo(self, currPlayer):
        super(FunRandomQueueProvider, self)._doRequestQueueInfo(currPlayer)

    def _getRequestQueueInfoParams(self):
        return (self._queueType, self.getDesiredSubMode().getSubModeID())

    @hasDesiredSubMode(defReturn='')
    def __getTitle(self):
        subModeName = backport.text(self.getDesiredSubMode().getLocalsResRoot().userName())
        return self.getModeDetailedUserName(subModeName=subModeName)
