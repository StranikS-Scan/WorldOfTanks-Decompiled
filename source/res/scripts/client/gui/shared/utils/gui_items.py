# Embedded file name: scripts/client/gui/shared/utils/gui_items.py
import BigWorld, nations
import cPickle as pickle
from types import IntType
from AccountCommands import LOCK_REASON
from account_shared import LayoutIterator
from gui.shared.utils import ItemsParameters, CLIP_VEHICLES_CD_PROP_NAME
from items.vehicles import VehicleDescr, getDictDescr, getDefaultAmmoForGun, VEHICLE_CLASS_TAGS
from items import ITEM_TYPE_NAMES, ITEM_TYPE_INDICES, getTypeInfoByName
from helpers.i18n import makeString
from adisp import async, process
from debug_utils import *
from gui import SystemMessages, nationCompareByIndex, GUI_SETTINGS
from items.tankmen import TankmanDescr, getNationConfig, getSkillsConfig, ACTIVE_SKILLS
from items import vehicles
from helpers.i18n import convert
from gui.shared.utils import ParametersCache

class VEHICLE_ELITE_STATE():
    NOT_ELITE = 0
    NOT_FULLY_ELITE = 1
    FULLY_ELITE = 2


_ITEM_TYPES_ORDER = ['lightTank',
 'mediumTank',
 'heavyTank',
 'AT-SPG',
 'SPG',
 'vehicleGun',
 'vehicleTurret',
 'vehicleEngine',
 'vehicleChassis',
 'vehicleRadio',
 'ARMOR_PIERCING',
 'ARMOR_PIERCING_CR',
 'HOLLOW_CHARGE',
 'HIGH_EXPLOSIVE',
 'optionalDevice',
 'equipment']
_ICONS_MASK = '../maps/icons/%(type)s/%(subtype)s%(unicName)s.png'

class FittingItem(object):

    def __init__(self, compactDescr, itemTypeName, priceOrder = (0, 0), suitFor = []):
        self.__userType = None
        self.compactDescr = compactDescr
        self.itemTypeName = itemTypeName
        self.priceOrder = priceOrder
        self.price = (0, 0)
        self.isCurrent = False
        self.__suitableVehicles = suitFor
        self.index = None
        return

    @property
    def isRemovable(self):
        if self.type == ITEM_TYPE_NAMES[9]:
            return self.descriptor['removable']
        return True

    @property
    def userType(self):
        """
        Translated item type
        """
        if self.__userType is None:
            self.__userType = getTypeInfoByName(self.itemTypeName)['userString']
        return self.__userType

    @property
    def type(self):
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            tags = VEHICLE_CLASS_TAGS.intersection(self.descriptor.type.tags)
            for tag in tags:
                return tag

        elif self.itemTypeName == ITEM_TYPE_NAMES[10]:
            return self.descriptor['kind']
        return self.itemTypeName

    def getPriceByModifiers(self, sellPriceModifiers):
        return BigWorld.player().shop.getSellPrice(self.priceOrder, sellPriceModifiers, ITEM_TYPE_INDICES[self.itemTypeName])

    @property
    def hasTurrets(self):
        """
        @return: True if vehicle has at least one not fake turret, False otherwise
        """
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            return len(self.descriptor.hull['fakeTurrets']['lobby']) != len(self.descriptor.type.turrets)
        return False

    @property
    def isPremium(self):
        return bool(self.descriptor.type.tags & frozenset(('premium',)))

    @property
    def isSpecial(self):
        return bool(self.descriptor.type.tags & frozenset(('special',)))

    @property
    def isDisabledInRoaming(self):
        from gui.LobbyContext import g_lobbyContext
        return bool(self.tags & frozenset(('disabledInRoaming',))) and g_lobbyContext.getServerSettings().roaming.isInRoaming()

    @property
    def unicName(self):
        """
        Item identificator (name in xml)
        """
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            return self.descriptor.type.name
        return self.descriptor['name']

    @property
    def name(self):
        """
        Translated item identificator (userString in xml)
        """
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            return self.descriptor.type.userString
        return self.descriptor['userString']

    @property
    def longName(self):
        """
        Translated item name (userType + identificator)
        """
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            return getVehicleFullName(self.descriptor)
        if self.itemTypeName == ITEM_TYPE_NAMES[10]:
            if self.nation == nations.INDICES['germany']:
                caliber = float(self.descriptor['caliber']) / 10
                dimension = makeString('#item_types:shell/dimension/sm')
            elif self.nation == nations.INDICES['usa']:
                caliber = float(self.descriptor['caliber']) / 25.4
                dimension = makeString('#item_types:shell/dimension/inch')
            else:
                caliber = self.descriptor['caliber']
                dimension = makeString('#item_types:shell/dimension/mm')
            return makeString('#item_types:shell/name') % {'kind': makeString('#item_types:shell/kinds/' + self.descriptor['kind']),
             'name': self.name,
             'caliber': BigWorld.wg_getNiceNumberFormat(caliber),
             'dimension': dimension}
        try:
            return self.userType + ' ' + self.descriptor['userString']
        except KeyError:
            return self.userType

    @property
    def shortName(self):
        """
        Translated item name for vehicle 6 letters
        Translated item name for module 10 letters
        """
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            return self.descriptor.type.shortUserString
        return self.descriptor['shortUserString']

    @property
    def description(self):
        """
        Translated description from xml
        """
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            if self.descriptor.type.description.find('_descr') == -1:
                return self.descriptor.type.description
            return ''
        else:
            return self.descriptor['description']

    @property
    def level(self):
        if self.itemTypeName in (ITEM_TYPE_NAMES[9], ITEM_TYPE_NAMES[10], ITEM_TYPE_NAMES[11]):
            return 0
        elif self.itemTypeName == ITEM_TYPE_NAMES[1]:
            return self.descriptor.level
        elif self.descriptor.has_key('level'):
            return self.descriptor['level']
        else:
            LOG_ERROR('Module %s:%s without level' % (self.type, self.unicName))
            return 0

    @property
    def tableName(self):
        return self.getTableName()

    def getTableName(self, vehicle = None):
        """
        Translated table name consists short description of main parameters
        Short name not included
        """
        if not GUI_SETTINGS.technicalInfo:
            return ''
        elif self.itemTypeName in (ITEM_TYPE_NAMES[9], ITEM_TYPE_NAMES[11]):
            return self.description
        else:
            try:
                description = makeString('#menu:descriptions/' + self.itemTypeName)
                vDescr = vehicle.descriptor if vehicle is not None else None
                itemParams = dict(ItemsParameters.g_instance.getParameters(self.descriptor, vDescr))
                if self.itemTypeName == ITEM_TYPE_NAMES[1]:
                    itemParams['caliber'] = BigWorld.wg_getIntegralFormat(self.descriptor.gun['shots'][0]['shell']['caliber'])
                return description % itemParams
            except Exception:
                LOG_CURRENT_EXCEPTION()
                return ''

            return

    @property
    def toolTip(self):
        """
        Long description for ToolTips an other usage
        Includes full list of parameters
        """
        return self.longName

    def getParams(self, vehicle):
        from gui.shared.utils import ItemsParameters
        vDescr = vehicle.descriptor if vehicle is not None else None
        return ItemsParameters.g_instance.get(self.descriptor, vDescr)

    def isClipGun(self, vehicleDescr = None):
        if self.type == ITEM_TYPE_NAMES[4]:
            compatibles = ParametersCache.g_instance.getGunCompatibles(self.descriptor, vehicleDescr)
            clipVehicleList = compatibles[CLIP_VEHICLES_CD_PROP_NAME]
            if vehicleDescr is not None:
                if len(clipVehicleList) > 0:
                    if type(vehicleDescr) is IntType:
                        intCD = vehicleDescr
                    else:
                        intCD = vehicleDescr.type.compactDescr
                    for cVdescr in clipVehicleList:
                        if cVdescr == intCD:
                            return True

            elif len(clipVehicleList) > 0 and len(compatibles['vehicles']) == 0:
                return True
        return False

    @property
    def suitableVehicles(self):
        """
        List of vehicles module fits
        """
        return self.__suitableVehicles

    @property
    def tags(self):
        """
        Set of tags
        """
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            return self.descriptor.type.tags
        return self.descriptor['tags']

    @property
    def oldIcon(self):
        """
        path wheree icon for item stored
        """
        return _ITEM_TYPES_ORDER.index(self.type) + 2 + self.nation * 5

    @property
    def icon(self):
        """
        path where icon for item stored
        """
        if self.itemTypeName in (ITEM_TYPE_NAMES[9], ITEM_TYPE_NAMES[11]):
            return self.descriptor.icon[0]
        if self.itemTypeName == ITEM_TYPE_NAMES[10]:
            return _ICONS_MASK[:-4] % {'type': self.itemTypeName,
             'subtype': '',
             'unicName': self.descriptor['icon'][0]}
        return _ICONS_MASK % {'type': self.itemTypeName,
         'subtype': '',
         'unicName': self.unicName.replace(':', '-')}

    @property
    def iconContour(self):
        """
        path where icon contour for item stored
        """
        return _ICONS_MASK % {'type': self.itemTypeName,
         'subtype': 'contour/',
         'unicName': self.unicName.replace(':', '-')}

    @property
    def iconSmall(self):
        """
        path where icon contour for item stored
        """
        return _ICONS_MASK % {'type': self.itemTypeName,
         'subtype': 'small/',
         'unicName': self.unicName.replace(':', '-')}

    def _getMessage(self, type, extra = None):
        message = '#system_messages:fitting/'
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            if extra is not None and len(extra) == 2:
                message += 'vehicle_dismantling_'
            else:
                message += 'vehicle_'
        elif self.itemTypeName == ITEM_TYPE_NAMES[10]:
            message += 'shell_'
        elif self.itemTypeName in (ITEM_TYPE_NAMES[9], ITEM_TYPE_NAMES[11]):
            message += 'artefact_'
        else:
            message += 'module_'
        message += type
        args = [message]
        if self.itemTypeName not in (ITEM_TYPE_NAMES[1], ITEM_TYPE_NAMES[10]):
            args.append(self.userType)
        args.append(self.name)
        if extra is not None:
            if isinstance(extra, tuple):
                args.extend(extra)
            else:
                args.append(extra)
        return makeString(*tuple(args))

    @staticmethod
    def unpack(pickleString):
        data = pickle.loads(pickleString)
        try:
            return data[0](*data[1])
        except:
            return None

        return None

    def __cmp__(self, other):
        if other is None:
            return 1
        nationCompareResult = nationCompareByIndex(self.nation, other.nation)
        if nationCompareResult:
            return nationCompareResult
        if self.type in _ITEM_TYPES_ORDER and other.type in _ITEM_TYPES_ORDER:
            if _ITEM_TYPES_ORDER.index(self.type) < _ITEM_TYPES_ORDER.index(other.type):
                return -1
            if _ITEM_TYPES_ORDER.index(self.type) > _ITEM_TYPES_ORDER.index(other.type):
                return 1
        else:
            LOG_WARNING('%s or %s is not in _ITEM_TYPES_ORDER = %s' % (self.type, other.type, _ITEM_TYPES_ORDER))
        if self.level < other.level:
            return -1
        elif self.level > other.level:
            return 1
        elif self.priceOrder[1] < other.priceOrder[1]:
            return -1
        elif self.priceOrder[1] > other.priceOrder[1]:
            return 1
        elif self.priceOrder[0] < other.priceOrder[0]:
            return -1
        elif self.priceOrder[0] > other.priceOrder[0]:
            return 1
        elif self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        else:
            return 0

    def __eq__(self, other):
        if other is None:
            return False
        elif self.itemTypeName == ITEM_TYPE_NAMES[1]:
            return self.descriptor.type.id == other.descriptor.type.id
        else:
            return self.compactDescr == other.compactDescr


