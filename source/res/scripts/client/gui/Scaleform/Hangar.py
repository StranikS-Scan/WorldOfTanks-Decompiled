# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Hangar.py
# Compiled at: 2019-03-27 02:05:59
from AccountCommands import LOCK_REASON
import account_helpers
from account_helpers.AccountPrebattle import AccountPrebattle
from account_helpers.AccountSettings import AccountSettings, CAROUSEL_FILTER
import BigWorld
import MusicController
from adisp import process
from CurrentVehicle import g_currentVehicle
from constants import WOT_CLASSIC_LOCK_MODE
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION
from items.tankmen import getSkillsConfig, COMMANDER_ADDITION_RATIO, SKILL_NAMES, SKILLS_BY_ROLES, PERKS, MAX_SKILL_LEVEL
from items import ITEM_TYPE_NAMES, ITEM_TYPE_INDICES
from helpers.i18n import convert, makeString
from gui import SystemMessages, AOGAS
from gui.Scaleform.graphs.ResearchInterface import ResearchInterface
from gui.Scaleform.utils.requesters import Requester, AvailableItemsRequester, StatsRequester
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.utils import gui_items
from gui.Scaleform.utils.parameters import getCurrentVehicleParams
from gui.Scaleform.utils.gui_items import formatPrice, getItemByCompact, VehicleItem
from gui.Scaleform.utils.functions import makeTooltip, isModuleFitVehicle, findConflictedEquipmentForModule, async_showConfirmDialog
from gui.Scaleform.utils.HangarSpace import g_hangarSpace
from PlayerEvents import g_playerEvents
from gui.Scaleform.TankmenInterface import TankmenInterface
import FMOD, SoundGroups
from gui.Scaleform import VoiceChatInterface, ColorSchemeManager
INVENTORY_ITEM_TANKMEN_IDX = 3

