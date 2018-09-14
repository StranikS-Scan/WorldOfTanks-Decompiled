# Embedded file name: scripts/client/gui/shared/utils/requesters/deprecated/StatsRequester.py
from functools import partial
import AccountCommands
import BigWorld
from adisp import async, process
import constants
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_NOTE
import dossiers2
from helpers import isPlayerAccount
from items import ITEM_TYPE_INDICES
from items import tankmen
_TANKMAN = ITEM_TYPE_INDICES['tankman']
_SAFE_SERVER_ERROR_CODES = (AccountCommands.RES_NOT_AVAILABLE,)

def responseIfNotAccount(*dargs, **dkwargs):

    def decorate(fn):

        def checkAccount(*fargs, **fkwargs):
            if not isPlayerAccount():
                LOG_NOTE('Server call "StatsRequester.%s" canceled: player is not account.' % fn.func_name)
                returnFurnc = dkwargs.get('func', None)
                if returnFurnc:
                    returnArgs = dkwargs.get('args', None)
                    if returnArgs:
                        return fkwargs['callback'](returnFurnc(returnArgs))
                    return fkwargs['callback'](returnFurnc())
                return fkwargs['callback'](*dargs, **dkwargs)
            else:
                fargs[0].setCallback(fkwargs['callback'])
                return fn(*fargs, **fkwargs)

        return checkAccount

    return decorate