class ShopItem(FittingItem):
    """
    Represent an item from the shop
    @param itemTypeName: item type @see: items.ITEM_TYPE_NAMES
    @param id: in nation ID for vehicles, compactDescription for others
    @param priceOrder: price in shop
    @param suitFor: a list of vehicles module fits @see: self.suitableVehicles (not mandatory)
    @param nation: nation index from nations.INDICES (not mandatory for all except vehicles)
    """

    def __init__(self, itemTypeName, compactDescr, nation = None, priceOrder = (0, 0), hidden = False):
        self.__descriptor = None
        FittingItem.__init__(self, compactDescr, itemTypeName, priceOrder)
        self.__nation = nation
        self.hidden = hidden
        if not (nation is None and self.itemTypeName == ITEM_TYPE_NAMES[1] and 'vehicle without nation'):
            raise AssertionError
        return

    @property
    def priceSync(self):
        return (self.priceOrder[0], self.priceOrder[1])

    @async
    def getPrice(self, callback):
        price = (self.priceOrder[0], self.priceOrder[1])
        callback(price)

    @property
    def nation(self):
        """
        Nation index from nations.INDICES
        """
        if self.__nation is None:
            self.__nation = self.descriptor['id'][0]
        return self.__nation

    @property
    def descriptor(self):
        """
        Descriptor for Item
        VehicleDescr for vehicles
        """
        if self.__descriptor is None:
            if self.itemTypeName == ITEM_TYPE_NAMES[1]:
                self.__descriptor = VehicleDescr(typeID=(self.nation, self.compactDescr))
            else:
                self.__descriptor = getDictDescr(self.compactDescr)
        return self.__descriptor

    @property
    def target(self):
        """
        Return 3 for all items
        InventoryItem return 1 if module is current, 2 for all other
        """
        return 3

    @async
    @process
    def buy(self, count = 1, isShell = False, isCrew = True, crew_type = 0, isSlot = False, buyForCredits = False, callback = None):
        """
        Buy this module in shop, and return it as InventoryItem in callback
        For vehicle buy default shells and crew.
        @param callback:
        @param count: number of modules to buy
        @param buyForCredits: buy gold ammo for credits
        @todo: refactor this (add auto apply), make it independent from other code? do not use callback
        """

        def getBuyResponse(code, itemInvID = None):
            if code >= 0:
                if callback is not None:
                    component = InventoryItem(self.itemTypeName, self.compactDescr, id=itemInvID, count=count)
                    message = ''
                    if self.itemTypeName == ITEM_TYPE_NAMES[1]:
                        message = self._getMessage('buy_success', formatPrice(buyPrice))
                    else:
                        message = self._getMessage('buy_success', (count, formatPrice(buyPrice)))
                    callback((True,
                     message,
                     getPurchaseSysMessageType(buyPrice),
                     component))
            else:
                LOG_ERROR('Server response en error for buy item(%s - %s) operation code: %s' % (self.itemTypeName, self.name, code))
                from AccountCommands import RES_CENTER_DISCONNECTED
                message = 'buy_server_error'
                if code == RES_CENTER_DISCONNECTED:
                    message = 'buy_server_error_centerDown'
                if callback is not None:
                    callback((False, self._getMessage(message)))
            return

        from gui.shared.utils.requesters import DeprecatedStatsRequester, ShopRequester, StatsRequester
        shopRqs = yield ShopRequester().request()
        statsRqs = yield StatsRequester().request()
        buyPrice = yield self.getPrice()
        buyGoldAmmoForCredits = buyForCredits and buyPrice[1] > 0 and (self.itemTypeName == 'shell' and shopRqs.isEnabledBuyingGoldShellsForCredits or self.itemTypeName == 'equipment' and shopRqs.isEnabledBuyingGoldEqsForCredits)
        buyPrice = [buyPrice[0] * count, buyPrice[1] * count]
        if buyGoldAmmoForCredits:
            buyPrice = [buyPrice[1] * shopRqs.exchangeRate, 0]
        if self.itemTypeName == 'vehicle':
            tankmenCount = len(self.descriptor.type.crewRoles)
            if isCrew:
                if crew_type == 1:
                    buyPrice[0] += shopRqs.tankmanCost[1]['credits'] * tankmenCount
                elif crew_type == 2:
                    buyPrice[1] += shopRqs.tankmanCost[2]['gold'] * tankmenCount
            if isShell:
                shells = vehicles.getDefaultAmmoForGun(self.descriptor.gun)
                for i in range(0, len(shells), 2):
                    _, nationIdx, shellInnationIdx = vehicles.parseIntCompactDescr(shells[i])
                    shellPrice = yield DeprecatedStatsRequester().getShellPrice(nationIdx, shells[i])
                    buyPrice[0] += shellPrice[0] * shells[i + 1]
                    buyPrice[1] += shellPrice[1] * shells[i + 1]

            if isSlot:
                success = yield DeprecatedStatsRequester().buySlot()
                if not success:
                    SystemMessages.g_instance.pushI18nMessage('#system_messages:buy_slot/server_error', SystemMessages.SM_TYPE.Error)
                    return
                price = yield DeprecatedStatsRequester().getSlotsPrices()
                buyPrice[1] += price[1][0]
        if (statsRqs.credits, statsRqs.gold) >= tuple(buyPrice):
            if self.itemTypeName == 'vehicle':
                BigWorld.player().shop.buyVehicle(self.descriptor.type.id[0], self.descriptor.type.id[1], isShell, isCrew, crew_type, -1, callback=getBuyResponse)
            else:
                BigWorld.player().shop.buy(ITEM_TYPE_INDICES[self.itemTypeName], self.nation, self.compactDescr, int(count), int(buyGoldAmmoForCredits), getBuyResponse)
        elif callback is not None:
            price = (buyPrice[0] - statsRqs.credits, buyPrice[1] - statsRqs.gold)
            callback((False, self._getMessage('buy_money_error', formatPrice(price))))
        return

    def pack(self):
        return pickle.dumps([ShopItem, (self.itemTypeName,
          self.compactDescr,
          self.nation,
          self.priceOrder)])