class Hangar(UIInterface):

    def __init__(self):
        self.__inited = 0
        UIInterface.__init__(self)
        self.tankmenInterface = TankmenInterface(self)
        self.researchInterface = ResearchInterface()
        self.__fitting = Fitting()
        self.vehiclesFilter = dict(AccountSettings.getFilter(CAROUSEL_FILTER))

    def __del__(self):
        LOG_DEBUG('HangarHandler deleted')

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.tankmenInterface.populateUI(proxy)
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        self.researchInterface.populateUI(proxy)
        self.__fitting.populateUI(proxy)
        self.uiHolder.movie.backgroundAlpha = 0.0
        self.uiHolder.movie.wg_inputKeyMode = 1
        self.uiHolder.addExternalCallbacks({'hangar.vehicleChange': self.onVehicleSelectChange,
         'hangar.ammoRequest': self.onAmmoRequest,
         'hangar.ammoInstallRequest': self.onAmmoInstall,
         'hangar.ammoAutoInstallRequest': self.onAmmoInstall,
         'hangar.repair': self.onRepair,
         'hangar.checkMoney': self.onCheckMoney,
         'hangar.buySlot': self.onBuySlot,
         'hangar.setVehiclesFilter': self.onSetVehiclesFilter,
         'hangar.sellVehicle': self.onSellVehicle,
         'hangar.getVehicleSellParams': self.onGetSellVehicleParams,
         'hangar.favoriteVehicle': self.onFavoriteVehicle,
         'hangar.getUnlockVehicles': self.onGetUnlockVehicles,
         'hangar.buyTankClick': self.onBuyTank})
        self.colorManager = ColorSchemeManager._ColorSchemeManager()
        self.colorManager.populateUI(proxy)
        VoiceChatInterface.g_instance.onVoiceChatInitFailed += self.onVoiceChatInitFailed
        VoiceChatInterface.g_instance.onVoiceChatInitSucceded += self.onVoiceChatInitSucceded
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        g_playerEvents.onClientUpdated += self.update
        g_playerEvents.onShopResync += self.update
        g_playerEvents.onPrebattleLeft += self.__onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle += self.__onKickedFromPrebattle
        g_currentVehicle.update()
        self.call('hangar.setCarouselFilter', [self.vehiclesFilter['nation'], self.vehiclesFilter['tankType'], self.vehiclesFilter['ready']])
        MusicController.g_musicController.stopMusic()
        MusicController.g_musicController.stopAmbient()
        BigWorld.player().stats.get('attrs', self.__startSoundEventsCallback)
        AOGAS.g_controller.enableNotifyAccount()
        if not self.uiHolder.commandsBinded:
            self.uiHolder.bindCommands()
        Waiting.hide('loadPage')

    def onVoiceChatInitFailed(self):
        self.call('VoiceChat.initFailed', [])

    def onVoiceChatInitSucceded(self):
        self.call('VoiceChat.initSucceded', [])

    def __startSoundEventsCallback(self, resultId, attrs):
        isPremium = account_helpers.isPremiumAccount(attrs)
        MusicController.g_musicController.setAccountAttrs(attrs)
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)
        self.__premiumHangarSndFan = None
        if isPremium:
            self.__premiumHangarSndFan = FMOD.getSound('/ambient/hangar/hangar_prem_fen')
        if self.__premiumHangarSndFan is not None:
            self.__premiumHangarSndFan.position = (50, 2, 64)
            self.__premiumHangarSndFan.play()
        SoundGroups.g_instance.enableLobbySounds(True)
        return

    def dispossessUI(self):
        self.researchInterface.dispossessUI()
        if self.colorManager:
            self.colorManager.dispossessUI()
        if self.__premiumHangarSndFan is not None:
            self.__premiumHangarSndFan.stop()
            self.__premiumHangarSndFan = None
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        self.__fitting.dispossessUI()
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        g_playerEvents.onClientUpdated -= self.update
        g_playerEvents.onShopResync -= self.update
        g_playerEvents.onPrebattleLeft -= self.__onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle -= self.__onKickedFromPrebattle
        VoiceChatInterface.g_instance.onVoiceChatInitSucceded -= self.onVoiceChatInitSucceded
        VoiceChatInterface.g_instance.onVoiceChatInitFailed -= self.onVoiceChatInitFailed
        self.uiHolder.removeExternalCallbacks('hangar.getUnlockVehicles', 'hangar.vehicleChange', 'hangar.ammoRequest', 'hangar.ammoInstallRequest', 'hangar.ammoAutoInstallRequest', 'hangar.repair', 'hangar.checkMoney', 'hangar.buySlot', 'hangar.setVehiclesFilter', 'hangar.sellVehicle', 'hangar.getVehicleSellParams', 'hangar.favoriteVehicle', 'hangar.buyTankClick')
        self.tankmenInterface.dispossessUI()
        UIInterface.dispossessUI(self)
        return

    def __onVehicleBecomeElite(self, vehTypeCompDescr):
        self.__updateVehicles()

    def __onPrebattleLeft(self):
        self.__onCurrentVehicleChanged()

    def __onKickedFromPrebattle(self, prebattleID):
        self.__onCurrentVehicleChanged()

    @process
    def onGetUnlockVehicles(self, callbackId):
        shopVehicles = yield Requester('vehicle').getFromShop()
        iventoryVehicles = yield Requester('vehicle').getFromInventory()
        unlocks = yield StatsRequester().getUnlocks()
        credits = yield StatsRequester().getCredits()
        gold = yield StatsRequester().getGold()
        shopVehicles.sort()
        value = [callbackId]
        for shpVcl in shopVehicles:
            if shpVcl.descriptor.type.compactDescr in unlocks and shpVcl not in iventoryVehicles:
                if not shpVcl.hidden:
                    price = yield shpVcl.getPrice()
                    credits >= price[0] and gold >= price[1] and value.append(shpVcl.pack())
                    value.append(shpVcl.name)
                    value.append(shpVcl.descriptor.type.name.replace(':', '-'))
                    elite = price[0] == 0 and price[1] != 0
                    value.append(price[1] if elite else price[0])
                    value.append(elite)

        self.respond(value)

    @process
    def onSellVehicle(self, callbackId, id, isUnload, isDismantling):
        Waiting.show('sellItem')
        item = getItemByCompact(id)
        vcls = yield Requester('vehicle').getFromInventory()
        vehicle = None
        for vcl in vcls:
            if vcl.inventoryId == item.inventoryId:
                vehicle = vcl

        vclSellsLeft = yield StatsRequester().getVehicleSellsLeft()
        if vclSellsLeft == 0:
            SystemMessages.pushI18nMessage(makeString('#system_messages:fitting/vehicle_sell_limit', vehicle.name), type=SystemMessages.SM_TYPE.Error)
            Waiting.hide('sellItem')
            return
        else:
            berths = yield StatsRequester().getTankmenBerthsCount()
            tankmenInBarrack = 0
            tankmen = yield Requester('tankman').getFromInventory()
            for t in tankmen:
                if not t.isInTank:
                    tankmenInBarrack += 1

            currentCrew = [ t for t in vehicle.crew if t is not None ]
            if berths - tankmenInBarrack < len(currentCrew) and isUnload:
                SystemMessages.pushI18nMessage(makeString('#system_messages:fitting/vehicle_sell_barracks_full', vehicle.name), type=SystemMessages.SM_TYPE.Error)
                Waiting.hide('sellItem')
                return
            success = yield vehicle.sell(not isUnload, isDismantling)
            SystemMessages.pushI18nMessage(success[1], type=SystemMessages.SM_TYPE.Selling if success[0] else SystemMessages.SM_TYPE.Error)
            self.call('inventory.sellComplete', list(success))
            Waiting.hide('sellItem')
            return

    @process
    def onGetSellVehicleParams(self, callbackID, compact):
        item = getItemByCompact(compact)
        vcls = yield Requester('vehicle').getFromInventory()
        vehicle = None
        for vcl in vcls:
            if vcl.inventoryId == item.inventoryId:
                vehicle = vcl

        isUnique = yield vehicle.isUnique()
        sellParams = yield vehicle.sellParams()
        args = [isUnique]
        args.extend(sellParams)
        self.call('hangar.sellVehicle', args)
        return

    def onFavoriteVehicle(self, callbackId, compact, isFavorite):
        item = getItemByCompact(compact)
        item.favorite = isFavorite
        self.update()

    def update(self, diff=None):
        if diff is None or diff.get('inventory', {}).get(ITEM_TYPE_INDICES['vehicle'], {}).get('compDescr', {}).has_key(g_currentVehicle.vehicle.inventoryId) or diff.get('inventory', {}).get(ITEM_TYPE_INDICES['vehicle'], {}).get('repair', {}).has_key(g_currentVehicle.vehicle.inventoryId) or diff.get('inventory', {}).get(ITEM_TYPE_INDICES['vehicle'], {}).get('shells', {}).has_key(g_currentVehicle.vehicle.inventoryId) or diff.get('inventory', {}).get(ITEM_TYPE_INDICES['vehicle'], {}).get('shellsLayout', {}).has_key(g_currentVehicle.vehicle.inventoryId) or diff.get('inventory', {}).get(ITEM_TYPE_INDICES['vehicle'], {}).get('eqs', {}).has_key(g_currentVehicle.vehicle.inventoryId) or diff.get('inventory', {}).get(ITEM_TYPE_INDICES['vehicle'], {}).get('eqsLayout', {}).has_key(g_currentVehicle.vehicle.inventoryId) or 'vehTypeLocks' in diff.get('stats', {}):
            g_currentVehicle.update()
        else:
            stats = diff.get('stats', {})
            if diff.get('inventory', {}).get(ITEM_TYPE_INDICES['vehicle'], False):
                self.__updateVehicles()
            elif diff.get('inventory', False) or 'credits' in stats or 'gold' in stats or 'unlocks' in stats:
                self.__fitting.update()
            if stats.has_key('vehicleSellsLeft'):
                self.__fitting.update()
        if diff is not None:
            if diff.get('inventory', {}).get(ITEM_TYPE_INDICES['tankman'], False):
                self.__updateTankmen()
                self.call('PersonalcCaseManager.update', [])
        return

    def __onCurrentVehicleChanged(self):
        Waiting.show('updateVehicle')
        self.__updateVehicleHasTurret()
        self.__updateState()
        self.__updateVehicles()
        self.__updateParams()
        self.__updateAmmo()
        self.__updateTankmen()
        self.__fitting.update()
        self.call('PersonalcCaseManager.update', [])
        Waiting.hide('updateVehicle')

    def __updateParams(self):
        self.call('hangar.setVehicleParameters', getCurrentVehicleParams())

    def __updateVehicleHasTurret(self):
        if g_currentVehicle.isPresent():
            self.call('hangar.isVehicleHasTurret', [g_currentVehicle.vehicle.hasTurrets])

    def onSetVehiclesFilter(self, callbackID, nation, tankType, ready):
        self.vehiclesFilter['nation'] = nation
        self.vehiclesFilter['tankType'] = tankType
        self.vehiclesFilter['ready'] = ready
        AccountSettings.setFilter(CAROUSEL_FILTER, self.vehiclesFilter)
        self.__updateVehicles(True)

    def __onBattleResultsReceived(self, isActiveVehicle=None, id=None, results=None):
        if id == g_currentVehicle.vehicle.inventoryId:
            g_currentVehicle.update()
        else:
            self.__updateVehicles()
            self.__fitting.update()
        self.researchInterface.updateExperience()

    def __updateLock(self, id, lock):
        if g_currentVehicle.vehicle:
            id == g_currentVehicle.vehicle.inventoryId or self.__updateVehicles()

    @process
    def __updateState(self):
        vehicleTypeLocks = yield StatsRequester().getVehicleTypeLocks()
        clanLock = vehicleTypeLocks.get(g_currentVehicle.vehicle.descriptor.type.compactDescr, {}).get(WOT_CLASSIC_LOCK_MODE, None) if g_currentVehicle.isPresent() else None
        value = []
        if g_currentVehicle.isPresent():
            value.append(gui_items.getVehicleFullName())
            value.append(g_currentVehicle.repairCost)
            value.append(g_currentVehicle.vehicle.descriptor.getMaxRepairCost())
            value.append(g_currentVehicle.vehicle.health)
            value.append(g_currentVehicle.vehicle.descriptor.maxHealth)
        else:
            value.append('')
            value.append(0)
            value.append(0)
            value.append(0)
            value.append(0)
        self.call('hangar.setRepair', value)
        if clanLock is None:
            lock = ''
        else:
            lock = makeString('#menu:currentVehicleStatus/clanLocked') % (BigWorld.wg_getShortTimeFormat(clanLock) + ' ' + BigWorld.wg_getShortDateFormat(clanLock))
        self.call('hangar.readyToFight', [g_currentVehicle.isReadyToFight(),
         g_currentVehicle.getHangarMessage(),
         lock,
         g_currentVehicle.isPresent(),
         AccountPrebattle.isMemberReady() and not AccountPrebattle.isTraining(),
         g_currentVehicle.isCrewFull(),
         g_currentVehicle.isInHangar()])
        return

    @process
    def __updateTankmen(self):
        Waiting.show('updateTankmen')
        tankmen = yield Requester('tankman').getFromInventory()
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.vehicle
            isVehiclePremium = vehicle.isPremium
            crew = []
            for tId in vehicle.crew:
                if tId is None:
                    crew.append(None)
                    continue
                for tankman in tankmen:
                    if tankman.inventoryId == tId:
                        crew.append(tankman)

            commander_bonus = 0.0
            data = [len(vehicle.crew)]
            for i in range(len(vehicle.crew)):
                data.append(vehicle.crew[i])
                data.append(vehicle.descriptor.type.crewRoles[i][0])
                if vehicle.crew[i] != None and vehicle.descriptor.type.crewRoles[i][0] == 'commander':
                    tman = None
                    for tankman in tankmen:
                        if tankman.inventoryId == vehicle.crew[i]:
                            tman = tankman

                    if tman is not None:
                        commander_bonus = round(tman.efficiencyRoleLevel(vehicle.descriptor) / COMMANDER_ADDITION_RATIO)
                data.append(convert(getSkillsConfig()[vehicle.descriptor.type.crewRoles[i][0]]['userString']))
                data.append(getSkillsConfig()[vehicle.descriptor.type.crewRoles[i][0]]['icon'])
                data.append(vehicle.descriptor.type.id[0])
                data.append(vehicle.descriptor.type.id[1])
                data.append(i)
                data.append(vehicle.shortName)
                data.append(vehicle.type)
                data.append(isVehiclePremium)
                data.append(len(vehicle.descriptor.type.crewRoles[i]))
                for role in vehicle.descriptor.type.crewRoles[i]:
                    data.append(role)

            for tankman in tankmen:
                if not tankman.isInTank or tankman.inventoryId in vehicle.crew:
                    bonus_role_level = commander_bonus if tankman.descriptor.role != 'commander' else 0.0
                    penalty_role_level = tankman.efficiencyRoleLevel(vehicle.descriptor) - tankman.roleLevel
                    common_role_level = tankman.efficiencyRoleLevel(vehicle.descriptor) + bonus_role_level
                    data.append(tankman.firstname)
                    data.append(tankman.lastname)
                    data.append(tankman.rank)
                    data.append(tankman.roleLevel)
                    data.append(tankman.role)
                    data.append(tankman.vehicle.type.shortUserString)
                    data.append(tankman.icon)
                    data.append(tankman.iconRank)
                    data.append(tankman.iconRole)
                    data.append(tankman.vehicleIconContour)
                    data.append(tankman.inventoryId)
                    data.append(tankman.nation)
                    data.append(tankman.vehicle.type.id[1])
                    data.append(tankman.isInTank)
                    data.append(tankman.descriptor.role)
                    data.append(tankman.vehicleType)
                    data.append(tankman.efficiencyRoleLevel(vehicle.descriptor))
                    data.append(bonus_role_level)
                    data.append(tankman.lastSkillLevel)
                    data.append(tankman.pack())
                    decrypt_role_level = tankman.roleLevel
                    if penalty_role_level:
                        if penalty_role_level > 0:
                            decrypt_role_level = '%d+' % decrypt_role_level
                        decrypt_role_level = '%s%d' % (decrypt_role_level, penalty_role_level)
                    if bonus_role_level:
                        decrypt_role_level = '%s+%d' % (decrypt_role_level, bonus_role_level)
                    skills_list = ''
                    for skill in tankman.skills:
                        skills_list = '%s\n%s: %d%%' % (skills_list, convert(getSkillsConfig()[skill]['userString']), 100 if tankman.skills.index(skill) + 1 != len(tankman.skills) else tankman.lastSkillLevel)

                    data.append(makeTooltip('%s %s %s' % (tankman.rank, tankman.firstname, tankman.lastname), '%s, %s %s, %d%% (%s)%s' % (tankman.role,
                     convert(makeString('#menu:tankmen/%s' % tankman.vehicleType)),
                     convert(tankman.vehicle.type.shortUserString),
                     common_role_level,
                     decrypt_role_level,
                     skills_list), convert(makeString('#tooltips:hangar/crew/note'))))
                    skills_count = 0
                    for skill in SKILL_NAMES:
                        if skill in SKILLS_BY_ROLES[tankman.descriptor.role]:
                            skills_count += 1

                    data.append(skills_count)
                    data.append(len(tankman.skills))
                    for skill in tankman.skills:
                        skillLevel = tankman.lastSkillLevel if tankman.skills.index(skill) == len(tankman.skills) - 1 else 100
                        data.append(skill)
                        data.append(getSkillsConfig()[skill]['userString'])
                        data.append(getSkillsConfig()[skill]['description'])
                        data.append(getSkillsConfig()[skill]['icon'])
                        data.append(skill not in PERKS or skillLevel == 100)

            self.call('hangar.setTankmenParameters', data)
        Waiting.hide('updateTankmen')
        return

    @process
    def onCheckMoney(self, callbackId):
        credits = yield StatsRequester().getGold()
        slots = yield StatsRequester().getSlotsCount()
        slotsPrices = yield StatsRequester().getSlotsPrices()
        slotPrice = BigWorld.player().shop.getNextSlotPrice(slots, slotsPrices)
        self.call('hangar.shoyBuySlotConfirmation', [credits, slotPrice])

    @process
    def onBuySlot(self, callbackId):
        Waiting.show('buySlot')
        message = '#system_messages:buy_slot/server_error'
        success = yield StatsRequester().buySlot()
        price = yield StatsRequester().getSlotsPrices()
        if success:
            message = makeString('#system_messages:buy_slot/success') % formatPrice((0, price[1][0]))
            self.__updateVehicles()
        SystemMessages.g_instance.pushI18nMessage(message, type=SystemMessages.SM_TYPE.PurchaseForGold if success else SystemMessages.SM_TYPE.Error)
        Waiting.hide('buySlot')

    def onBuyTank(self, callbackId):
        filter = list(AccountSettings.getFilter('shop_current'))
        filter[1] = 'vehicle'
        AccountSettings.setFilter('shop_current', tuple(filter))
        self.uiHolder.movie.invoke(('loadShop',))

    @process
    def __updateVehicles(self, resetPos=False):
        Waiting.show('updateMyVehicles')
        slots = yield StatsRequester().getSlotsCount()
        price = yield StatsRequester().getSlotsPrices()
        multipliedXPVehs = yield StatsRequester().getMultipliedXPVehicles()
        vehicleTypeLocks = yield StatsRequester().getVehicleTypeLocks()
        if not g_currentVehicle.isPresent():
            self.call('hangar.vehiclesResponse', [slots, ''])
            Waiting.hide('updateMyVehicles')
            return
        else:
            filteredVehiclesCount = 0
            value = [price[1][0], slots]
            vehicles = yield Requester('vehicle').getFromInventory()
            value.append(len(vehicles))
            value.append(gui_items.compactItem(g_currentVehicle.vehicle))

            def sorting(first, second):
                if first.favorite and not second.favorite:
                    return -1
                if not first.favorite and second.favorite:
                    return 1
                return first.__cmp__(second)

            vehicles.sort(sorting)
            eliteVehicles = yield StatsRequester().getEliteVehicles()
            for vehicle in vehicles:
                if self.vehiclesFilter['nation'] != -1 and vehicle.nation != self.vehiclesFilter['nation'] or self.vehiclesFilter['tankType'] != -1 and vehicle.type != self.vehiclesFilter['tankType'] or self.vehiclesFilter['ready'] == True and vehicle.favorite == False:
                    filteredVehiclesCount += 1
                    continue
                try:
                    v = []
                    v.append(gui_items.compactItem(vehicle))
                    v.append(vehicle.name)
                    v.append(vehicle.icon)
                    v.append(vehicle.nation)
                    v.append(vehicle.level)
                    v.append(vehicle.getState())
                    v.append(vehicle.descriptor.type.compactDescr in multipliedXPVehs)
                    vehState = vehicle.getState()
                    clanLock = vehicleTypeLocks.get(vehicle.descriptor.type.compactDescr, {}).get(WOT_CLASSIC_LOCK_MODE, None)
                    if vehState == 'undamaged' and clanLock:
                        stateMsg = makeString('#tooltips:tanks_carousel/vehicleStates/clanLocked', time=BigWorld.wg_getShortTimeFormat(clanLock), date=BigWorld.wg_getShortDateFormat(clanLock))
                    else:
                        stateMsg = makeString('#tooltips:tanks_carousel/vehicleStates/%s' % vehState)
                    tooltip = makeTooltip(vehicle.longName, stateMsg, makeString('#tooltips:tanks_carousel/current_vehicle/note' if vehicle.isCurrent else '#tooltips:tanks_carousel/vehicle/note'))
                    v.append(tooltip)
                    v.append(vehicle.descriptor.type.compactDescr)
                    v.append(vehicle.favorite)
                    v.append(clanLock is not None)
                    elite = vehicle.isGroupElite(eliteVehicles)
                    v.append(elite)
                except:
                    LOG_CURRENT_EXCEPTION()
                    continue

                value.extend(v)

            value[1] -= filteredVehiclesCount
            self.call('hangar.vehiclesResponse', value)
            if filteredVehiclesCount != 0 and resetPos == True:
                self.call('hangar.setCarouselPosition', [0])
            Waiting.hide('updateMyVehicles')
            return

    def onAmmoRequest(self, callbackId):
        self.__updateAmmo()

    @process
    def __updateAmmo(self):
        Waiting.show('updateAmmo')
        credits = yield StatsRequester().getCredits()
        ammo = ['',
         0,
         False,
         False,
         0,
         0,
         False,
         False]
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.vehicle
            gun = gui_items.VehicleItem(vehicle.descriptor.gun)
            default_ammo_count = 0
            default_ammo = gui_items.listToDict(vehicle.getShellsDefaultList())
            for compactDescr, count in default_ammo.iteritems():
                default_ammo_count += count

            ammo = [gun.longName,
             gun.descriptor['maxAmmo'],
             not g_currentVehicle.isLocked(),
             not g_currentVehicle.isBroken(),
             default_ammo_count,
             0,
             g_currentVehicle.isLocked()]
            iAmmo = yield Requester('shell').getFromInventory()
            sAmmo = yield Requester('shell').getFromShop()
            totalPrice = {'credits': 0,
             'gold': 0}
            for shell in vehicle.shells:
                shopShell = sAmmo[sAmmo.index(shell)] if shell in sAmmo else None
                if shopShell:
                    iCount = iAmmo[iAmmo.index(shell)].count if shell in iAmmo else 0
                    sPrice = (yield shopShell.getPrice()) if shell is not shopShell else (0, 0)
                    buyCount = max(shell.default - iCount - shell.count, 0)
                    ammo.append(gui_items.compactItem(shopShell))
                    ammo.append(shell.type)
                    ammo.append('../maps/icons/ammopanel/ammo/%s' % shell.descriptor['icon'][0])
                    ammo.append(shell.count)
                    ammo.append(shell.default)
                    ammo.append(iCount)
                    if sPrice[1] == 0:
                        totalPrice['credits'] += sPrice[0] * buyCount
                        ammo.append(sPrice[0])
                        ammo.append('credits')
                    else:
                        totalPrice['gold'] += sPrice[1] * buyCount
                        ammo.append(sPrice[1])
                        ammo.append('gold')
                    ammo.append(shell.longName)
                    ammo.append(shell.tableName)
                    ammo.append(makeTooltip(shell.toolTip, None, makeString('#tooltips:hangar/ammo_panel/shell/note')))

        self.call('hangar.ammoResponse', ammo)
        Waiting.hide('updateAmmo')
        return

    @process
    def onAmmoInstall(self, callbackId, *args):
        Waiting.show('updateAmmo')
        vehicle = args[0]
        if vehicle is None:
            vehicle = g_currentVehicle.vehicle
        credits = yield StatsRequester().getCredits()
        gold = yield StatsRequester().getGold()
        if vehicle is not None:
            buyAmmo = {}
            installAmmo = []
            completed = [False, 'error']
            shells = list(args[1:])
            isAutoRefill = len(shells) == 0
            if len(shells) > 0:
                while 1:
                    item = len(shells) > 0 and gui_items.getItemByCompact(shells.pop(0))
                    buyAmmo[item] = shells.pop(0)
                    installAmmo.append(item.compactDescr)
                    installAmmo.append(shells.pop(0))

            else:
                iAmmo = yield Requester('shell').getFromInventory()
                sAmmo = yield Requester('shell').getFromShop()
                for shell in vehicle.shells:
                    shopShell = sAmmo[sAmmo.index(shell)] if shell in sAmmo else shell
                    iCount = iAmmo[iAmmo.index(shell)].count if shell in iAmmo else 0
                    buyAmmo[shopShell] = shell.default - iCount - shell.count
                    installAmmo.append(shell.compactDescr)
                    installAmmo.append(shell.default)

            totalPrice = {'credits': 0,
             'gold': 0}
            totalCount = 0
            for item, count in buyAmmo.items():
                if count > 0:
                    totalCount += count
                    sPrice = yield item.getPrice()
                    if sPrice[0] > 0:
                        totalPrice['credits'] += sPrice[0] * count
                    else:
                        totalPrice['gold'] += sPrice[1] * count

            if (vehicle.lock != LOCK_REASON.NONE or vehicle.repairCost > 0) and isAutoRefill:
                Waiting.hide('updateAmmo')
                return
            if totalPrice['credits'] <= credits and totalPrice['gold'] <= gold:
                self.__ammoBuyInstall(vehicle, buyAmmo, installAmmo)
            elif totalPrice['credits'] > credits and totalPrice['gold'] > gold:
                SystemMessages.g_instance.pushI18nMessage('#system_messages:charge/credit_error', BigWorld.wg_getIntegralFormat(totalPrice['credits'] - credits), BigWorld.wg_getGoldFormat(totalPrice['gold'] - gold), type=SystemMessages.SM_TYPE.Error)
            elif totalPrice['credits'] > credits:
                SystemMessages.g_instance.pushI18nMessage('#system_messages:charge/credit_error_credits', BigWorld.wg_getIntegralFormat(totalPrice['credits'] - credits), type=SystemMessages.SM_TYPE.Error)
            else:
                SystemMessages.g_instance.pushI18nMessage('#system_messages:charge/credit_error_gold', BigWorld.wg_getGoldFormat(totalPrice['gold'] - gold), type=SystemMessages.SM_TYPE.Error)
        Waiting.hide('updateAmmo')
        return

    @process
    def __ammoBuyInstall(self, vehicle, buyAmmo, installAmmo):
        Waiting.show('updateAmmo')
        completed = [False, 'error']
        accountMoney = {'credits': 0,
         'gold': 0}
        accountMoney['credits'] = yield StatsRequester().getCredits()
        accountMoney['gold'] = yield StatsRequester().getGold()
        totalPrice = {'credits': 0,
         'gold': 0}
        totalBuyCount = 0
        installAmmoVehicle = vehicle
        for item, count in buyAmmo.items():
            if count > 0:
                totalBuyCount += count
                response = yield item.buy(count)
                success = response[0]
                message = response[1]
                if not success:
                    if totalPrice['credits'] > 0 or totalPrice['gold'] > 0 and accountMoney['credits'] >= totalPrice['credits'] and accountMoney['gold'] >= totalPrice['gold']:
                        SystemMessages.g_instance.pushI18nMessage('#system_messages:charge/money_spent', BigWorld.wg_getIntegralFormat(totalPrice['credits']), BigWorld.wg_getGoldFormat(totalPrice['gold']), type=SystemMessages.SM_TYPE.Error)
                    completed = [success, message]
                    break
                SystemMessages.g_instance.pushMessage(message, response[2] if success else SystemMessages.SM_TYPE.Error)
                sPrice = yield item.getPrice()
                if sPrice[0] > 0:
                    totalPrice['credits'] += sPrice[0] * count
                else:
                    totalPrice['gold'] += sPrice[1] * count
        else:
            if totalBuyCount > 0:
                price = (totalPrice['credits'], totalPrice['gold'])
                SystemMessages.g_instance.pushI18nMessage('#system_messages:charge/money_spent', gui_items.formatPrice(price), type=gui_items.getPurchaseSysMessageType(price))
            success, message = yield installAmmoVehicle.loadShells(installAmmo)
            if g_currentVehicle.vehicle.getShellsList() != installAmmo:
                SystemMessages.g_instance.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Information if success else SystemMessages.SM_TYPE.Error)
            if g_currentVehicle.vehicle.getShellsDefaultList() != installAmmo:
                SystemMessages.g_instance.pushI18nMessage(message + '_save', type=SystemMessages.SM_TYPE.Information if success else SystemMessages.SM_TYPE.Error)
            completed = [success, message]

        self.call('hangar.ammoInstallResponse', completed)
        Waiting.hide('updateAmmo')

    def onVehicleSelectChange(self, callbackId, vehicleId):
        vehicle = gui_items.getItemByCompact(vehicleId)
        if vehicle != g_currentVehicle.vehicle:
            g_currentVehicle.vehicle = vehicle

    def onRepair(self, callbackId, code=None):
        self.__repair()

    @process
    def __repair(self, vehicle=None):
        Waiting.show('updateMyVehicles')
        if vehicle is None:
            vehicle = g_currentVehicle.vehicle
        if vehicle.repairCost > 0:
            success, message = yield vehicle.repair()
            SystemMessages.g_instance.pushMessage(message, SystemMessages.SM_TYPE.Repair if success else SystemMessages.SM_TYPE.Error)
        self.uiHolder.call('common.ammunitionInstall', [])
        Waiting.hide('updateMyVehicles')
        return


