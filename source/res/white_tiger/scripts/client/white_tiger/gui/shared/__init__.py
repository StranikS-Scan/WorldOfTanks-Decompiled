# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/shared/__init__.py
import logging
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class RewardVideoSequencePlayer(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    def playSequence(self, parent, boxType, boxCount, mainRewards, allRewards):
        box = self.__itemsCache.items.tokens.getLootBoxByType(boxType)
        customBonusVideoNumber = box.getCustomBonusData().get('numberOfShownRewardVideos', 0)
        numberOfShownVideos = min(customBonusVideoNumber, len(mainRewards))
        if numberOfShownVideos < 1:
            _logger.error('Wrong number of videos [%s] or rewards [%s]', len(mainRewards), customBonusVideoNumber)
            return
        slice = len(mainRewards) - numberOfShownVideos if len(mainRewards) > numberOfShownVideos else 0
        mainRewards = mainRewards[slice:]
        from white_tiger.gui.impl.lobby.wt_portal_vehicle_reward import WtPortalVehicleRewardWindow as window
        w = window(boxType=boxType, boxCount=boxCount, vehiclesReward=mainRewards, awards=allRewards, parent=parent, numberOfVideos=numberOfShownVideos)
        w.load()


rewardVideoSequencePlayer = RewardVideoSequencePlayer()