class InventoryItem(FittingItem):
    """
    Represent an item from the inventory
    @param itemTypeName: item type @see: items.ITEM_TYPE_NAMES
    @param id: in nation ID for vehicles, compactDescription for others
    @param priceOrder: price in shop if needed for ordering
    @param suitFor: a list of vehicles module fits @see: self.suitableVehicles (not mandatory)
    @param nation: nation index from nations.INDICES (not mandatory for all except vehicles)
    """

    def __init__(self, itemTypeName, compactDescr = None, id = None, priceOrder = (0, 0), count = 1, isCurrent = False):
        self.__descriptor = None
        FittingItem.__init__(self, compactDescr, itemTypeName, priceOrder)
        self.inventoryId = id
        self.count = count
        self.isCurrent = isCurrent
        return

    @async
    def getPrice(self, callback):

        def __valueResponse(responseCode, value, revision = 0):
            if responseCode < 0:
                LOG_ERROR('Server return error for shop getSellPrice request: responseCode=%s' % responseCode)
            if callback:
                callback((value, 0))

        raise hasattr(BigWorld.player(), 'shop') or AssertionError('Request from shop is not possible')
        BigWorld.player().shop.getComponentSellPrice(self.compactDescr, __valueResponse)

    @property
    def isSellPosible(self):
        return True

    @property
    def nation(self):
        """
        Nation index from nations.INDICES
        """
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            return self.descriptor.type.id[0]
        return self.descriptor['id'][0]

    @property
    def descriptor(self):
        """
        Descriptor for Item
        VehicleDescr for vehicles
        TankmanDescr for tankman
        """
        if self.__descriptor is None:
            if self.itemTypeName == 'vehicle':
                self.__descriptor = VehicleDescr(compactDescr=self.compactDescr)
            elif self.itemTypeName == 'tankman':
                self.__descriptor = TankmanDescr(compactDescr=self.compactDescr)
            else:
                self.__descriptor = getDictDescr(self.compactDescr)
        return self.__descriptor

    @property
    def target(self):
        """
        Return 1 if module is current, 2 for all other
        ShopItem return 3 for all items
        """
        if self.isCurrent:
            return 1
        return 2

    @async
    @process
    def apply(self, callback, slotIdx = None, isUseGold = False, invVehicle = None):
        """
        Install this module to current vehicle
        @param callback:
        @todo: refactor this, make it independent from other code? do not use callback
        """
        from gui.shared.utils.requesters import Requester
        invVehicles = yield Requester('vehicle').getFromInventory()
        if self.itemTypeName == ITEM_TYPE_NAMES[1]:
            pass
        else:
            if invVehicle is None:
                for v in invVehicles:
                    from CurrentVehicle import g_currentVehicle
                    if v.inventoryId == g_currentVehicle.invID:
                        invVehicle = v
                        break

            if invVehicle is not None and invVehicle.isAlive():
                if self.itemTypeName == ITEM_TYPE_NAMES[11]:
                    currents = list(invVehicle.equipments)
                    if len(currents) > slotIdx and currents[slotIdx] != self.compactDescr:
                        currents[slotIdx] = self.compactDescr
                        calbackType = self.__responseApply
                    else:
                        currents[slotIdx] = 0
                        calbackType = self.__responseRemove
                    BigWorld.player().inventory.equipEquipments(invVehicle.inventoryId, currents, lambda code: calbackType(code, callback, invVehicle, slotIdx=slotIdx, equipments=currents))
                    return
                if self.itemTypeName == ITEM_TYPE_NAMES[9]:
                    currents = list(invVehicle.descriptor.optionalDevices)
                    for i, current in enumerate(currents):
                        if current:
                            currents[i] = current.compactDescr

                    if self.compactDescr in currents:
                        mayRemove = invVehicle.descriptor.mayRemoveOptionalDevice(slotIdx)
                        if mayRemove[0]:
                            BigWorld.player().inventory.equipOptionalDevice(invVehicle.inventoryId, 0, slotIdx, isUseGold, lambda code: self.__responseRemove(code, callback, invVehicle, slotIdx=slotIdx, isUseGold=isUseGold))
                            return
                        error = mayRemove[1].replace(' ', '_')
                        type = 'remove_error_' + error
                        value = (False, self._getMessage(type))
                    else:
                        mayInstall = invVehicle.descriptor.mayInstallOptionalDevice(self.compactDescr, slotIdx)
                        if mayInstall[0]:
                            BigWorld.player().inventory.equipOptionalDevice(invVehicle.inventoryId, self.compactDescr, slotIdx, isUseGold, lambda code: self.__responseApply(code, callback, invVehicle, slotIdx=slotIdx))
                            return
                        error = mayInstall[1].replace(' ', '_')
                        type = 'apply_error_' + error
                        value = (False, self._getMessage(type))
                elif self.descriptor['id'] == invVehicle.descriptor.getComponentsByType(self.itemTypeName)[0]['id']:
                    value = (False, self._getMessage('apply_error_is_current'))
                else:
                    if self.itemTypeName != ITEM_TYPE_NAMES[3]:
                        mayInstall = invVehicle.descriptor.mayInstallComponent(self.compactDescr)
                        if mayInstall[0]:
                            BigWorld.player().inventory.equip(invVehicle.inventoryId, self.compactDescr, lambda code, ext: self.__responseApply(code, callback, invVehicle, ext))
                            return
                        error = mayInstall[1].replace(' ', '_')
                        type = 'apply_error_' + error
                        if error == 'too_heavy' and self.itemTypeName == ITEM_TYPE_NAMES[2]:
                            type += '_chassis'
                    else:
                        mayInstall = invVehicle.descriptor.mayInstallTurret(self.compactDescr, 0)
                        if mayInstall[0]:
                            BigWorld.player().inventory.equipTurret(invVehicle.inventoryId, self.compactDescr, 0, lambda code, ext: self.__responseApply(code, callback, invVehicle, ext, 0))
                            return
                        self.__applyTurret(mayInstall[1] == 'too heavy', callback, invVehicle)
                        return
                    value = (False, self._getMessage(type))
            else:
                message = 'apply_vehicle_'
                if self.itemTypeName == ITEM_TYPE_NAMES[9]:
                    currents = list(invVehicle.descriptor.optionalDevices)
                    for i, current in enumerate(currents):
                        if current:
                            currents[i] = current.compactDescr

                    if self.compactDescr in currents:
                        if not self.isRemovable and isUseGold or self.isRemovable:
                            message = 'remove_vehicle_'
                        else:
                            message = 'destroy_vehicle_'
                if invVehicle.isLocked():
                    value = (False, self._getMessage(message + 'locked'))
                else:
                    value = (False, self._getMessage(message + 'broken'))
        if callback is not None:
            value = (value[0], value[1], {})
            callback(value)
        return

    @process
    def __applyTurret(self, isToHeavy, callback, invVehicle):
        from gui.shared.utils.requesters import Requester
        iGuns = yield Requester(ITEM_TYPE_NAMES[4]).getFromInventory()
        iGuns.sort(reverse=True)
        for iGun in iGuns:
            for gun in self.descriptor['guns']:
                if iGun.compactDescr == gun['compactDescr']:
                    mayInstall = invVehicle.descriptor.mayInstallTurret(self.compactDescr, gun['compactDescr'])
                    if mayInstall[0]:
                        BigWorld.player().inventory.equipTurret(invVehicle.inventoryId, self.compactDescr, gun['compactDescr'], lambda code, ext: self.__responseApply(code, callback, invVehicle, ext, gun['compactDescr']))
                        return
                    if mayInstall[1] == 'too heavy':
                        isToHeavy = True

        if isToHeavy:
            value = (False, self._getMessage('apply_error_too_heavy'), [])
        else:
            value = (False, self._getMessage('apply_error_no_gun'), [])
        if callback is not None:
            callback(value)
        return

    def __responseApply(self, code, callback, invVehicle, removed = None, gun = None, slotIdx = None, equipments = None):
        if removed is None:
            removed = {}
        if code >= 0:
            value = (True, self._getMessage('apply_success'), removed)
            if equipments:
                pass
            elif slotIdx is not None:
                invVehicle.descriptor.installOptionalDevice(self.compactDescr, slotIdx)
            elif gun is not None:
                invVehicle.descriptor.installTurret(self.compactDescr, gun)
                if gun:
                    value = (True, self._getMessage('apply_success_gun_change', getDictDescr(gun)['userString']), removed)
            else:
                invVehicle.descriptor.installComponent(self.compactDescr)
        else:
            LOG_ERROR('Server response an error for install item(%s - %s) operation code: %s' % (self.itemTypeName, self.descriptor['name'], code))
            value = (False, self._getMessage('server_apply_error'), removed)
        if callback is not None:
            callback(value)
        return

    @process
    def __responseRemove(self, code, callback, invVehicle, slotIdx, equipments = [], isUseGold = False):
        from gui.shared.utils.requesters import DeprecatedStatsRequester
        cost = yield DeprecatedStatsRequester().getPaidRemovalCost()
        if code >= 0:
            if equipments:
                pass
            else:
                invVehicle.descriptor.removeOptionalDevice(slotIdx)
            if self.isRemovable:
                value = (True, self._getMessage('remove_success'), {})
            elif isUseGold:
                value = (True, self._getMessage('remove_gold_success', cost), {})
            else:
                value = (True, self._getMessage('destroy_success'), {})
        else:
            LOG_ERROR('Server response en error for remove item(%s - %s) operation code: %s' % (self.itemTypeName, self.descriptor['name'], code))
            value = (False, self._getMessage('server_remove_error'))
        if callback is not None:
            callback(value)
        return

    @async
    @process
    def sell(self, callback = None, count = 1):
        """
        Buy this module in shop, and return it as InventoryItem in callback
        @param callback:
        @param count: number of modules to buy
        @todo: refactor this (add auto apply), make it independent from other code? do not use callback
        """

        def getSellResponse(code):
            if code >= 0:
                if callback is not None:
                    message = self._getMessage('sell_success', (count, formatPrice(sellPrice)))
                    callback((True, message))
            else:
                LOG_ERROR('Server response en error for sell item(%s - %s) operation code: %s' % (self.itemTypeName, self.name, code))
                if callback is not None:
                    callback((False, self._getMessage('sell_server_error')))
            return

        sellPrice = yield self.getPrice()
        sellPrice = (sellPrice[0] * count, sellPrice[1] * count)
        BigWorld.player().inventory.sell(ITEM_TYPE_INDICES[self.itemTypeName], self.inventoryId if self.inventoryId is not None else self.compactDescr, count, getSellResponse)
        return

    def pack(self):
        return pickle.dumps([InventoryItem, (self.itemTypeName, self.compactDescr, self.inventoryId)])


