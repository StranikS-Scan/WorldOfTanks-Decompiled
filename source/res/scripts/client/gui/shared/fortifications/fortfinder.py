# Embedded file name: scripts/client/gui/shared/fortifications/FortFinder.py
import BigWorld
from constants import FORT_SCOUTING_DATA_ERROR
from gui.shared.utils.requesters.rqs_by_id import DataRequestsByIDProcessor, DataRequestCtx

class FortFinder(DataRequestsByIDProcessor):

    def getSender(self):
        return BigWorld.player()

    def request(self, filterType, abbrevPattern, homePeripheryID, limit, lvlFrom, lvlTo, ownStartDefHourFrom, ownStartDefHourTo, extStartDefHourFrom, extStartDefHourTo, attackDay, ownFortLvl, ownProfitFactor10, avgBuildingLevel10, ownBattleCountForFort, electedClanDBIDs, callback = None):

        def wrapper(result, data):
            callback(result == FORT_SCOUTING_DATA_ERROR.DONE, data)

        return self.doRequestEx(DataRequestCtx(), wrapper, 'requestFortPublicInfo', filterType, abbrevPattern, homePeripheryID, limit, lvlFrom, lvlTo, ownStartDefHourFrom, ownStartDefHourTo, extStartDefHourFrom, extStartDefHourTo, attackDay, ownFortLvl, ownProfitFactor10, avgBuildingLevel10, ownBattleCountForFort, electedClanDBIDs)

    def response(self, requestID, result, data):
        self._onResponseReceived(requestID, result, data)
