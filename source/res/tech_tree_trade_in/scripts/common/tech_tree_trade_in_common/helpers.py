# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/common/tech_tree_trade_in_common/helpers.py
from collections import namedtuple
from items import vehicles
from tech_tree_trade_in_config import getTradeInVehiclesCfg
TechTreeBranch = namedtuple('TechTreeBranch', ['branchId', 'vehCDs'])
Token = namedtuple('Token', ['prefix',
 'launchID',
 'tradedBranch',
 'receivedBranch',
 'tradeSummary'])

class TradeInToken(object):
    PREFIX = 'tech_tree_trade_in'
    __PENDING = 'pending'

    @staticmethod
    def generateToken(launchID, tradedBranch, receivedBranch, tradeSummary=__PENDING):
        return ':'.join([TradeInToken.PREFIX,
         launchID,
         tradedBranch,
         receivedBranch,
         tradeSummary])

    @staticmethod
    def parseToken(token):
        return Token(*token.split(':'))

    @staticmethod
    def isBlockerToken(token):
        return True if token.startswith(TradeInToken.PREFIX) and TradeInToken.parseToken(token).tradeSummary == TradeInToken.__PENDING else False

    @staticmethod
    def makeTokenComplete(token, summary):
        token = TradeInToken.parseToken(token)
        return TradeInToken.generateToken(token.launchID, token.tradedBranch, token.receivedBranch, summary)

    @staticmethod
    def isTradeInToken(token):
        return token.startswith(TradeInToken.PREFIX)


def generateTokenFromBranches(launchID, branchToTrade, branchToReceive):
    return TradeInToken.generateToken(launchID, generateBranchSign(branchToTrade), generateBranchSign(branchToReceive))


def generateBranchSign(branch):
    config = getTradeInVehiclesCfg()

    def vehicleName(vehicleCD):
        return vehicles.getItemByCompactDescr(vehicleCD).name.split(':')[1]

    return '{}!{}'.format(vehicleName(branch[0]), vehicleName(branch[-1])) if branch[-1] in config['branches']['multy10'] else vehicleName(branch[-1])


def getBranchFromSign(branchSign):
    allBranches = getTradeInVehiclesCfg()['branches']['allBranches']

    def getVehCDByName(vehicleName):
        vehicleType = vehicles.g_cache.vehicle(*vehicles.g_list.getIDsByVehName(vehicleName))
        return vehicleType.compactDescr

    vehNames = branchSign.split('!')
    vehCDs = set((getVehCDByName(name) for name in vehNames))
    return next((branch for branch in allBranches if vehCDs.issubset(branch)), [])