class InventoryVehicle(InventoryItem):
    NOT_FULL_AMMO_MULTIPLIER = 0.2

    class STATE_LEVEL:
        CRITICAL = 'critical'
        INFO = 'info'
        WARNING = 'warning'
        RENTED = 'rented'

    def __init__(self, compactDescr, id, crew = [], shells = {}, ammoLayout = {}, repairCost = 0, health = 0, lock = 0, equipments = [], equipmentsLayout = [], settings = 0):
        InventoryItem.__init__(self, ITEM_TYPE_NAMES[1], compactDescr=compactDescr, id=id, count=1)
        self.__shells = []
        self.__ammoLayout = ammoLayout
        self.setShellsList(shells)
        self.repairCost = repairCost
        self.__health = health
        self.__crew = crew
        self.lock = lock
        self.__equipments = equipments
        self.equipmentsLayout = equipmentsLayout
        self.__settings = settings

    @async
    @process
    def sell(self, sellEqs = False, performDismantling = False, callback = None):
        from gui.shared.utils.requesters import VehicleItemsRequester
        if not self.isSellPosible:
            callback((False, self._getMessage('sell_server_error')))
            return
        getMoney, putMoney = yield self.getSellPrice(sellEqs, performDismantling)

        def getSellResponse(code):
            if code >= 0:
                if callback is not None:
                    formatArgs = [formatPrice(getMoney)]
                    if putMoney[0] != 0 or putMoney[1] != 0:
                        formatArgs.append(formatPrice(putMoney))
                    message = self._getMessage('sell_success', tuple(formatArgs))
                    callback((True, message))
            else:
                LOG_ERROR('Server response en error for sell item(%s - %s) operation code: %s' % (self.itemTypeName, self.name, code))
                if callback is not None:
                    callback((False, self._getMessage('sell_server_error')))
            return

        componentCompDescrs = list()
        devs = VehicleItemsRequester((self,)).getItems(('optionalDevice',))
        if sellEqs:
            for shell in self.shells:
                componentCompDescrs.append(shell.compactDescr)

            eqs = VehicleItemsRequester((self,)).getItems(('equipment',))
            for eq in eqs:
                componentCompDescrs.append(eq.compactDescr)

            for dev in devs:
                if dev.descriptor['removable']:
                    componentCompDescrs.append(dev.compactDescr)

        if not performDismantling:
            for dev in devs:
                if not dev.descriptor['removable']:
                    componentCompDescrs.append(dev.compactDescr)

        BigWorld.player().inventory.sellVehicle(self.inventoryId, sellEqs, sellEqs, False, sellEqs, performDismantling, sellEqs, componentCompDescrs, getSellResponse)

    @property
    def canSell(self):
        st = self.getState()
        return st == 'undamaged' or st == 'crewNotFull' or st == 'ammoNotFull'

    @property
    def vehicleType(self):
        for tag in vehicles.VEHICLE_CLASS_TAGS.intersection(self.descriptor.type.tags):
            return tag

    @async
    @process
    def getSellPrice(self, sellEqs = True, performDismantling = False, callback = None):
        from gui.shared.utils.requesters import VehicleItemsRequester, DeprecatedStatsRequester
        getMoney = yield self.getPrice()
        getMoney = list(getMoney)
        putMoney = [0, 0]
        artefacts = VehicleItemsRequester((self,)).getItems(('equipment', 'optionalDevice'))
        devicesRemovablePrice = 0
        devicesNotRemovablePrice = 0
        devicesNotRemovableCount = 0
        equipmentsPrice = 0
        shellsPrice = yield DeprecatedStatsRequester().getAmmoSellPrice(self.getShellsList())
        for art in artefacts:
            artPrice = yield art.getPrice()
            if not hasattr(art.descriptor, 'removable') or art.descriptor['removable']:
                if not hasattr(art.descriptor, 'removable'):
                    equipmentsPrice += artPrice[0]
                else:
                    devicesRemovablePrice += artPrice[0]
            else:
                devicesNotRemovablePrice += artPrice[0]
                devicesNotRemovableCount += 1

        getMoney[0] += shellsPrice[0] + equipmentsPrice
        if not sellEqs:
            getMoney[0] -= devicesRemovablePrice
            getMoney[0] -= shellsPrice[0]
            getMoney[0] -= equipmentsPrice
        if performDismantling:
            getMoney[0] -= devicesNotRemovablePrice
            removeDeviceCost = yield DeprecatedStatsRequester().getPaidRemovalCost()
            putMoney[1] += removeDeviceCost * devicesNotRemovableCount
        callback((getMoney, putMoney))

    @async
    @process
    def sellParams(self, callback):
        from gui.shared.utils.requesters import VehicleItemsRequester, DeprecatedStatsRequester, Requester
        artefacts = VehicleItemsRequester((self,)).getItems(('equipment', 'optionalDevice'))
        removeDeviceCost = yield DeprecatedStatsRequester().getPaidRemovalCost()
        shopVehicles = yield Requester('vehicle').getFromShop()
        vehiclePrice = yield self.getPrice()
        shellsPrice = yield DeprecatedStatsRequester().getAmmoSellPrice(self.getShellsList())
        shellsCount = 0
        for shell in self.shells:
            shellsCount += shell.count

        vehicleFullPrice = vehiclePrice[0] + shellsPrice[0]
        crewCount = 0
        for tankman in self.crew:
            if tankman is not None:
                crewCount += 1

        artefactsCount = 0
        artefactsRemovableCount = 0
        artefactsRemovablePrice = shellsPrice[0]
        artefactsNotRemovablePrice = 0
        artefactsDismantlingPrice = 0
        for art in artefacts:
            artefactsCount += 1
            artPrice = yield art.getPrice()
            if not hasattr(art.descriptor, 'removable') or art.descriptor['removable']:
                if not hasattr(art.descriptor, 'removable'):
                    vehicleFullPrice += artPrice[0]
                artefactsRemovablePrice += artPrice[0]
                artefactsRemovableCount += 1
            else:
                artefactsNotRemovablePrice += artPrice[0]
                artefactsDismantlingPrice += removeDeviceCost

        callback([self.pack(),
         makeString('#dialogs:vehicleSellDialog/title') % self.name,
         makeString('#dialogs:vehicleSellDialog/content/tankmenField') % crewCount,
         makeString('#dialogs:vehicleSellDialog/content/equipmentsField') % artefactsCount,
         makeString('#dialogs:vehicleSellDialog/content/shellsField') % shellsCount,
         vehicleFullPrice,
         artefactsRemovablePrice,
         artefactsNotRemovablePrice,
         artefactsDismantlingPrice,
         crewCount != 0 or artefactsRemovableCount != 0 or shellsCount != 0])
        return

    @async
    @process
    def isUnique(self, callback):
        from gui.shared.utils.requesters import Requester
        shopVehicles = yield Requester('vehicle').getFromShop()
        isUnique = True
        for sv in shopVehicles:
            if sv.descriptor.type.id == self.descriptor.type.id:
                isUnique = sv.hidden
                break

        callback(isUnique)

    @async
    def getPrice(self, callback):

        def __valueResponse(responseCode, value, revision = 0):
            if responseCode < 0:
                LOG_ERROR('Server return error for shop getSellPrice request: responseCode=%s' % responseCode)
            if callback:
                callback((value, 0))

        raise hasattr(BigWorld.player(), 'shop') or AssertionError('Request from shop is not possible')
        BigWorld.player().shop.getVehicleSellPrice(self.compactDescr, __valueResponse)

    def __getHealth(self):
        if not self.repairCost:
            return self.descriptor.maxHealth
        if self.__health > 0:
            return self.__health
        return 0

    def __setHealth(self, value):
        self.__health = min(value, self.descriptor.maxHealth)

    health = property(__getHealth, __setHealth)

    @property
    def crew(self):
        return self.__crew

    def isCrewFull(self):
        return None not in self.__crew and self.__crew != []

    def isAmmoFull(self):
        loadedCount = 0
        for shell in self.shells:
            loadedCount += shell.count

        return loadedCount >= self.getShellsMaxCount() * self.NOT_FULL_AMMO_MULTIPLIER

    @property
    def modelState(self):
        if self.__health < 0:
            return 'exploded'
        if self.repairCost > 0 and self.health == 0:
            return 'destroyed'
        return 'undamaged'

    @property
    def isSellPosible(self):
        if self.repairCost == 0 and not self.lock:
            return True
        return False

    def __getEquipmets(self):
        return self.__equipments

    equipments = property(__getEquipmets)

    def __getShells(self):
        return self.__shells

    def __setShells(self, shells):
        self.__shells = shells

    shells = property(__getShells, __setShells)

    def getShellsList(self):
        shells = []
        for shell in self.__shells:
            shells.append(shell.compactDescr)
            shells.append(shell.count)

        return shells

    def getShellsDefaultList(self):
        shells = []
        for shell in self.__shells:
            shells.append(shell.compactDescr)
            shells.append(shell.default)

        return shells

    def getShellsMaxCount(self):
        return VehicleItem(self.descriptor.gun).descriptor['maxAmmo']

    def setShellsList(self, shellsList = None):
        if shellsList is None:
            return
        else:
            defaults = dict(self.__getDefaultsForCurrentConfiguration())
            shellsDict = listToDict(shellsList)
            self.__shells = []
            shellsList = list(shellsList)
            for shot in self.descriptor.gun['shots']:
                if shot['shell']['compactDescr'] not in shellsDict.keys():
                    shellsList.append(shot['shell']['compactDescr'])
                    shellsList.append(0)

            def getShellParams(cDescr):
                for shot in self.descriptor.gun['shots']:
                    if cDescr == shot['shell']['compactDescr']:
                        return shot

                return None

            while len(shellsList) != 0:
                cDescr = shellsList[0]
                count = shellsList[1]
                shellsList = shellsList[2:]
                shot = getShellParams(cDescr)
                defaultCount = 0
                boughtForCredits = False
                default = defaults.get(cDescr)
                if default is not None:
                    defaultCount = default[0]
                    boughtForCredits = default[1]
                if shot is not None:
                    self.__shells.append(VehicleShellSlot(shot['shell'], cDescr, count, defaultCount, shot['piercingPower'], shot['shell']['damage'], boughtForCredits))

            return

    def __setEquipmentsList(self, equipemtsList = []):
        self.__equipemts = []
        for equipemt in equipemtsList:
            self.__equipemts.append(VehicleItem(compactDescr=equipemt))

    def __getDefaultsForCurrentConfiguration(self):
        defaults = self.__ammoLayout.get((self.descriptor.turret['compactDescr'], self.descriptor.gun['compactDescr']), [])
        if not defaults:
            defaults = getDefaultAmmoForGun(self.descriptor.gun)
        result = list()
        for compDescr, count, boughtForCredits in LayoutIterator(defaults):
            result.append((compDescr, (count, boughtForCredits)))

        return result

    def __isCurrent(self):
        from CurrentVehicle import g_currentVehicle
        return self.inventoryId == g_currentVehicle.invID

    def __setCurrent(self, value):
        pass

    isCurrent = property(__isCurrent, __setCurrent)

    def getState(self):
        if self.lock == LOCK_REASON.ON_ARENA:
            return 'battle'
        if self.lock in (LOCK_REASON.PREBATTLE, LOCK_REASON.UNIT, LOCK_REASON.UNIT_CLUB):
            return 'inPrebattle'
        if self.lock:
            return 'locked'
        if self.isDisabledInRoaming:
            return 'serverRestriction'
        ms = self.modelState
        if ms == 'undamaged':
            if self.repairCost > 0:
                return 'damaged'
            if not self.isCrewFull():
                return 'crewNotFull'
            if not self.isAmmoFull():
                return 'ammoNotFull'
        return ms

    def getStateLevel(self):
        state = self.getState()
        if state in ('crewNotFull', 'damaged', 'exploded', 'destroyed', 'serverRestriction'):
            return InventoryVehicle.STATE_LEVEL.CRITICAL
        if state in ('undamaged',):
            return InventoryVehicle.STATE_LEVEL.INFO
        return InventoryVehicle.STATE_LEVEL.WARNING

    @async
    def loadShells(self, shells, callback):

        def loadShellsResponse(responseCode):
            response = (False, '#system_messages:charge/server_error')
            if responseCode < 0:
                LOG_ERROR('Server return error for inventory equipShells request: responseCode=%s.' % responseCode)
            else:
                response = (True, '#system_messages:charge/success')
            if callback:
                callback(response)

        if not hasattr(BigWorld.player(), 'inventory'):
            raise AssertionError('Load shells is not possible')
            if shells is None:
                shells = list()
                for cDescr, (count, boughtForCredits) in self.__getDefaultsForCurrentConfiguration():
                    shells.extend([cDescr if not boughtForCredits else -cDescr, count])

            defaults = listToDict(getDefaultAmmoForGun(self.descriptor.gun))
            defaultsCount = 0
            for _, count in defaults.iteritems():
                defaultsCount += count

            shellsCount = 0
            for _, count in listToDict(shells).iteritems():
                shellsCount += count

            shellsCount > defaultsCount and callback((False, '#system_messages:charge/server_error'))
        BigWorld.player().inventory.setAndFillLayouts(self.inventoryId, shells, None, lambda code, errStr, buyingList: loadShellsResponse(code))
        return

    @async
    def repair(self, callback):

        def checkCredit(code, value):

            def repairResponse(code):
                if code >= 0:
                    if callback is not None:
                        message = makeString('#system_messages:repair/success', self.name, formatPrice((repairCost, 0)))
                        callback((True, message))
                else:
                    LOG_ERROR('Server response en error for repair vehicle(%s - %s) operation code: %s' % (self.name, self.inventoryId, code))
                    if callback is not None:
                        callback((False, makeString('#system_messages:repair/server_error', self.name)))
                return

            if value >= self.repairCost:
                repairCost = self.repairCost
                BigWorld.player().inventory.repair(self.inventoryId, repairResponse)
            elif callback is not None:
                callback((False, makeString('#system_messages:repair/credit_error', int(self.repairCost - value), self.name)))
            return

        BigWorld.player().stats.get('credits', checkCredit)

    @async
    @process
    def isElite(self, callback):
        from gui.shared.utils.requesters import DeprecatedStatsRequester
        eliteVehicles = yield DeprecatedStatsRequester().getEliteVehicles()
        callback(self.isGroupElite(eliteVehicles))

    def isGroupElite(self, eliteVehicles):
        return len(self.descriptor.type.unlocksDescrs) == 0 or self.descriptor.type.compactDescr in eliteVehicles

    @property
    def isXPToTman(self):
        from AccountCommands import VEHICLE_SETTINGS_FLAG
        return bool(self.__settings & VEHICLE_SETTINGS_FLAG.XP_TO_TMAN)

    @async
    def setXPToTmen(self, isOn, callback):

        def response(responseCode):
            if responseCode < 0:
                LOG_ERROR('Server return error for setXPToTmen request: responseCode=%s.' % responseCode)
            if callback:
                callback(responseCode >= 0)

        from AccountCommands import VEHICLE_SETTINGS_FLAG
        BigWorld.player().inventory.changeVehicleSetting(self.inventoryId, VEHICLE_SETTINGS_FLAG.XP_TO_TMAN, bool(isOn), response)

    @property
    def isAutoRepair(self):
        from AccountCommands import VEHICLE_SETTINGS_FLAG
        return bool(self.__settings & VEHICLE_SETTINGS_FLAG.AUTO_REPAIR)

    @async
    def setAutoRepair(self, isOn, callback):

        def response(responseCode):
            if responseCode < 0:
                LOG_ERROR('Server return error for setAutoRepair request: responseCode=%s.' % responseCode)
            if callback:
                callback(responseCode >= 0)

        from AccountCommands import VEHICLE_SETTINGS_FLAG
        BigWorld.player().inventory.changeVehicleSetting(self.inventoryId, VEHICLE_SETTINGS_FLAG.AUTO_REPAIR, bool(isOn), response)

    @property
    def isAutoLoad(self):
        from AccountCommands import VEHICLE_SETTINGS_FLAG
        return bool(self.__settings & VEHICLE_SETTINGS_FLAG.AUTO_LOAD)

    @async
    def setAutoLoad(self, isOn, callback):

        def response(responseCode):
            if responseCode < 0:
                LOG_ERROR('Server return error for setAutoLoad request: responseCode=%s.' % responseCode)
            if callback:
                callback(responseCode >= 0)

        from AccountCommands import VEHICLE_SETTINGS_FLAG
        BigWorld.player().inventory.changeVehicleSetting(self.inventoryId, VEHICLE_SETTINGS_FLAG.AUTO_LOAD, bool(isOn), response)

    @property
    def isAutoEquip(self):
        from AccountCommands import VEHICLE_SETTINGS_FLAG
        return bool(self.__settings & VEHICLE_SETTINGS_FLAG.AUTO_EQUIP)

    @async
    def setAutoEquip(self, isOn, callback):

        def response(responseCode):
            if responseCode < 0:
                LOG_ERROR('Server return error for AUTO_EQUIP request: responseCode=%s.' % responseCode)
            if callback:
                callback(responseCode >= 0)

        from AccountCommands import VEHICLE_SETTINGS_FLAG
        BigWorld.player().inventory.changeVehicleSetting(self.inventoryId, VEHICLE_SETTINGS_FLAG.AUTO_EQUIP, bool(isOn), response)

    @property
    def isFavorite(self):
        from AccountCommands import VEHICLE_SETTINGS_FLAG
        return bool(self.__settings & VEHICLE_SETTINGS_FLAG.GROUP_0)

    @async
    def setFavorite(self, isOn, callback):

        def response(responseCode):
            if responseCode < 0:
                LOG_ERROR('Server return error for GROUP_0 request: responseCode=%s.' % responseCode)
            if callback:
                callback(responseCode >= 0)

        from AccountCommands import VEHICLE_SETTINGS_FLAG
        BigWorld.player().inventory.changeVehicleSetting(self.inventoryId, VEHICLE_SETTINGS_FLAG.GROUP_0, bool(isOn), response)

    def isLocked(self):
        return self.lock != LOCK_REASON.NONE

    def isBroken(self):
        return self.repairCost > 0

    def isAlive(self):
        return not self.isBroken() and not self.isLocked()

    def __repr__(self):
        return 'InventoryVehicle<id:%d, repairCost:%f, lock:%d>' % (self.inventoryId, self.repairCost, self.lock)

    def pack(self):
        return pickle.dumps([InventoryVehicle, (self.compactDescr, self.inventoryId, self.crew)])

    def __eq__(self, other):
        if other is not None and isinstance(other, InventoryVehicle):
            return self.inventoryId == other.inventoryId
        else:
            return False