class Fitting(UIInterface):
    __FITTING_SLOTS = (ITEM_TYPE_NAMES[2],
     ITEM_TYPE_NAMES[3],
     ITEM_TYPE_NAMES[4],
     ITEM_TYPE_NAMES[5],
     ITEM_TYPE_NAMES[7],
     ITEM_TYPE_NAMES[9],
     ITEM_TYPE_NAMES[11])
    __ARTEFACTS_SLOTS = (ITEM_TYPE_NAMES[9], ITEM_TYPE_NAMES[11])

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'hangar.FittingChange': self.onFittingChange})

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('hangar.FittingChange')
        UIInterface.dispossessUI(self)

    def update(self):
        if g_currentVehicle.isPresent():
            Waiting.show('updateFitting', isSingle=True)
            self.__requestsCount = len(Fitting.__FITTING_SLOTS)
            for type in Fitting.__FITTING_SLOTS:
                self.__requestAvailableItems(type)

    @process
    def __requestAvailableItems(self, type):

        def createToolTip(module, fits):
            tooltip_body = makeString(fits)
            if type == ITEM_TYPE_NAMES[9] and not module.descriptor['removable']:
                tooltip_body += ('\n' if len(tooltip_body) != 0 else '') + makeString('#tooltips:moduleFits/not_removable/body')
            return makeTooltip(module.toolTip, tooltip_body if len(tooltip_body) != 0 else None, makeString('#tooltips:hangar/ammo_panel/module/note'))

        data = yield AvailableItemsRequester(g_currentVehicle.vehicle, type).request()
        if type in Fitting.__ARTEFACTS_SLOTS:
            unlocks = [ m for m in data if m.isCurrent ]
        else:
            unlocks = yield StatsRequester().getUnlocks()
        data.sort(reverse=True)
        value = []
        credits = yield StatsRequester().getCredits()
        gold = yield StatsRequester().getGold()
        for module in data:
            value.append(gui_items.compactItem(module))
            value.append(module.name if type in Fitting.__ARTEFACTS_SLOTS else module.longName)
            value.append(module.getTableName(g_currentVehicle.vehicle))
            price = yield module.getPrice()
            if type == ITEM_TYPE_NAMES[3] and not g_currentVehicle.vehicle.hasTurrets:
                value.append(2)
            else:
                value.append(module.target)
            if price[1] == 0:
                value.append(price[0])
                value.append('credits')
            else:
                value.append(price[1])
                value.append('gold')
            value.append(module.icon if type in Fitting.__ARTEFACTS_SLOTS else module.level)
            fits = isModuleFitVehicle(module, g_currentVehicle.vehicle, price, (credits, gold), unlocks)
            value.append(fits[1])
            value.append(createToolTip(module, fits[2]))
            if type in Fitting.__ARTEFACTS_SLOTS:
                fits = isModuleFitVehicle(module, g_currentVehicle.vehicle, price, (credits, gold), unlocks, 1)
                value.append(fits[1])
                value.append(createToolTip(module, fits[2]))
                fits = isModuleFitVehicle(module, g_currentVehicle.vehicle, price, (credits, gold), unlocks, 2)
                value.append(fits[1])
                value.append(createToolTip(module, fits[2]))
                value.append(module.index)
                value.append(module.isRemovable)

        if type in Fitting.__ARTEFACTS_SLOTS:
            cost = yield StatsRequester().getPaidRemovalCost()
            value.append(0)
            value.append(cost)
            unlock_reasons = [ '' for i in xrange(6) ]
            for i, module in enumerate(unlocks):
                if module:
                    fits1 = isModuleFitVehicle(module, g_currentVehicle.vehicle, (0, 0), (credits, gold), unlocks, module.index, True)
                    fits2 = isModuleFitVehicle(module, g_currentVehicle.vehicle, (0, cost), (credits, gold), unlocks, module.index, True)
                    unlock_reasons[module.index * 2] = fits1[1]
                    unlock_reasons[module.index * 2 + 1] = fits2[1]

            value.extend(unlock_reasons)
        self.call('hangar.set' + type, value)
        self.__requestsCount -= 1
        if self.__requestsCount == 0:
            Waiting.hide('updateFitting')

    @process
    def onFittingChange(self, callbackID, id, slotIdx=0, isUseGold=False):
        component = gui_items.getItemByCompact(id)
        installAmmoVehicle = g_currentVehicle.vehicle
        conflictedEqs = findConflictedEquipmentForModule(component, installAmmoVehicle)
        if isinstance(component, gui_items.ShopItem):
            if conflictedEqs:
                confirmMsg = makeString('#dialogs:buyInstallConfirmation/conflictedMessage', name=component.name, conflicted="', '".join([ VehicleItem(descriptor=eq).name for eq in conflictedEqs ]))
            else:
                confirmMsg = makeString('#dialogs:buyInstallConfirmation/message', name=component.name)
            isConfirmed = yield async_showConfirmDialog('buyInstallConfirmation', customMessage=confirmMsg)
            if not isConfirmed:
                return
            Waiting.show('buyItem')
            response = yield component.buy()
            success = response[0]
            message = response[1]
            smType = response[2] if len(response) > 2 else SystemMessages.SM_TYPE.Error
            component = response[3] if len(response) > 3 else None
            SystemMessages.g_instance.pushMessage(message, smType)
            if success and component is not None:
                self.uiHolder.updateAccountInfo()
            Waiting.hide('buyItem')
        elif conflictedEqs:
            isConfirmed = yield async_showConfirmDialog('removeIncompatibleEqs', customMessage=makeString('#dialogs:removeIncompatibleEqs/customMessage', "', '".join([ VehicleItem(descriptor=eq).name for eq in conflictedEqs ])))
            if not isConfirmed:
                return
        Waiting.show('applyModule')
        success, message, removed = yield component.apply(slotIdx=int(slotIdx), isUseGold=isUseGold)
        messageType = SystemMessages.SM_TYPE.DismantlingForGold if isUseGold else SystemMessages.SM_TYPE.Information
        if not success:
            messageType = SystemMessages.SM_TYPE.Error
        if removed:
            removedItems = []
            for eqKd in removed.get('incompatibleEqs', []):
                item = VehicleItem(compactDescr=eqKd)
                removedItems.append(item.name)

            if removedItems:
                SystemMessages.pushI18nMessage('#system_messages:fitting/remove/incompatibleEqs', "', '".join(removedItems), type=messageType)
        SystemMessages.pushI18nMessage(message, type=messageType)
        if success and component.itemTypeName in ('vehicleTurret', 'vehicleGun'):
            g_hangarSpace.refreshVehicle()
            iAmmo = yield Requester('shell').getFromInventory()
            iVehicles = yield Requester('vehicle').getFromInventory()
            for iVehicle in iVehicles:
                if iVehicle.inventoryId == g_currentVehicle.vehicle.inventoryId:
                    installAmmoVehicle = iVehicle

            for shell in installAmmoVehicle.shells:
                iCount = iAmmo[iAmmo.index(shell)].count if shell in iAmmo else 0
                if shell.default > iCount:
                    success, message = False, '#system_messages:charge/inventory_error'
                    break
            else:
                success, message = yield installAmmoVehicle.loadShells(None)

            SystemMessages.g_instance.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Information if success else SystemMessages.SM_TYPE.Warning)
        Waiting.hide('applyModule')
        return