class StatsRequester(object):

    def __init__(self):
        self.__callback = None
        return

    def setCallback(self, callback):
        self.__callback = callback

    @async
    @process
    def getClanEmblemTextureID(self, clanDBID, isBig, textureID, callback):
        import imghdr
        if clanDBID is not None and clanDBID != 0:
            clanEmblemUrl, clanEmblemFile = yield self.getFileFromServer(clanDBID, 'clan_emblems_small' if not isBig else 'clan_emblems_big')
            if clanEmblemFile and imghdr.what(None, clanEmblemFile) is not None:
                BigWorld.wg_addTempScaleformTexture(textureID, clanEmblemFile)
                callback(True)
                return
        callback(False)
        return

    @async
    @responseIfNotAccount(set())
    def getMultipliedXPVehicles(self, callback):
        BigWorld.player().stats.get('multipliedXPVehs', self.__valueResponse)

    @async
    @responseIfNotAccount(func=dossiers2.getAccountDossierDescr, args=('',))
    def getAccountDossier(self, callback):
        BigWorld.player().stats.get('dossier', self.__accountDossierResponse)

    @async
    @responseIfNotAccount(func=dossiers2.getVehicleDossierDescr, args=('',))
    def getVehicleDossier(self, vehTypeCompDescr, callback):
        BigWorld.player().dossierCache.get(constants.DOSSIER_TYPE.VEHICLE, vehTypeCompDescr, self.__vehicleDossierResponse)

    @async
    @responseIfNotAccount(func=dossiers2.getTankmanDossierDescr, args=('',))
    def getTankmanDossier(self, tankmanID, callback):
        BigWorld.player().inventory.getItems(_TANKMAN, partial(self.__tankmanDossierResponse, tankmanID))

    @async
    @responseIfNotAccount(0)
    def getCredits(self, callback):
        BigWorld.player().stats.get('credits', self.__valueResponse)

    @async
    @responseIfNotAccount(1)
    def getFreeXPToTManXPRate(self, callback):
        BigWorld.player().shop.getFreeXPToTManXPRate(self.__valueResponse)

    @async
    @responseIfNotAccount(1)
    def freeXPToTankman(self, tankmanId, freeXp, callback):
        BigWorld.player().inventory.freeXPToTankman(tankmanId, freeXp, lambda eStr, code: self.__callback((code >= 0, eStr)))

    @async
    @responseIfNotAccount(False)
    def isTeamKiller(self, callback):
        BigWorld.player().stats.get('tkillIsSuspected', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getRestrictions(self, callback):
        BigWorld.player().stats.get('restrictions', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getDenunciations(self, callback):
        BigWorld.player().stats.get('denunciationsLeft', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getGold(self, callback):
        BigWorld.player().stats.get('gold', self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getVehicleTypeExperiences(self, callback):
        BigWorld.player().stats.get('vehTypeXP', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getFreeExperience(self, callback):
        BigWorld.player().stats.get('freeXP', self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getVehicleTypeLocks(self, callback):
        BigWorld.player().stats.get('vehTypeLocks', self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getGlobalVehicleLocks(self, callback):
        BigWorld.player().stats.get('globalVehicleLocks', self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def exchange(self, gold, callback):
        BigWorld.player().stats.exchange(gold, self.__response)

    @async
    @responseIfNotAccount(0)
    def getAmmoSellPrice(self, ammo, callback):
        BigWorld.player().shop.getAmmoSellPrice(ammo, self.__valueResponse)

    @async
    @responseIfNotAccount(1)
    def getDailyXPFactor(self, callback):
        BigWorld.player().shop.getDailyXPFactor(self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def convertVehiclesXP(self, xp, vehTypeDescrs, callback):
        BigWorld.player().stats.convertToFreeXP(vehTypeDescrs, xp, self.__response)

    @async
    @responseIfNotAccount(set())
    def getUnlocks(self, callback):
        BigWorld.player().stats.get('unlocks', self.__valueResponse)

    @async
    @responseIfNotAccount(set())
    def getEliteVehicles(self, callback):
        BigWorld.player().stats.get('eliteVehicles', self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def upgradeToPremium(self, days, arenaUniqueID, callback):
        BigWorld.player().stats.upgradeToPremium(days, arenaUniqueID, self.__response)

    @async
    @responseIfNotAccount(False)
    def buySlot(self, callback):
        BigWorld.player().stats.buySlot(self.__response)

    @async
    @responseIfNotAccount(0)
    def getSlotsCount(self, callback):
        BigWorld.player().stats.get('slots', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getTankmenBerthsCount(self, callback):
        BigWorld.player().stats.get('berths', self.__valueResponse)

    @async
    @responseIfNotAccount([0, [0]])
    def getSlotsPrices(self, callback):
        BigWorld.player().shop.getSlotsPrices(self.__valueResponse)

    @async
    @responseIfNotAccount(dict())
    def getSteamGoldPackets(self, callback):
        BigWorld.player().shop.getGoldPackets(self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getPaidRemovalCost(self, callback):
        BigWorld.player().shop.getPaidRemovalCost(self.__valueResponse)

    @async
    @responseIfNotAccount([0, 1, [0]])
    def getBerthsPrices(self, callback):
        BigWorld.player().shop.getBerthsPrices(self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def buyBerths(self, callback):
        BigWorld.player().stats.buyBerths(self.__response)

    @async
    @responseIfNotAccount(tuple())
    def getTankmanCost(self, callback):
        BigWorld.player().shop.getTankmanCost(self.__valueResponse)

    @async
    @responseIfNotAccount(tuple())
    def getDropSkillsCost(self, callback):
        BigWorld.player().shop.getDropSkillsCost(self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getPassportChangeCost(self, callback):
        BigWorld.player().shop.getPassportChangeCost(self.__valueResponse)

    @async
    @responseIfNotAccount((0, 0))
    def getShellPrice(self, nationIdx, shellCompactDescr, callback):
        BigWorld.player().shop.getPrice(ITEM_TYPE_INDICES['shell'], nationIdx, shellCompactDescr, self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def getSellPriceModifiers(self, compDescr, callback):
        BigWorld.player().shop.getSellPriceModifiers(compDescr, self.__valueResponse)

    @async
    @responseIfNotAccount(1)
    def getExchangeRate(self, callback):
        BigWorld.player().shop.getExchangeRate(self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getFreeXPConversion(self, callback):
        BigWorld.player().shop.getFreeXPConversion(self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getPremiumCost(self, callback):
        BigWorld.player().shop.getPremiumCost(self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getAccountAttrs(self, callback):
        BigWorld.player().stats.get('attrs', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getPremiumExpiryTime(self, callback):
        BigWorld.player().stats.get('premiumExpiryTime', self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getClanInfo(self, callback):
        BigWorld.player().stats.get('clanInfo', self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getClanDBID(self, callback):
        BigWorld.player().stats.get('clanDBID', self.__valueResponse)

    @async
    @responseIfNotAccount(dict())
    def setAndFillLayouts(self, vehInvID, shellsLayout, eqsLayout, callback):
        BigWorld.player().inventory.setAndFillLayouts(vehInvID, shellsLayout, eqsLayout, lambda resID, errStr, value: self.__callback((resID, errStr, value)))

    @async
    @responseIfNotAccount(dict())
    def getBattleResults(self, arenaUniqueID, callback):
        BigWorld.player().battleResultsCache.get(arenaUniqueID, self.__valueResponse)

    @async
    @responseIfNotAccount((None, None))
    def getFileFromServer(self, clanId, fileType, callback):
        if not BigWorld.player().serverSettings['file_server'].has_key(fileType):
            LOG_ERROR("Invalid server's file type: %s" % fileType)
            self.__valueResponse(0, (None, None))
            return None
        else:
            clan_emblems = BigWorld.player().serverSettings['file_server'][fileType]
            BigWorld.player().customFilesCache.get(clan_emblems['url_template'] % clanId, lambda url, file: self.__valueResponse(0, (url, file)), True)
            return None

    @async
    @responseIfNotAccount(None)
    def getUserClanInfo(self, userName, callback):
        BigWorld.player().requestPlayerClanInfo(userName, lambda resultID, str, clanDBID, clanInfo: self.__valueResponse(resultID, (clanDBID, clanInfo)))

    @async
    @responseIfNotAccount(False)
    def hasFinPassword(self, callback):
        BigWorld.player().stats.get('hasFinPassword', self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getVehiclesPrices(self, vehicles, callback):
        BigWorld.player().shop.getVehiclesSellPrices(vehicles, self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getFreeVehicleLeft(self, callback):
        BigWorld.player().stats.get('freeVehiclesLeft', self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getVehicleSellsLeft(self, callback):
        BigWorld.player().stats.get('vehicleSellsLeft', self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getFreeTankmanLeft(self, callback):
        BigWorld.player().stats.get('freeTMenLeft', self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def setEquipments(self, vehInvId, equipments, callback):
        BigWorld.player().inventory.equipEquipments(vehInvId, equipments, self.__response)

    @async
    @responseIfNotAccount({})
    def getTradeFees(self, callback):
        raise hasattr(BigWorld.player(), 'shop') or AssertionError('Request from shop is not possible')
        self.__callback = callback
        BigWorld.player().shop.getTradeFees(self.__valueResponse)

    def __accountDossierResponse(self, responseCode, dossierCompDescr = ''):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat account dossier request: responseCode=%s' % responseCode)
            return
        if self.__callback:
            dossierDescr = dossiers2.getAccountDossierDescr(dossierCompDescr)
            self.__callback(dossierDescr)

    def __vehicleDossierResponse(self, responseCode, vehTypeDossiers = ''):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat account dossier request: responseCode=%s' % responseCode)
            return
        else:
            if self.__callback:
                if vehTypeDossiers is not None:
                    self.__callback(dossiers2.getVehicleDossierDescr(vehTypeDossiers))
                self.__callback(dossiers2.getVehicleDossierDescr(''))
            return

    def __tankmanDossierResponse(self, tankmanID, resultID, data):
        if resultID < 0:
            LOG_ERROR('Server return error for inventory tankman dossier request: responseCode=%s' % resultID)
            return
        else:
            if self.__callback and data is not None:
                dossier = ''
                tankman = data.get('compDescr', None)
                if tankman is not None:
                    tmenCompDescr = tankman.get(tankmanID, None)
                    if tmenCompDescr is not None:
                        dossier = tankmen.TankmanDescr(tmenCompDescr).dossierCompactDescr
                self.__callback(dossiers2.getTankmanDossierDescr(dossier))
            return

    def _valueResponse(self, responseCode, value = None, revision = 0):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat request: responseCode=%s' % responseCode)
            self.__dumpStack()
        elif self.__callback:
            self.__callback(value)

    def __valueResponse(self, responseCode, value = None, revision = 0):
        if responseCode < 0:
            if responseCode not in _SAFE_SERVER_ERROR_CODES:
                LOG_ERROR('Server return error for stat request: responseCode=%s' % responseCode)
                self.__dumpStack()
            else:
                LOG_WARNING('Server return error for stat request: responseCode=%s' % responseCode)
        if self.__callback:
            self.__callback(value)

    def __response(self, responseCode):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat request: responseCode=%s.' % responseCode)
            self.__dumpStack()
        if self.__callback:
            self.__callback(responseCode >= 0)

    def __dumpStack(self):
        import inspect
        dump = 'frames stack dumping --------------'
        for frame, file, line, method, _, _ in inspect.stack():
            dump = '%s\n (%s, %d): %s' % (dump,
             str(file),
             line,
             str(method))

        LOG_ERROR(dump)