class InventoryTankman(InventoryItem):

    def __init__(self, compactDescr, id, vehicleID = -1):
        InventoryItem.__init__(self, ITEM_TYPE_NAMES[8], compactDescr=compactDescr, id=id, count=1)
        self.__nationConfig = getNationConfig(self.descriptor.nationID)
        skillsConfig = getSkillsConfig()
        self.__vehicleID = vehicleID

    @property
    def nation(self):
        return self.descriptor.nationID

    @property
    def nationConfig(self):
        return getNationConfig(self.nation)

    @property
    def skills(self):
        return self.descriptor.skills

    @property
    def vehicle(self):
        return VehicleDescr(typeID=(self.descriptor.nationID, self.descriptor.vehicleTypeID))

    @property
    @async
    @process
    def currentVehicle(self, callback):
        from gui.shared.utils.requesters import Requester
        vcls = yield Requester('vehicle').getFromInventory()
        if self.isInTank:
            for vcl in vcls:
                if vcl.inventoryId == self.vehicleID:
                    callback(vcl)
                    return

        callback(None)
        return

    @property
    def vehicleIconContour(self):
        return '../maps/icons/vehicle/contour/%s.png' % self.vehicle.type.name.replace(':', '-')

    @property
    def vehicleType(self):
        for tag in vehicles.VEHICLE_CLASS_TAGS.intersection(self.vehicle.type.tags):
            return tag

    def efficiencyRoleLevel(self, vehicleDescr):
        factor, addition = self.descriptor.efficiencyOnVehicle(vehicleDescr) if self.isInTank else (1, 0)
        return round(self.roleLevel * factor + addition)

    @property
    def lastSkillLevel(self):
        return self.descriptor.lastSkillLevel

    @property
    def roleLevel(self):
        return self.descriptor.roleLevel

    @property
    def icon(self):
        return self.__nationConfig['icons'][self.descriptor.iconID]

    @property
    def iconRank(self):
        return self.__nationConfig['ranks'][self.descriptor.rankID]['icon']

    @property
    def iconRole(self):
        return getSkillsConfig()[self.descriptor.role]['icon']

    @property
    def firstname(self):
        return convert(self.__nationConfig['firstNames'][self.descriptor.firstNameID])

    @property
    def lastname(self):
        return convert(self.__nationConfig['lastNames'][self.descriptor.lastNameID])

    @property
    def rank(self):
        return convert(self.__nationConfig['ranks'][self.descriptor.rankID]['userString'])

    @property
    def role(self):
        return convert(getSkillsConfig()[self.descriptor.role]['userString'])

    @property
    def vehicleID(self):
        return self.__vehicleID

    @property
    def isInTank(self):
        return self.__vehicleID != -1

    @property
    def newSkillCount(self):
        hasNewSkill = self.roleLevel == 100 and (self.lastSkillLevel == 100 or not len(self.skills))
        if hasNewSkill:
            tmanDescr = TankmanDescr(self.compactDescr)
            i = 0
            skills_list = list(ACTIVE_SKILLS)
            while tmanDescr.roleLevel == 100 and (tmanDescr.lastSkillLevel == 100 or len(tmanDescr.skills) == 0) and len(skills_list) > 0:
                skillname = skills_list.pop()
                if skillname not in tmanDescr.skills:
                    tmanDescr.addSkill(skillname)
                    i += 1

            last_skill_level = tmanDescr.lastSkillLevel
            return (i, last_skill_level)
        return (0, 0)

    @async
    @process
    def __checkVehicleReady(self, operationType, callback):
        from gui.shared.utils.requesters import Requester
        vcls = yield Requester('vehicle').getFromInventory()
        if not self.isInTank:
            callback((True, '', None))
            return
        else:
            for vcl in vcls:
                if vcl.inventoryId == self.vehicleID:
                    vehicle = vcl
                    break
            else:
                message = '#system_messages:%s/wrong_vehicle' % operationType

            if vehicle is not None:
                if vehicle.repairCost > 0:
                    message = '#system_messages:%s/vehicle_need_repair' % operationType
                elif vehicle.lock:
                    message = '#system_messages:%s/vehicle_need_wait' % operationType
                else:
                    callback((True, '', vehicle))
                    return
            callback((False, message, vehicle))
            return

    @async
    @process
    def addSkill(self, skillName, callback):

        def addSkillResponse(code):
            if code >= 0:
                callback((True, '#system_messages:addTankmanSkill/success'))
            else:
                callback((False, '#system_messages:addTankmanSkill/server_error'))

        ready, message, vehicle = yield self.__checkVehicleReady('addTankmanSkill')
        if not (ready and skillName not in self.skills and hasattr(BigWorld.player(), 'inventory')):
            raise AssertionError('Request from inventory is not possible')
            BigWorld.player().inventory.addTankmanSkill(self.inventoryId, skillName, addSkillResponse)
            return
        else:
            if callback is not None:
                callback((False, message))
            return

    @async
    @process
    def dropSkills(self, dropSkillsCostIdx, callback):
        from gui.shared.utils.requesters import DeprecatedStatsRequester
        dropSkillsCost = yield DeprecatedStatsRequester().getDropSkillsCost()
        price = (dropSkillsCost[dropSkillsCostIdx]['credits'], dropSkillsCost[dropSkillsCostIdx]['gold'])
        message_type = getTankmanOpertnSysMessageType(dropSkillsCostIdx)

        def dropSkillsResponse(code):
            if code >= 0:
                callback((True, makeString('#system_messages:dropTankmanSkill/success') % formatPrice(price), message_type))
            else:
                callback((False, '#system_messages:dropTankmanSkill/server_error', SystemMessages.SM_TYPE.Error))

        ready, message, vehicle = yield self.__checkVehicleReady('dropTankmanSkill')
        if not (ready and hasattr(BigWorld.player(), 'inventory')):
            raise AssertionError('Request from inventory is not possible')
            BigWorld.player().inventory.dropTankmanSkills(self.inventoryId, dropSkillsCostIdx, dropSkillsResponse)
            return
        else:
            if callback is not None:
                callback((False, message, SystemMessages.SM_TYPE.Error))
            return

    @async
    @process
    def respec(self, vehTypeCompDescr, tmanCostTypeIdx, callback):
        from gui.shared.utils.requesters import DeprecatedStatsRequester
        upgradeParams = yield DeprecatedStatsRequester().getTankmanCost()

        def respecResponse(code):
            if code >= 0:
                callback((True, makeString('#system_messages:retrainingTankman/success') + formatTankmanPrice(upgradeParams, tmanCostTypeIdx)))
            else:
                callback((False, '#system_messages:retrainingTankman/server_error'))

        ready, message, _ = yield self.__checkVehicleReady('retrainingTankman')
        if not (ready and hasattr(BigWorld.player(), 'inventory')):
            raise AssertionError('Request from inventory is not possible')
            BigWorld.player().inventory.respecTankman(self.inventoryId, vehTypeCompDescr, tmanCostTypeIdx, respecResponse)
            return
        else:
            if callback is not None:
                callback((False, message))
            return

    @async
    @process
    def dismiss(self, callback):

        def dismissResponse(code):
            if code >= 0:
                callback((True, '#system_messages:dismissTankman/success'))
            else:
                callback((False, '#system_messages:dismissTankman/server_error'))

        ready, message, vehicle = yield self.__checkVehicleReady('dismissTankman')
        if not (ready and hasattr(BigWorld.player(), 'inventory')):
            raise AssertionError('Request from inventory is not possible')
            BigWorld.player().inventory.dismissTankman(self.inventoryId, dismissResponse)
            return
        else:
            if callback is not None:
                callback((False, message))
            return

    @async
    @process
    def unload(self, callback, unloadAll):
        from gui.shared.utils.requesters import DeprecatedStatsRequester, Requester
        messageCode = 'unloadCrew' if unloadAll else 'unloadTankman'

        def unloadResponse(code):
            if code >= 0:
                callback((True, '#system_messages:%s/success' % messageCode))
            else:
                callback((False, '#system_messages:%s/server_error' % messageCode))

        ready, message, vehicle = yield self.__checkVehicleReady(messageCode)
        ready = True
        if ready:
            tankmanInBarracks = 0
            berthsCount = yield DeprecatedStatsRequester().getTankmenBerthsCount()
            tankmen = yield Requester('tankman').getFromInventory()
            for tankman in tankmen:
                if not tankman.isInTank:
                    tankmanInBarracks += 1

            unloadCount = 1
            if unloadAll:
                unloadCount = 0
                for tID in vehicle.crew:
                    if tID is not None:
                        unloadCount += 1

            if berthsCount - tankmanInBarracks < unloadCount:
                message = '#system_messages:%s/not_enought_space' % messageCode
            else:
                if unloadAll:
                    slot = -1
                else:
                    slot = 0
                    for tmanId in vehicle.crew:
                        if tmanId == self.inventoryId:
                            break
                        slot += 1

                if slot is not None and vehicle.lock == LOCK_REASON.NONE and slot < len(vehicle.crew):
                    if not hasattr(BigWorld.player(), 'inventory'):
                        raise AssertionError('Request from inventory is not possible')
                        BigWorld.player().inventory.equipTankman(vehicle.inventoryId, slot, None, unloadResponse)
                        return
                callback is not None and callback((False, message))
        return

    @async
    @process
    def equip(self, vehicleID, slot, callback):
        from gui.shared.utils.requesters import Requester
        ready, message, vehicle = yield self.__checkVehicleReady('equipTankman')
        if ready:
            vcls = yield Requester('vehicle').getFromInventory()
            for vcl in vcls:
                if vcl.inventoryId == vehicleID:
                    dest_vehicle = vcl
                    break
            else:
                message = '#system_messages:%s/wrong_vehicle' % 'equipTankman'

            if dest_vehicle is not None:
                if dest_vehicle.repairCost > 0:
                    message = '#system_messages:%s/vehicle_need_repair' % 'equipTankman'
                elif dest_vehicle.lock:
                    message = '#system_messages:%s/vehicle_need_wait' % 'equipTankman'
                else:

                    def equipResponse(code):
                        messageCode = 'equipTankman' if dest_vehicle.crew[int(slot)] is None else 'reequipTankman'
                        if code >= 0:
                            callback((True, '#system_messages:%s/success' % messageCode))
                        else:
                            callback((False, '#system_messages:%s/server_error' % messageCode))
                        return

                    if not hasattr(BigWorld.player(), 'inventory'):
                        raise AssertionError('Request from inventory is not possible')
                        BigWorld.player().inventory.equipTankman(int(vehicleID), int(slot), self.inventoryId, equipResponse)
                        return
            callback is not None and callback((False, message))
        return

    @async
    @process
    def replacePassport(self, firstNameID, lastNameID, iconID, isFemale, callback):
        from gui.shared.utils.requesters import DeprecatedStatsRequester
        from gui.shared import g_itemsCache
        passportCost = yield DeprecatedStatsRequester().getPassportChangeCost()
        gold = g_itemsCache.items.stats.gold

        def replacePassportResponse(code):
            if code >= 0:
                callback((True, makeString('#system_messages:replaceTankman/success') % formatPrice((0, passportCost))))
            else:
                callback((False, '#system_messages:replaceTankman/server_error'))

        ready, message, vehicle = yield self.__checkVehicleReady('replaceTankman')
        if ready:
            if gold < passportCost:
                message = '#sytem_messages:replaceTankman/not_enough_money'
            else:
                if not hasattr(BigWorld.player(), 'inventory'):
                    raise AssertionError('Request from inventory is not possible')
                    BigWorld.player().inventory.replacePassport(self.inventoryId, False, isFemale, 0, firstNameID, 0, lastNameID, 0, iconID, replacePassportResponse)
                    return
                callback is not None and callback((False, message))
        return

    def __repr__(self):
        return 'InventoryTankman<id:%d, vehicleID:%d>' % (self.inventoryId, self.vehicleID)

    def pack(self):
        return pickle.dumps([InventoryTankman, (self.compactDescr, self.inventoryId, self.vehicleID)])

    def __eq__(self, other):
        if other is not None and isinstance(other, InventoryTankman):
            return self.inventoryId == other.inventoryId
        else:
            return False

    def __response(self, responseCode):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat request: responseCode=%s.' % responseCode)
        if self.__callback:
            self.__callback(responseCode >= 0, self.__message)


