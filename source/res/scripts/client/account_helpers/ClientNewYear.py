# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/ClientNewYear.py
from pprint import pformat
from collections import namedtuple
import cPickle
import zlib
import AccountCommands
import Event
from items import new_year_types
from items.new_year_types import getTotalAtmosphere, getAtmosphereLevel, getAtmosphereProgress
from items.new_year_types import NATIONAL_SETTINGS_IDS_BY_NAME, TOY_TYPES_IDS_BY_NAME, NY_STATE
from items.new_year_types import getCollectionLevel, getBonuses, SETTING_ID_BY_NATION_ID, SETTING_BY_NATION_ID
from constants import EVENT_CLIENT_DATA
from debug_utils import LOG_DEBUG_DEV, LOG_ERROR
import PlayerEvents

def _defaultLogger(*args):
    msg = pformat(args)
    LOG_DEBUG_DEV('\n\n[SERVER CMD RESPONSE]\n{}\n'.format(msg))


ToyInventoryData = namedtuple('ToyInventoryData', ('totalCount', 'newCount'))
TankmanPassportData = namedtuple('TankmanPassportData', ('groupID',
 'firstNameID',
 'lastNameID',
 'iconID'))

class ClientNewYear(object):
    __em = Event.EventManager()
    onInventoryChanged = Event.Event(__em)
    onSlotsChanged = Event.Event(__em)
    onLevelChanged = Event.Event(__em)
    onToyFragmentsChanged = Event.Event(__em)
    onBoxesChanged = Event.Event(__em)
    onChestsChanged = Event.Event(__em)
    onVariadicDiscountsChanged = Event.Event(__em)
    onVariadicTankmenChanged = Event.Event(__em)
    onStateChanged = Event.Event(__em)
    onToyCollectionChanged = Event.Event(__em)
    onTankmanChoicesChanged = Event.Event(__em)

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__ignore = False
        self.__inventoryToys = {}
        self.__slots = [-1] * len(new_year_types.g_cache.slots)
        self.__level = 1
        self.__toyFragments = 0
        self.__boxes = {}
        self.__chests = {}
        self.__variadicDiscounts = {}
        self.__variadicTankmen = {}
        self.__toyCollection = set()
        self.__collectionRatings = [0] * len(new_year_types.NATIONAL_SETTINGS)
        self.__tankmanNextChoices = {}
        self.__state = NY_STATE.NOT_STARTED
        PlayerEvents.g_playerEvents.onEventsDataChanged += self.__onEventsDataChanged
        return

    def clear(self):
        PlayerEvents.g_playerEvents.onEventsDataChanged -= self.__onEventsDataChanged

    @property
    def state(self):
        return self.__state

    @property
    def boxes(self):
        return self.__boxes

    @property
    def chests(self):
        return self.__chests

    @property
    def variadicDiscounts(self):
        return self.__variadicDiscounts

    @property
    def variadicTankmen(self):
        return self.__variadicTankmen

    @property
    def inventoryToys(self):
        return self.__inventoryToys

    @property
    def slots(self):
        return self.__slots

    @property
    def toyFragments(self):
        return self.__toyFragments

    @property
    def toyCollection(self):
        return self.__toyCollection

    @property
    def collectionLevels(self):
        return tuple((getCollectionLevel(rating) for rating in self.__collectionRatings))

    @property
    def level(self):
        return self.__level

    @property
    def atmosphereLevel(self):
        return getAtmosphereLevel(getTotalAtmosphere(self.__slots))

    @property
    def progress(self):
        return getAtmosphereProgress(getTotalAtmosphere(self.__slots))

    @property
    def tankmanNextChoices(self):
        return self.__tankmanNextChoices

    def getBonusesForNation(self, nationID):
        atmosphereLevel = getAtmosphereLevel(getTotalAtmosphere(self.__slots))
        collectionLevel = getCollectionLevel(self.__collectionRatings[SETTING_ID_BY_NATION_ID[nationID]])
        return getBonuses(atmosphereLevel, collectionLevel)

    def calculateBonusesForCollectionLevel(self, collectionLevel):
        atmosphereLevel = getAtmosphereLevel(getTotalAtmosphere(self.__slots))
        return getBonuses(atmosphereLevel, collectionLevel)

    def getBonusesForSetting(self, settingID):
        atmosphereLevel = getAtmosphereLevel(getTotalAtmosphere(self.__slots))
        collectionLevel = getCollectionLevel(self.__collectionRatings[settingID])
        return getBonuses(atmosphereLevel, collectionLevel)

    def getCollectionLevelForNation(self, nationID):
        return getCollectionLevel(self.__collectionRatings[SETTING_ID_BY_NATION_ID[nationID]])

    def getCollectionRatingForNation(self, nationID):
        return self.__collectionRatings[SETTING_ID_BY_NATION_ID[nationID]]

    def getSettingForNation(self, nationID):
        return SETTING_BY_NATION_ID[nationID]

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def checkDiffSanity(self, diff):
        if self.state == NY_STATE.IN_PROGRESS:
            if len(diff) == 3 and all((key in ('rev', 'prevRev', 'eventsData') for key in diff.iterkeys())):
                return diff['eventsData']
        return True

    def synchronize(self, isFullSync, diff):
        if self.__ignore:
            return
        else:
            update = diff.get('newYear', None)
            if update is not None:
                LOG_DEBUG_DEV('diff["newYear"] update={}'.format(update))
                if 'toyCollection' in update:
                    self.__addToCollection(_unpackBinaryCollection(update['toyCollection']))
                if 'slots' in update:
                    self.__slots = update['slots']
                    self.onSlotsChanged(self.__slots)
                if 'inventoryToys' in update:
                    tDiff = dict(((toyID, ToyInventoryData(*data)) for toyID, data in update['inventoryToys'].iteritems()))
                    self.__inventoryToys.update(tDiff)
                    self.__addToCollection(tDiff.iterkeys())
                    self.onInventoryChanged(tDiff)
                if 'level' in update:
                    self.__level = update['level']
                    self.onLevelChanged(self.__level, *self.progress)
                if 'toyFragments' in update:
                    self.__toyFragments = update['toyFragments']
                    self.onToyFragmentsChanged(self.__toyFragments)
                if 'tankmanNextChoices' in update:
                    choiceItems = update['tankmanNextChoices'].iteritems()
                    tmDiff = dict(((nationID, TankmanPassportData(*data)) for nationID, data in choiceItems))
                    self.__tankmanNextChoices.update(tmDiff)
                    self.onTankmanChoicesChanged(tmDiff)
            tokensUpdate = diff.get('tokens', None)
            if tokensUpdate is not None:
                LOG_DEBUG_DEV('update tokens={}'.format(tokensUpdate))
                nyCache = new_year_types.g_cache
                boxesCache = nyCache.boxes
                chestsCache = nyCache.chests
                varDiscountsCache = nyCache.variadicDiscounts
                varTankmenCache = nyCache.variadicTankmen
                boxesDiff = {}
                chestsDiff = {}
                varDiscountsDiff = {}
                varTankmenDiff = {}
                nyTokens = []
                for token, data in tokensUpdate.iteritems():
                    count = 0 if data is None else data[1]
                    if token in boxesCache:
                        self.__boxes[token] = boxesDiff[token] = count
                    elif token in chestsCache:
                        self.__chests[token] = chestsDiff[token] = count
                    elif token in varDiscountsCache:
                        self.__variadicDiscounts[token] = varDiscountsDiff[token] = count
                    elif token in varTankmenCache:
                        self.__variadicTankmen[token] = varTankmenDiff[token] = count
                    if 'ny18:' in token:
                        nyTokens.append(token)

                if boxesDiff:
                    self.onBoxesChanged(boxesDiff)
                if chestsDiff:
                    self.onChestsChanged(chestsDiff)
                if varDiscountsDiff:
                    self.onVariadicDiscountsChanged(varDiscountsDiff)
                if varTankmenDiff:
                    self.onVariadicTankmenChanged(varTankmenDiff)
                if not isFullSync:
                    for token in nyTokens:
                        del diff['tokens'][token]

                    if not diff['tokens']:
                        del diff['tokens']
            return

    def fillSlot(self, slotID, toyID, callback=_defaultLogger):
        if self.__account is not None:
            self.__account._doCmdInt3(AccountCommands.CMD_NEW_YEAR_SLOT_FILL, slotID, toyID, 0, callback)
        return

    def craft(self, toyType, nationalSetting, rank, callback=_defaultLogger):
        if self.__account is not None:
            toyTypeID = -1 if toyType is None else TOY_TYPES_IDS_BY_NAME[toyType]
            settingID = -1 if nationalSetting is None else NATIONAL_SETTINGS_IDS_BY_NAME[nationalSetting]
            rank = -1 if rank is None else rank
            self.__account._doCmdInt3(AccountCommands.CMD_NEW_YEAR_CRAFT, toyTypeID, settingID, rank, callback)
        return

    def breakToys(self, toys, callback=_defaultLogger):
        if self.__account is not None:
            toysArr = sum(((toyID, count) for toyID, count in toys if count > 0), ())
            self.__account._doCmdIntArr(AccountCommands.CMD_NEW_YEAR_BREAK_TOYS, toysArr, callback)
        return

    def markToysAsSeen(self, toys, callback=_defaultLogger):
        if self.__account is not None:
            toysArr = sum((list(pair) for pair in toys), [])
            self.__account._doCmdIntArr(AccountCommands.CMD_NEW_YEAR_SEE_TOYS, toysArr, callback)
        return

    def openBox(self, boxID, callback=_defaultLogger):
        if self.__account is not None:
            self.__account._doCmdStr(AccountCommands.CMD_NEW_YEAR_OPEN_BOX, boxID, callback)
        return

    def openChest(self, chestID, callback=_defaultLogger):
        if self.__account is not None:
            self.__account._doCmdStr(AccountCommands.CMD_NEW_YEAR_OPEN_BOX, chestID, callback)
        return

    def selectDiscount(self, goodieID, variadicDiscountID, callback=_defaultLogger):
        if self.__account is not None:
            self.__account._doCmdIntStr(AccountCommands.CMD_NEW_YEAR_SELECT_DISCOUNT, goodieID, variadicDiscountID, callback)
        return

    def selectTankman(self, nationID, vehicleInnationID, roleID, variadicTankmanID, callback=_defaultLogger):
        if self.__account is not None:
            self.__account._doCmdIntArrStrArr(AccountCommands.CMD_NEW_YEAR_SELECT_TANKMAN, (nationID, vehicleInnationID, roleID), (variadicTankmanID,), callback)
        return

    def __onEventsDataChanged(self):
        if self.__account is None:
            return
        else:
            ingameEventsCompressed = self.__account.eventsData.get(EVENT_CLIENT_DATA.INGAME_EVENTS, None)
            if not ingameEventsCompressed:
                return
            ingameEvents = cPickle.loads(zlib.decompress(ingameEventsCompressed))
            newYearEventData = ingameEvents.get('newYearEvent', None)
            if newYearEventData is None:
                LOG_ERROR('ClientNewYear.__onEventsDataChanged: missing newYearEvent data.')
                return
            state = newYearEventData['state']
            if state != self.__state:
                self.__state = state
                self.onStateChanged(state)
            return

    def __addToCollection(self, toyIDs):
        diff = set(toyIDs).difference(self.__toyCollection)
        if not diff:
            return
        toysCache = new_year_types.g_cache.toys
        ratings = self.__collectionRatings
        for toyID in diff:
            toyDescr = toysCache[toyID]
            ratings[toyDescr.settingID] += toyDescr.rating

        self.__toyCollection.update(diff)
        self.onToyCollectionChanged(diff)

    def addToys(self, toys, callback=_defaultLogger):
        if self.__account is not None:
            self.__account._doCmdIntArr(AccountCommands.CMD_NEW_YEAR_ADD_TOYS_DEV, toys, callback)
        return

    def addBox(self, boxID, callback=_defaultLogger):
        if boxID not in new_year_types.g_cache.boxes:
            LOG_ERROR('addBox: wrong boxID')
            return
        else:
            if self.__account is not None:
                self.__account._doCmdStr(AccountCommands.CMD_NEW_YEAR_ADD_TOKEN_DEV, boxID, callback)
            return

    def addChest(self, chestID, callback=_defaultLogger):
        if chestID not in new_year_types.g_cache.chests:
            LOG_ERROR('addChest: wrong chestID')
            return
        else:
            if self.__account is not None:
                self.__account._doCmdStr(AccountCommands.CMD_NEW_YEAR_ADD_TOKEN_DEV, chestID, callback)
            return

    def addVariadicDiscount(self, varDiscountID, callback=_defaultLogger):
        if varDiscountID not in new_year_types.g_cache.variadicDiscounts:
            LOG_ERROR('addVariadicDiscount: wrong varDiscountID')
            return
        else:
            if self.__account is not None:
                self.__account._doCmdStr(AccountCommands.CMD_NEW_YEAR_ADD_TOKEN_DEV, varDiscountID, callback)
            return

    def addVariadicTankman(self, variadicTankmanID, callback=_defaultLogger):
        if variadicTankmanID not in new_year_types.g_cache.variadicTankmen:
            LOG_ERROR('addVariadicTankman: wrong variadicTankmanID')
            return
        else:
            if self.__account is not None:
                self.__account._doCmdStr(AccountCommands.CMD_NEW_YEAR_ADD_TOKEN_DEV, variadicTankmanID, callback)
            return

    def setState(self, state):
        self.__state = state
        self.onStateChanged(self.__state)


def _unpackBinaryCollection(binaryData):
    for bytePos, byte in enumerate(binaryData):
        for bitPos in xrange(8):
            if byte & 1 << bitPos:
                yield bytePos * 8 + bitPos