class VehicleItem(FittingItem):

    def __init__(self, descriptor = None, compactDescr = None, count = 0):
        if not (descriptor is not None or compactDescr is not None):
            raise AssertionError('descriptor or compactDescr should be provided for VehicleItem')
            self.count = count
            self.descriptor = descriptor
            self.vehicles = []
            self.descriptor = descriptor is None and getDictDescr(compactDescr)
        elif compactDescr is None:
            compactDescr = descriptor['compactDescr']
        FittingItem.__init__(self, compactDescr, self.descriptor['itemTypeName'])
        return

    @property
    def nation(self):
        """
        Nation index from nations.INDICES
        """
        return self.descriptor['id'][0]

    @async
    def getPrice(self, callback):

        def __valueResponse(responseCode, value, revision = 0):
            if responseCode < 0:
                LOG_ERROR('Server return error for shop getSellPrice request: responseCode=%s' % responseCode)
            if callback:
                callback((value, 0))

        raise hasattr(BigWorld.player(), 'shop') or AssertionError('Request from shop is not possible')
        BigWorld.player().shop.getComponentSellPrice(self.compactDescr, __valueResponse)

    def pack(self):
        return pickle.dumps([VehicleItem, (None, self.compactDescr, self.count)])


class Vehicle(FittingItem):

    def __init__(self, compactDescr):
        raise compactDescr is not None or AssertionError('compactDescr should be provided for Vehicle')
        self.descriptor = VehicleDescr(compactDescr=compactDescr)
        FittingItem.__init__(self, compactDescr, 'vehicle')
        return


class VehicleShellSlot(VehicleItem):

    def __init__(self, descriptor = None, compactDescr = None, count = 0, default = 0, piercingPower = (0, 0), damage = (0, 0), boughtForCredits = False):
        VehicleItem.__init__(self, descriptor, compactDescr, count)
        self.default = default
        self.piercingPower = piercingPower
        self.damage = damage
        self.boughtForCredits = boughtForCredits

    @property
    def nation(self):
        return self.descriptor['id'][0]

    def getTableName(self):
        if not GUI_SETTINGS.technicalInfo:
            return ''
        description = makeString('#menu:descriptions/shellFull')
        pPower = (BigWorld.wg_getIntegralFormat(round(self.piercingPower[0] - self.piercingPower[0] * self.descriptor['piercingPowerRandomization'])), BigWorld.wg_getIntegralFormat(round(self.piercingPower[0] + self.piercingPower[0] * self.descriptor['piercingPowerRandomization'])))
        damage = (BigWorld.wg_getIntegralFormat(round(self.damage[0] - self.damage[0] * self.descriptor['damageRandomization'])), BigWorld.wg_getIntegralFormat(round(self.damage[0] + self.damage[0] * self.descriptor['damageRandomization'])))
        description %= {'piercingPower': '%s-%s' % pPower,
         'damage': '%s-%s' % damage}
        return description


def getVehicleTypeFullName(vehicleType):
    typeInfo = getTypeInfoByName('vehicle')
    tagsDump = [ typeInfo['tags'][tag]['userString'] for tag in vehicleType.tags if typeInfo['tags'][tag]['userString'] != '' ]
    return '%s %s' % (' '.join(tagsDump), vehicleType.userString)


def getVehicleFullName(vd = None):
    from CurrentVehicle import g_currentVehicle
    if vd is None:
        vd = g_currentVehicle.item.descriptor
    return getVehicleTypeFullName(vd.type)


def findVehicleArmorMinMax(vd):

    def findComponentArmorMinMax(armor, minMax):
        for value in armor:
            if value != 0:
                if minMax is None:
                    minMax = [value, value]
                else:
                    minMax[0] = min(minMax[0], value)
                    minMax[1] = max(minMax[1], value)

        return minMax

    minMax = None
    minMax = findComponentArmorMinMax(vd.hull['primaryArmor'], minMax)
    for turrets in vd.type.turrets:
        for turret in turrets:
            minMax = findComponentArmorMinMax(turret['primaryArmor'], minMax)

    return minMax


def compactItem(item):
    return item.pack()


def getItemByCompact(compact):
    if compact:
        return FittingItem.unpack(compact)
    else:
        return None


def listToDict(listVar):
    dictVar = {}
    listVar = list(listVar)
    while len(listVar) > 0:
        key = listVar.pop(0)
        dictVar[key] = listVar.pop(0) if len(listVar) else 0

    return dictVar


def formatPrice(price, reverse = False):
    outPrice = []
    credits, gold = price[:2]
    if credits != 0 or gold == 0:
        cname = makeString('#menu:price/credits') + ': '
        cformatted = BigWorld.wg_getIntegralFormat(credits)
        outPrice.extend([cformatted, ' ', cname] if reverse else [cname, ' ', cformatted])
        if gold != 0:
            outPrice.append(', ')
    if gold != 0:
        gname = makeString('#menu:price/gold') + ': '
        gformatted = BigWorld.wg_getGoldFormat(gold)
        outPrice.extend([gformatted, ' ', gname] if reverse else [gname, ' ', gformatted])
    return ''.join(outPrice)


def formatGoldPrice(gold, reverse = False):
    outPrice = []
    gname = makeString('#menu:price/gold') + ': '
    gformatted = BigWorld.wg_getGoldFormat(gold)
    outPrice.extend([gformatted, ' ', gname] if reverse else [gname, ' ', gformatted])
    return ''.join(outPrice)


def formatTankmanPrice(costType, roleLevelIdx):
    message = ' %s' % makeString('#menu:price/spent')
    if roleLevelIdx == 1:
        message = message % formatPrice((costType[1]['credits'], 0))
    elif roleLevelIdx == 2:
        message = message % formatPrice((0, costType[2]['gold']))
    else:
        return ''
    return message


def getPurchaseSysMessageType(price):
    credits, gold = price[:2]
    type = SystemMessages.SM_TYPE.Information
    if credits > 0 and gold == 0:
        type = SystemMessages.SM_TYPE.PurchaseForCredits
    elif gold > 0:
        type = SystemMessages.SM_TYPE.PurchaseForGold
    return type


def isVehicleElite(vehicle, eliteVehicles):
    return len(vehicle.descriptor.type.unlocksDescrs) == 0 or vehicle.descriptor.type.compactDescr in eliteVehicles


def getVehicleEliteState(vehicle, eliteVehicles, unlocks):
    if not isVehicleElite(vehicle, eliteVehicles):
        return VEHICLE_ELITE_STATE.NOT_ELITE
    for data in vehicle.descriptor.type.unlocksDescrs:
        if data[1] not in unlocks:
            return VEHICLE_ELITE_STATE.NOT_FULLY_ELITE

    return VEHICLE_ELITE_STATE.FULLY_ELITE


def isVehicleObserver(vehTypeCompDescr):
    item_type_id, nation_id, item_id_within_nation = vehicles.parseIntCompactDescr(vehTypeCompDescr)
    return 'observer' in vehicles.g_cache.vehicle(nation_id, item_id_within_nation).tags
