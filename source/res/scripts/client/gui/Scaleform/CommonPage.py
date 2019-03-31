# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/CommonPage.py
# Compiled at: 2019-01-22 20:48:44
from gui.Scaleform.CaptchaView import CaptchaView
import BigWorld, GUI, datetime, Keys, weakref, Event, constants, account_helpers, nations
from adisp import process
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION, LOG_ERROR
from exceptions import DeprecationWarning
from gui import SystemMessages, GUI_NATIONS, GUI_NATIONS_ORDER_INDEX
from gui.Scaleform import main_interfaces, VoiceChatInterface, FEATURES
from gui.Scaleform.BattleDispatcherInterface import BattleDispatcherInterface
from gui.Scaleform.CursorDelegator import g_cursorDelegator
from gui.Scaleform.SettingsInterface import SettingsInterface
from gui.Scaleform.SoundManager import SoundManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.windows import GUIWindow
from gui.Scaleform.TankmenInterface import TankmenInterface
from gui.Scaleform.utils.key_mapping import getScaleformKey, voidSymbol
from gui.Scaleform.utils.gui_items import getItemByCompact, formatPrice, getVehicleFullName, compactItem, InventoryItem, VehicleItem
from gui.Scaleform.utils.functions import makeTooltip, isModuleFitVehicle
from gui.Scaleform.utils.requesters import StatsRequester, Requester, AvailableItemsRequester
from gui.Scaleform.utils.HangarSpace import g_hangarSpace
from messenger.gui import MessengerDispatcher
from PlayerEvents import g_playerEvents
from items import vehicles
from helpers.links import getPaymentWebsiteURL, openPaymentWebsite, openFinPasswordWebsite
from helpers.i18n import convert, makeString
from helpers.time_utils import makeLocalServerTime
from gui.Scaleform.utils import dossiers_utils
from items.vehicles import getDefaultAmmoForGun, parseIntCompactDescr
from account_helpers.AccountSettings import AccountSettings
from items.tankmen import getSkillsConfig
from AccountCommands import LOCK_REASON
from external_strings_utils import isPasswordValid
from LogitechMonitor import LogitechMonitor

class CommonPage(GUIWindow):
    """
    Interface common swf, serves:
    - implementation common lobby functions (collect statistics, exit/logoff, etc.)
    - to load the appropriate interface is loaded from flash page
    """
    __mainInterface = None
    __settingsInterface = None
    currentInterface = None
    __statsCallbackId = None
    __isSubscribe = False

    def __init__(self):
        self.proxy = weakref.proxy(self)
        GUIWindow.__init__(self, 'common.swf')
        self.__settingsInterface = None
        self.__battleDispatcher = None
        self.__soundManager = None
        self.commandsBinded = False
        self.addExternalCallbacks({'Loader.LoadStart': self.onLoadStart,
         'Loader.LoadInit': self.onLoadInit,
         'common.getAccountInfo': self.onUpdateAccountInfo,
         'common.Exchange': self.onExchange,
         'common.spaceMove': self.onSpaceMove,
         'common.getModuleInfo': self.onModuleInfo,
         'common.getAchievementInfo': self.onAchievementInfo,
         'common.getVehicleInfo': self.onVehicleInfo,
         'common.getXPExchangeInfo': self.getExchangeXPInfo,
         'common.ConvertXP': self.onConvertXP,
         'common.XPToTmen': self.onXPToTmen,
         'profile.getPremiumCost': self.getPremiumCost,
         'profile.PrebiumBuy': self.buyPremium,
         'common.payment': self.onPayment,
         'common.steamPayment': self.onSteamPayment,
         'common.restoreFinPass': self.onFinPasswordWebPage,
         'common.getNations': self.getNations,
         'common.getShopBuyWindowStats': self.__onShopBuyWindowGetStats,
         'common.buyItem': self.__onBuyItem,
         'common.saveShopBuyWindowSetting': self.__onSaveShopBuyWindowSetting,
         'common.populateGatheringWindow': self.onPopulateGatheringWindow,
         'common.exchangeVehiclesXP': self.onExchangeVehiclesXP,
         'common.populateTechnicalMaitenance': self.onPopulateTechnicalMaintenance,
         'common.populateTechnicalMaitenanceEquipments': self.onPopulateTechnicalMaintenanceEquipments,
         'common.installEquipment': self.onInstallEquipment,
         'common.setRefillSettings': self.onSetRefillSettings,
         'common.showWaiting': self.onShowWaiting,
         'common.hideWaiting': self.onCloseWaiting,
         'common.transferMoney': self.onTransferMoney,
         'common.transferMoneyPopulateUI': self.onTransferMoneyPopulateUI,
         'common.showMoneyTransfer': self.onShowMoneyTransfer})
        self.onXPConverted = Event.Event()
        BigWorld.wg_setRedefineKeysMode(True)
        return

    def afterCreate(self):
        GUIWindow.afterCreate(self)
        LOG_DEBUG('[CommonPage] afterCreate')
        setattr(self.movie, '_global.wg_isDevelopment', constants.IS_DEVELOPMENT)
        setattr(self.movie, '_global.wg_isShowLanguageBar', constants.SHOW_LANGUAGE_BAR)
        setattr(self.movie, '_global.wg_isShowServerStats', constants.IS_SHOW_SERVER_STATS)
        setattr(self.movie, '_global.wg_isShowVoiceChat', FEATURES.VOICE_CHAT)
        BigWorld.wg_setScreenshotNotifyCallback(self.__screenshotNotifyCallback)
        self.__soundManager = SoundManager()
        self.__soundManager.populateUI(self.proxy)
        VoiceChatInterface.g_instance.populateUI(self.proxy)
        if self.__mainInterface:
            self.__mainInterface.populateUI(self.proxy)
        self.call('common.disablePaymentButon', [len(getPaymentWebsiteURL()) == 0])
        from game import g_guiResetters
        g_guiResetters.add(self.onUpdateStage)
        self.onUpdateStage()
        self.movie.setFocussed()

    def beforeDelete(self):
        if self.__soundManager:
            self.__soundManager.dispossessUI()
            self.__soundManager = None
        if VoiceChatInterface.g_instance:
            VoiceChatInterface.g_instance.dispossessUI()
        if self.__mainInterface:
            self.__mainInterface.dispossessUI()
        self._unsubscribe()
        LOG_DEBUG('[CommonPage] beforeDelete')
        GUIWindow.beforeDelete(self)
        from game import g_guiResetters
        g_guiResetters.discard(self.onUpdateStage)
        return

    def bindExCallbackToKey(self, key, command, function):
        try:
            gfx_key = getScaleformKey(key)
            if gfx_key != voidSymbol:
                self.movie.invoke(('bindExCallbackToKey', [gfx_key, command]))
                self.addExternalCallback(command, function)
            else:
                LOG_ERROR("Can't convert key:", key)
        except:
            LOG_CURRENT_EXCEPTION()

    def clearExCallbackToKey(self, key, command, function=None):
        try:
            gfx_key = getScaleformKey(key)
            if gfx_key != voidSymbol:
                self.movie.invoke(('clearExCallbackToKey', [gfx_key]))
                self.removeExternalCallback(command, function=function)
            else:
                LOG_ERROR("Can't convert key:", key)
        except:
            LOG_CURRENT_EXCEPTION()

    def _subscribe(self):
        if self.__isSubscribe:
            return
        self.__isSubscribe = True
        g_currentVehicle.onChanged += self.__changeCurrentVehicle
        g_playerEvents.onClientUpdated += self.__pe_onClientUpdated
        g_playerEvents.onServerStatsReceived += self.onStatsReceived
        g_playerEvents.onVehicleLockChanged += self.lockChange
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        g_playerEvents.onShopResyncStarted += self.onShopResyncStarted
        g_playerEvents.onShopResync += self.onShopResync
        g_playerEvents.onCenterIsLongDisconnected += self.centerIsUnavailable
        self.centerIsUnavailable(True)
        self.captcha = CaptchaView()
        self.captcha.populateUI(self.proxy)
        MessengerDispatcher.g_instance.currentWindow.populateUI(self)
        self.__settingsInterface = SettingsInterface(enableRedefineKeysMode=False)
        self.__settingsInterface.populateUI(self.proxy)
        self.__battleDispatcher = BattleDispatcherInterface()
        self.__battleDispatcher.populateUI(self.proxy)

    def _unsubscribe(self):
        if not self.__isSubscribe:
            return
        else:
            self.__isSubscribe = False
            g_currentVehicle.onChanged -= self.__changeCurrentVehicle
            g_playerEvents.onClientUpdated -= self.__pe_onClientUpdated
            g_playerEvents.onServerStatsReceived -= self.onStatsReceived
            g_playerEvents.onVehicleLockChanged -= self.lockChange
            g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
            g_playerEvents.onShopResyncStarted -= self.onShopResyncStarted
            g_playerEvents.onShopResync -= self.onShopResync
            g_playerEvents.onCenterIsLongDisconnected -= self.centerIsUnavailable
            self.captcha.dispossessUI()
            self.captcha = None
            MessengerDispatcher.g_instance.currentWindow.dispossessUI()
            if self.__statsCallbackId is not None:
                BigWorld.cancelCallback(self.__statsCallbackId)
                self.__statsCallbackId = None
            self.__settingsInterface.dispossessUI()
            self.__settingsInterface = None
            self.__battleDispatcher.dispossessUI()
            self.__battleDispatcher = None
            return

    def clearCommands(self):
        from CommandMapping import g_instance as cmdMapping
        key = cmdMapping.get('CMD_VOICECHAT_MUTE')
        self.clearExCallbackToKey(key, 'VoiceChat.PushToTalk', function=self.onVoiceChatPTT)

    def bindCommands(self):
        self.commandsBinded = True
        from CommandMapping import g_instance as cmdMapping
        key = cmdMapping.get('CMD_VOICECHAT_MUTE')
        self.bindExCallbackToKey(key, 'VoiceChat.PushToTalk', self.onVoiceChatPTT)

    def __screenshotNotifyCallback(self, path):
        SystemMessages.g_instance.pushMessage(convert(makeString('#menu:screenshot/save')) % {'path': path}, SystemMessages.SM_TYPE.Information)

    def showCursor(self, isShow):
        self.call('common.showCursor', [isShow])

    def __callPasswordResponse(self, code, errString):
        result = 'valid'
        if code < 0:
            if errString == 'WRONG_PASSWD':
                result = 'invalid'
            elif errString == 'WRONG_PASSWD_LIMIT':
                result = 'limit'
            elif errString == 'WRONG_PASSWD_VALID':
                result = 'wrong'
        self.call('common.validatePasswordResponse', [result == 'valid', makeString('#dialogs:finance_dialog/results/%s' % result)])

    @process
    def onShowMoneyTransfer(self, callbackId, uid, userName):
        rs = yield StatsRequester().getRestrictions()
        if constants.RESTRICTION_TYPE.TRADING in rs:
            for r in rs[constants.RESTRICTION_TYPE.TRADING].itervalues():
                lExpiryTime = makeLocalServerTime(r.get('expiryTime', 0))
                if r.get('expiryTime', 0) == 0 or datetime.datetime.utcfromtimestamp(lExpiryTime) > datetime.datetime.utcnow():
                    reason = makeString('#dialogs:moneyTransferRestriction/message') % makeString(r.get('reason', ''))
                    expiryTime = r.get('expiryTime', 0)
                    if expiryTime != 0:
                        expiry = makeString('#dialogs:moneyTransferRestriction/message_expiry') % BigWorld.wg_getLongDateFormat(expiryTime) + ' ' + BigWorld.wg_getShortTimeFormat(expiryTime)
                    else:
                        expiry = ''
                    self.call('common.showMessageDialog', ['moneyTransferRestriction',
                     False,
                     False,
                     '%s %s' % (reason, expiry)])
                    return

        self.call('common.showMoneyTransfer', [uid, userName])

    @process
    def onTransferMoney(self, callbackId, uid, userName, gold, password=''):
        has_fin_pass = yield StatsRequester().hasFinPassword()

        def callback(code, errString):
            self.__callPasswordResponse(code, errString)
            Waiting.hide('transferMoney')
            if code < 0:
                if not errString == 'WRONG_PASSWD' and not errString == 'WRONG_PASSWD_LIMIT':
                    SystemMessages.g_instance.pushMessage(makeString('#system_messages:tradingError/%s' % errString), SystemMessages.SM_TYPE.Error)
                return

        Waiting.show('transferMoney')
        if password != '':
            password = password.strip()
            if not isPasswordValid(password):
                self.__callPasswordResponse(-1, 'WRONG_PASSWD_VALID')
                Waiting.hide('transferMoney')
                return
        BigWorld.player().trader.makeOffer_sellGold(password, 'Account', int(uid), 20, int(gold), 0, callback)

    @process
    def onTransferMoneyPopulateUI(self, callbackId, uid, userName):
        Waiting.show('loadStats')
        userClanId, userClanInfo = yield StatsRequester().getUserClanInfo(userName)
        gold = yield StatsRequester().getGold()
        fees = yield StatsRequester().getTradeFees()
        clanInfo = yield StatsRequester().getClanInfo()
        has_fin_pass = yield StatsRequester().hasFinPassword()
        is_clan = clanInfo is not None and userClanInfo is not None and clanInfo[2] == userClanInfo[2]
        args = [userName,
         is_clan,
         gold,
         has_fin_pass]
        fee = round(fees.get('sameClan' if is_clan else 'default', (0, 0))[1], 2)
        args.append(fee)
        descr = makeString('#dialogs:moneyTransfer/labelNotification') % int(fee * 100)
        args.append(descr + makeString('#dialogs:moneyTransfer/not_a_clan') if not is_clan else descr)
        self.call('common.moneyTransferPopulateUI', args)
        Waiting.hide('loadStats')
        return

    @process
    def onSetRefillSettings(self, callbackId, vehicleCompact, refillSection, isRefill):
        Waiting.show('loadStats')
        vcls = yield Requester('vehicle').getFromInventory()
        vehicle = getItemByCompact(vehicleCompact)
        for v in vcls:
            if v.inventoryId == vehicle.inventoryId:
                vehicle = v

        if refillSection == 'repair':
            if vehicle.isAutoRepair != isRefill:
                yield vehicle.setAutoRepair(isRefill)
        elif refillSection == 'ammo':
            if vehicle.isAutoLoad != isRefill:
                yield vehicle.setAutoLoad(isRefill)
        elif refillSection == 'equipment':
            if vehicle.isAutoEquip != isRefill:
                yield vehicle.setAutoEquip(isRefill)
        Waiting.hide('loadStats')

    @process
    def onPopulateTechnicalMaintenance(self, callbackId):
        Waiting.show('techMaintenance')
        gold = yield StatsRequester().getGold()
        credits = yield StatsRequester().getCredits()
        params = [gold, credits]
        if g_currentVehicle.isPresent():
            iVehicles = yield Requester('vehicle').getFromInventory()
            for v in iVehicles:
                if v.inventoryId == g_currentVehicle.vehicle.inventoryId:
                    vehicle = v

            params.append(vehicle.pack())
            params.append(getVehicleFullName())
            params.append(vehicle.repairCost)
            params.append(vehicle.descriptor.getMaxRepairCost())
            params.append(vehicle.isAutoRepair)
            gun = VehicleItem(vehicle.descriptor.gun)
            iAmmo = yield Requester('shell').getFromInventory()
            sAmmo = yield Requester('shell').getFromShop()
            totalPrice = {'credits': 0,
             'gold': 0}
            params.append(gun.descriptor['maxAmmo'])
            params.append(gun.descriptor['maxGoldAmmo'])
            params.append(vehicle.lock != LOCK_REASON.NONE)
            params.append(vehicle.repairCost > 0)
            casseteCount = vehicle.descriptor.gun['clip'][0]
            params.append(casseteCount)
            params.append('' if casseteCount == 1 else makeString('#menu:technicalMaintenance/ammoTitleEx') % casseteCount)
            params.append(len(vehicle.shells))
            for shell in vehicle.shells:
                shopShell = sAmmo[sAmmo.index(shell)] if shell in sAmmo else None
                if shopShell:
                    iCount = iAmmo[iAmmo.index(shell)].count if shell in iAmmo else 0
                    sPrice = (yield shopShell.getPrice()) if shell is not shopShell else (0, 0)
                    shellParams = yield shopShell.getParams(vehicle)
                    buyCount = max(shell.default - iCount - shell.count, 0)
                    params.append(compactItem(shopShell))
                    params.append(shell.type)
                    params.append('../maps/icons/ammopanel/ammo/%s' % shell.descriptor['icon'][0])
                    params.append(shell.count)
                    params.append(shell.default)
                    params.append(iCount)
                    if sPrice[1] == 0:
                        totalPrice['credits'] += sPrice[0] * buyCount
                        params.append(sPrice[0])
                        params.append('credits')
                    else:
                        totalPrice['gold'] += sPrice[1] * buyCount
                        params.append(sPrice[1])
                        params.append('gold')
                    params.append(shell.longName)
                    params.append(shell.tableName)
                    tooltip_body = ''
                    for paramType, paramValue in shellParams['parameters']:
                        tooltip_body += ' %s: <b>%s</b>\n' % (makeString('#menu:moduleInfo/params/%s' % paramType), str(paramValue))

                    params.append(makeTooltip(shell.longName, tooltip_body[:-1], makeString('#tooltips:ammo/shellitemRenderer/note')))

            params.append(totalPrice['gold'])
            params.append(totalPrice['credits'])
            params.append(vehicle.isAutoLoad)
            equipsCount = 0
            for i in xrange(len(vehicle.equipments)):
                if vehicle.equipments[i] != 0:
                    equipsCount += 1

            params.append(len(vehicle.equipments))
            params.append(equipsCount)
            params.append(vehicle.isAutoEquip)
        self.call('common.populateTechnicalMaitenance', params)
        Waiting.hide('techMaintenance')
        return

    @process
    def onPopulateTechnicalMaintenanceEquipments(self, callbackId, eId1=None, eId2=None, eId3=None, slotIndex=None):
        gold = yield StatsRequester().getGold()
        credits = yield StatsRequester().getCredits()
        availableData = yield AvailableItemsRequester(g_currentVehicle.vehicle, 'equipment').request()
        shopEqs = yield Requester('equipment').getFromShop()
        invEqs = yield Requester('equipment').getFromInventory()
        eqs = g_currentVehicle.vehicle.equipmentsLayout

        def getShopModule(module):
            for eq in shopEqs:
                if eq == module:
                    return eq

            return None

        def getInventoryModule(module):
            for eq in invEqs:
                if eq == module:
                    return eq

            return None

        installed = [ m for m in availableData if m.isCurrent ]
        if eId1 is not None or eId2 is not None or eId3 is not None or slotIndex is not None:
            installed = [ getItemByCompact(id) for id in (eId1, eId2, eId3) if id is not None ]
        data = []
        for item in availableData:
            if item in installed:
                invEq = getInventoryModule(item)
                shopModule = getShopModule(item)
                i = InventoryItem(itemTypeName='equipment', compactDescr=item.compactDescr, count=invEq.count if invEq is not None else 0, priceOrder=shopModule.priceOrder if shopModule is not None else (0, 0))
                if item == getItemByCompact(eId1):
                    i.index = 0
                elif item == getItemByCompact(eId2):
                    i.index = 1
                elif item == getItemByCompact(eId3):
                    i.index = 2
                else:
                    i.index = item.index
                i.isCurrent = True
            elif isinstance(item, InventoryItem):
                i = InventoryItem(itemTypeName='equipment', compactDescr=item.compactDescr, count=item.count + 1, priceOrder=item.priceOrder)
            else:
                i = item
            data.append(i)

        unlocks = [ m for m in data if m.isCurrent ]
        data.sort(reverse=True)
        params = [0, 0, 0]
        for m in availableData:
            if m.isCurrent:
                params[m.index] = m.compactDescr

        params.extend(eqs if len(eqs) != 0 else [0, 0, 0])
        for module in data:
            params.append(compactItem(module))
            params.append(module.name)
            params.append(module.getTableName(g_currentVehicle.vehicle))
            params.append(makeTooltip(module.toolTip, module.description, makeString('#tooltips:ammo/equipment/note')))
            params.append(module.target)
            params.append(module.compactDescr)
            shopModule = getShopModule(module)
            price = (yield shopModule.getPrice()) if shopModule is not None else (0, 0)
            if price[1] == 0:
                params.append(price[0])
                params.append('credits')
            else:
                params.append(price[1])
                params.append('gold')
            params.append(module.icon)
            params.append(module.index)
            params.append(module.count if isinstance(module, InventoryItem) else 0)
            params.append(isModuleFitVehicle(module, g_currentVehicle.vehicle, price, (credits, gold), unlocks)[1])
            params.append(isModuleFitVehicle(module, g_currentVehicle.vehicle, price, (credits, gold), unlocks, 1)[1])
            params.append(isModuleFitVehicle(module, g_currentVehicle.vehicle, price, (credits, gold), unlocks, 2)[1])

        self.call('common.populateTechnicalMaitenanceEquipments', params)
        return

    @process
    def onInstallEquipment(self, callbackId, *args):
        Waiting.show('installEquipment')
        equips = list(args)
        equipsToInstall = [0, 0, 0]
        equipmentsInv = yield Requester('equipment').getFromInventory()

        def getInventoryItem(item):
            for equipmentInv in equipmentsInv:
                if equipmentInv == item:
                    return equipmentInv

        for id in equips:
            if id is not None:
                item = getItemByCompact(id)
                if getInventoryItem(item) is not None or item.compactDescr in g_currentVehicle.vehicle.equipments:
                    equipsToInstall[equips.index(id)] = item.compactDescr
                else:
                    equipmentsShop = yield Requester('equipment').getFromShop()
                    component = None
                    for equipmentsShop in equipmentsShop:
                        if equipmentsShop == item:
                            component = equipmentsShop
                            break

                    if component is not None:
                        response = yield component.buy()
                        component = response[3] if len(response) > 3 else None
                        if response[0]:
                            equipsToInstall[equips.index(id)] = component.compactDescr
                        SystemMessages.g_instance.pushMessage(response[1], response[2] if response[0] else SystemMessages.SM_TYPE.Error)

        success = yield StatsRequester().setEquipments(g_currentVehicle.vehicle.inventoryId, equipsToInstall)
        Waiting.hide('installEquipment')
        return

    @process
    def onPopulateGatheringWindow(self, callbackId, isReset, *args):
        Waiting.show('loadStats')
        checkedVcls = list(args)
        credits = yield StatsRequester().getCredits()
        gold = yield StatsRequester().getGold()
        rate = yield StatsRequester().getFreeXPConversion()
        if rate:
            xps = yield StatsRequester().getVehicleTypeExperiences()
            eliteVcls = yield StatsRequester().getEliteVehicles()
            vcls = yield Requester('vehicle').getFromShop()
            vclsInv = yield Requester('vehicle').getFromInventory()

            def isXPTman(vcl):
                for i in vclsInv:
                    if i.descriptor.type.id == vcl.descriptor.type.id:
                        return i.isXPToTman

                return False

            values = [credits,
             gold,
             rate[0],
             rate[1]]
            for vehicle in vcls:
                if vehicle.descriptor.type.compactDescr in eliteVcls:
                    xp = xps.get(vehicle.descriptor.type.compactDescr, 0)
                    if xp == 0:
                        continue
                    values.append(vehicle.pack())
                    values.append(vehicle.level)
                    values.append(vehicle.shortName)
                    values.append(xp)
                    values.append(True if isReset else vehicle.pack() in checkedVcls)
                    values.append(isXPTman(vehicle))

            self.call('common.populateGatheringWindow', values)
        Waiting.hide('loadStats')

    @process
    def onExchangeVehiclesXP(self, callback, exchangeXP, *args):
        Waiting.show('exchangeVehiclesXP')
        vclsCompacts = list(args)
        common_xp = 0
        xps = yield StatsRequester().getVehicleTypeExperiences()
        eliteVcls = yield StatsRequester().getEliteVehicles()
        vcls = yield Requester('vehicle').getFromShop()
        for vehicle in vcls:
            if vehicle.descriptor.type.compactDescr in eliteVcls:
                common_xp += xps.get(vehicle.descriptor.type.compactDescr, 0)

        rate = yield StatsRequester().getFreeXPConversion()
        vehTypeCompDescrs = [ getItemByCompact(x).descriptor.type.compactDescr for x in vclsCompacts ]
        success = yield StatsRequester().convertVehiclesXP(min(common_xp, int(exchangeXP)), vehTypeCompDescrs)
        if success:
            SystemMessages.pushI18nMessage('#system_messages:exchangeXP/success', BigWorld.wg_getIntegralFormat(exchangeXP), formatPrice((0, round(exchangeXP / rate[0]))), type=SystemMessages.SM_TYPE.FinancialTransactionWithGold)
        else:
            SystemMessages.pushI18nMessage(makeString('#system_messages:exchangeVehiclesXP/server_error') % int(exchangeXP))
        Waiting.hide('exchangeVehiclesXP')

    def lockChange(self, id, lock):
        if g_currentVehicle.vehicle and id == g_currentVehicle.vehicle.inventoryId:
            g_currentVehicle.update()

    def __onSaveShopBuyWindowSetting(self, callbackId, value):
        AccountSettings.setSettings('shopBuyWindow', value)

    @process
    def __onBuyItem(self, callbackId, id, count, isShell=False, crew_type=0, isSlot=False):
        Waiting.show('buyItem')
        item = getItemByCompact(id)
        isCrew = crew_type is not None
        if item.itemTypeName == 'vehicle':
            itemPrice = yield item.getPrice()
            if itemPrice == (0, 0) and crew_type == 0 and not isSlot:
                leftVehicles = yield StatsRequester().getFreeVehicleLeft()
                if leftVehicles == 0:
                    self.call('common.showMessageDialog', ['freeVehicleLeftLimit', False, False])
                    Waiting.hide('buyItem')
                    return
        success = yield item.buy(count=count, isShell=isShell, isCrew=isCrew, crew_type=int(crew_type) if isCrew else 0, isSlot=isSlot)
        if item.itemTypeName == 'vehicle':
            if not g_currentVehicle.isPresent():
                g_currentVehicle.update()
            if self.currentInterface == 'shop':
                self.__mainInterface.populateFilters()
        SystemMessages.pushI18nMessage(success[1], type=success[2] if success[0] else SystemMessages.SM_TYPE.Error)
        self.call('shop.buyComplete', [success[0], success[1]])
        g_currentVehicle.onChanged()
        Waiting.hide('buyItem')
        return

    @process
    def __onShopBuyWindowGetStats(self, callbackId, id):
        isOpen = AccountSettings.getSettings('shopBuyWindow')
        item = getItemByCompact(id)
        upgradeParams = yield StatsRequester().getTankmanCost()
        eliteVcls = yield StatsRequester().getEliteVehicles()
        tankmenCount = len(item.descriptor.type.crewRoles)
        price = yield item.getPrice()
        data = [isOpen]
        data.append(item.name)
        data.append(item.longName)
        data.append(item.description)
        data.append(item.icon)
        data.append(item.nation)
        data.append(item.level)
        data.append('premium' in item.tags)
        data.append(item.descriptor.type.compactDescr in eliteVcls)
        data.append(tankmenCount)
        data.append(upgradeParams[1]['credits'] * tankmenCount)
        data.append(upgradeParams[2]['gold'] * tankmenCount)
        data.append(price[0] if price[1] == 0 else price[1])
        sPrice = [0, 0]
        shells = getDefaultAmmoForGun(item.descriptor.gun)
        for i in range(0, len(shells), 2):
            _, nationIdx, shellInnationIdx = parseIntCompactDescr(shells[i])
            shellPrice = yield StatsRequester().getShellPrice(nationIdx, shells[i])
            sPrice[0] += shellPrice[0] * shells[i + 1]
            sPrice[1] += shellPrice[1] * shells[i + 1]

        data.append(sPrice[0])
        data.append(sPrice[1])
        slots = yield StatsRequester().getSlotsCount()
        slotsPrices = yield StatsRequester().getSlotsPrices()
        slotPrice = BigWorld.player().shop.getNextSlotPrice(slots, slotsPrices)
        vehicles = yield Requester('vehicle').getFromInventory()
        data.append(slotPrice)
        data.append(len(vehicles) >= slots)
        self.call('ShopBuyWindow.PopulateUI', data)

    @process
    def processLobby(self, isInQueue=False):
        g_cursorDelegator.activateCursor()
        s = yield g_currentVehicle.getFromServer()
        self._subscribe()
        if not account_helpers.AccountPrebattle.AccountPrebattle.isTraining():
            self.movie.invoke(('loginSuccess',))
        else:
            self.movie.invoke(('loadTraining',))
        if constants.IS_SHOW_SERVER_STATS:
            self.__requestServerStats()
        self.updateAccountInfo()
        self.__battleDispatcher.start(isInQueue)
        Waiting.hide('enter')

    def processLogin(self):
        g_cursorDelegator.activateCursor()
        self._unsubscribe()
        self.commandsBinded = False
        self.movie.invoke(('loadLogin',))

    def processStartGameVideo(self):
        g_cursorDelegator.activateCursor()
        self.movie.invoke(('loadStartGameVideo',))

    def processBattleLoading(self):
        self._unsubscribe()
        self.movie.invoke(('loadBattleLoading',))

    def onShowWaiting(self, callbackId, message=''):
        LOG_DEBUG('waiting open from flash "%s"' % message)
        Waiting.show('Flash')

    def onCloseWaiting(self, callbackId):
        LOG_DEBUG('waiting close from flash')
        Waiting.hide('Flash')

    def setCredits(self, credits):
        self.call('common.creditsResponse', [credits])

    def setGold(self, gold):
        self.call('common.goldResponse', [gold])

    @process
    def getSteamPackets(self):
        packets = yield StatsRequester().getSteamGoldPackets()
        data = []
        for key, pack in packets.items():
            data.append(key)
            data.append(BigWorld.wg_getGoldFormat(pack['gold']))
            data.append(BigWorld.wg_getNiceNumberFormat(pack['amount']))
            data.append(pack['currency'])

        self.call('common.setSteamPackets', data)

    def setFreeXP(self, freeXP):
        self.call('common.setFreeXP', [freeXP])

    def setNations(self):
        result = []
        for name in nations.NAMES:
            result.append(name)

        self.call('common.nations', result)

    def setDenunciationsCount(self, count):
        self.call('common.denunciations', [count])

    def setAccountType(self, accountType, premiumExpiryTime=0):
        raise DeprecationWarning, "Account type doesn't support"

    def setAccountsAttrs(self, attrs, premiumExpiryTime=0):
        if not FEATURES.GOLD_TRANSFER and attrs & constants.ACCOUNT_ATTR.TRADING:
            attrs ^= constants.ACCOUNT_ATTR.TRADING
        isPremiumAccount = account_helpers.isPremiumAccount(attrs)
        if g_hangarSpace.inited:
            g_hangarSpace.refreshSpace(isPremiumAccount)
        else:
            g_hangarSpace.init(isPremiumAccount)
        if isPremiumAccount:
            assert premiumExpiryTime > 0
            self.call('common.setProfileType', [True, '#menu:accountTypes/premium'])
            lExpiryTime = makeLocalServerTime(premiumExpiryTime)
            delta = datetime.datetime.utcfromtimestamp(lExpiryTime) - datetime.datetime.utcnow()
            if delta.days > 0:
                timeLeft = delta.days + 1 if delta.seconds > 0 else delta.days
                timeMetric = makeString('#menu:header/account/premium/days')
            elif delta.days == 0:
                import math
                timeLeft = math.ceil(delta.seconds / 3600.0)
                timeMetric = makeString('#menu:header/account/premium/hours')
            else:
                LOG_ERROR('timedelta with negative days', premiumExpiryTime, delta)
                return
            self.call('common.setPremiumParams', [timeLeft,
             timeMetric,
             makeString('#menu:common/premiumContinue'),
             delta.days > 360])
        else:
            self.call('common.setProfileType', [False, '#menu:accountTypes/base'])
        self.call('common.accountAttrs', [attrs])
        self.call('common.premiumResponse', [isPremiumAccount])
        MessengerDispatcher.g_instance.setAccountsAttrs(attrs)

    @process
    def setClanInfo(self, clanInfo):
        name = BigWorld.player().name
        isTeamKiller = yield StatsRequester().isTeamKiller()
        clanDBID = yield StatsRequester().getClanDBID()
        if clanInfo is not None and len(clanInfo) > 1:
            name = '%s [%s]' % (name, clanInfo[1])
        self.call('common.nameResponse', [name, isTeamKiller, clanInfo != None])
        MessengerDispatcher.g_instance.setClanInfo(clanInfo)
        if clanDBID is not None and clanDBID != 0:
            tID = 'clanInfo' + name
            success = yield dossiers_utils.getClanEmblemTextureID(clanDBID, False, tID)
            if success:
                self.call('common.setClanEmblem', [tID])
        return

    def setExchangeRate(self, exchangeRate):
        self.call('common.exchangeRateResponse', [exchangeRate])

    @process
    def updateAccountInfo(self):
        exchangeRate = yield StatsRequester().getExchangeRate()
        self.setExchangeRate(exchangeRate)
        self.updateMoneyStats()
        self.updateXPInfo()
        self.updateClanInfo()
        self.updateAccountAttrs()
        self.setServerInfo()

    @process
    def updateMoneyStats(self):
        credits = yield StatsRequester().getCredits()
        self.setCredits(credits)
        gold = yield StatsRequester().getGold()
        self.setGold(gold)

    def updateAccountType(self):
        raise DeprecationWarning, "Account type doesn't support"

    @process
    def updateAccountAttrs(self):
        accAttrs = yield StatsRequester().getAccountAttrs()
        denunciations = yield StatsRequester().getDenunciations()
        isPremium = account_helpers.isPremiumAccount(accAttrs)
        premiumExpiryTime = 0
        if isPremium:
            premiumExpiryTime = yield StatsRequester().getPremiumExpiryTime()
        self.setAccountsAttrs(accAttrs, premiumExpiryTime=premiumExpiryTime)
        self.setDenunciationsCount(denunciations)
        self.setNations()

    @process
    def updateClanInfo(self):
        clanInfo = yield StatsRequester().getClanInfo()
        self.setClanInfo(clanInfo)

    @process
    def updateXPInfo(self):
        freeXP = yield StatsRequester().getFreeExperience()
        self.setFreeXP(freeXP)

    def _updateFightButton(self):
        if self.__battleDispatcher is not None:
            self.__battleDispatcher.updateFightButton()
        return

    def __requestServerStats(self):
        self.statsCallbackId = None
        if hasattr(BigWorld.player(), 'requestServerStats'):
            BigWorld.player().requestServerStats()
        return

    def onStatsReceived(self, stats):
        if constants.IS_SHOW_SERVER_STATS:
            value = []
            for stat in ('playersCount', 'arenasCount', 'playersInArenaCount'):
                value.append(dict(stats).get(stat, 0))

            self.call('common.setServerStats', value)
            self.statsCallbackId = BigWorld.callback(5, self.__requestServerStats)

    def setServerInfo(self):
        from ConnectionManager import connectionManager
        if connectionManager.serverUserName:
            self.call('common.setServerInfo', [connectionManager.serverUserName])

    def onUpdateStage(self):
        self.call('Stage.Update', list(GUI.screenResolution()))

    @process
    def getPremiumCost(self, callbackId):
        premiumCost = yield StatsRequester().getPremiumCost()
        premiumCost = sorted(premiumCost.items(), reverse=True)
        args = []
        for period, cost in premiumCost:
            args.append(period)
            args.append(cost)

        self.call('profile.setPremiumCost', args)

    def buyPremium(self, callbackId, days):
        if days:
            self.__upgradeToPremium(days)

    @process
    def __upgradeToPremium(self, days):
        Waiting.show('loadStats')
        success = yield StatsRequester().upgradeToPremium(days)
        if success:
            premiumCost = yield StatsRequester().getPremiumCost()
            if premiumCost:
                SystemMessages.g_instance.pushI18nMessage('#system_messages:premium/success', days, formatPrice((0, premiumCost[int(days)])), type=SystemMessages.SM_TYPE.PurchaseForGold)
            self._updateFightButton()
        else:
            SystemMessages.g_instance.pushI18nMessage('#system_messages:premium/server_error', days, type=SystemMessages.SM_TYPE.Error)
        Waiting.hide('loadStats')

    @process
    def __changeCurrentVehicle(self):
        freeExperience = yield StatsRequester().getFreeExperience()
        unspentXP = None
        isElite = False
        isXPToTman = False
        self._updateFightButton()
        if g_currentVehicle.isPresent():
            experiences = yield StatsRequester().getVehicleTypeExperiences()
            unspentXP = experiences.get(g_currentVehicle.vehicle.descriptor.type.compactDescr, 0)
            isElite = yield g_currentVehicle.vehicle.isElite()
            isXPToTman = isElite and g_currentVehicle.vehicle.isXPToTman
            self.call('common.vehicleChangeResponse', [g_currentVehicle.vehicle.inventoryId])
            self.call('hangar.setVehicleExperience', [unspentXP,
             freeExperience,
             isElite,
             isXPToTman])
        return

    @process
    def updateTankParams(self):
        freeExperience = yield StatsRequester().getFreeExperience()
        if g_currentVehicle.isPresent():
            self.call('common.tankNameResponse', [g_currentVehicle.vehicle.name])
            for tag in vehicles.VEHICLE_CLASS_TAGS.intersection(g_currentVehicle.vehicle.tags):
                tankType = tag

            self.call('common.tankTypeResponse', [tankType])
            elite = yield g_currentVehicle.vehicle.isElite()
            self.call('common.tankEliteResponse', [elite])
        else:
            self.call('common.tankNameResponse', [''])
            self.call('common.tankTypeResponse', [''])
            self.call('common.tankEliteResponse', [False])

    def __pe_onClientUpdated(self, diff):
        stats = diff.get('stats', {})
        if 'credits' in stats:
            self.setCredits(stats['credits'])
        if 'gold' in stats:
            self.setGold(stats['gold'])
        if 'freeXP' in stats:
            self.setFreeXP(stats['freeXP'])
        if 'clanInfo' in stats:
            self.setClanInfo(stats['clanInfo'])
        if 'hasFinPassword' in stats:
            self.call('MoneyTransfer.update', [])
        if 'denunciationsLeft' in stats:
            self.setDenunciationsCount(stats['denunciationsLeft'])
        if 'vehTypeXP' in stats:
            self.__changeCurrentVehicle()
        account = diff.get('account', {})
        if 'accountType' in account:
            self.setAccountType(account['accountType'], premiumExpiryTime=account.get('premiumExpiryTime'))
        if 'attrs' in account or 'premiumExpiryTime' in account:
            attrs = account.get('attrs', 0)
            expiryTime = account.get('premiumExpiryTime', 0)
            if expiryTime > 0:
                attrs |= constants.ACCOUNT_ATTR.PREMIUM
            self.setAccountsAttrs(attrs, premiumExpiryTime=expiryTime)
        shop = diff.get('shop', {})
        if 'exchangeRate' in shop:
            self.setExchangeRate(shop['exchangeRate'])

    def onShopResyncStarted(self):
        Waiting.show('sinhronize')
        self.call('common.closeAllWindows', [])

    def onShopResync(self):
        Waiting.hide('sinhronize')
        SystemMessages.g_instance.pushI18nMessage('#system_messages:shop_resync', type=SystemMessages.SM_TYPE.Information)

    def onLoadStart(self, id, loadingName):
        """
        Start loading lobby page into a flash
        """
        if not Waiting.isVisible() and self.currentInterface != loadingName:
            Waiting.show('loadPage')
        LogitechMonitor.onScreenChange(loadingName)

    def onLoadInit(self, id, loadingName):
        """
        Lobby page is loaded into a Flash and
        commands in the first frame of the loaded clip will be implemented
        """
        idict = main_interfaces.idict
        interfaceCls = idict.get(loadingName, None)
        if interfaceCls and self.currentInterface != loadingName:
            if self.__mainInterface:
                self.__mainInterface.dispossessUI()
            self.currentInterface = loadingName
            self.__mainInterface = interfaceCls()
            self.__mainInterface.populateUI(self.proxy)
            if self.__battleDispatcher is not None:
                self.__battleDispatcher.onPageLoadInit(loadingName)
        return

    def onUpdateAccountInfo(self, callback):
        self.updateAccountInfo()

    @process
    def onExchange(self, callback, value):
        Waiting.show('transferMoney')
        message = '#system_messages:exchange/server_error'
        success = yield StatsRequester().exchange(int(value))
        if success:
            message = '#system_messages:exchange/success'
            self.updateAccountInfo()
            if isinstance(self.__mainInterface, main_interfaces.idict['hangar']):
                self.__mainInterface.update()
        SystemMessages.g_instance.pushI18nMessage(message, BigWorld.wg_getGoldFormat(value), type=SystemMessages.SM_TYPE.FinancialTransactionWithGold if success else SystemMessages.SM_TYPE.Error)
        Waiting.hide('transferMoney')

    def onSpaceMove(self, callbackId, dx, dy, dz):
        if g_hangarSpace.space:
            g_hangarSpace.space.handleMouseEvent(int(dx), int(dy), int(dz))

    @process
    def onModuleInfo(self, callbackId, moduleId, formName, isForCurrent=False):
        module = getItemByCompact(moduleId)
        response = []
        response.append(module.longName)
        if module.itemTypeName in ('optionalDevice', 'equipment'):
            response.append(module.description)
        else:
            response.append('')
        response.append(module.itemTypeName)
        if module.itemTypeName in ('optionalDevice', 'shell', 'equipment'):
            response.append(module.icon)
        else:
            response.append(module.level)
        if isForCurrent:
            params = yield module.getParams(g_currentVehicle.vehicle)
        else:
            params = yield module.getParams(None)
        response.append(len(params['parameters']))
        for paramType, paramValue in params['parameters']:
            response.append(paramType)
            response.append(paramValue)

        response.append(len(params['compatible']))
        for paramType, paramValue in params['compatible']:
            response.append(paramType)
            response.append(paramValue)

        self.call('common.initForm' + formName, response)
        return

    def onAchievementInfo(self, callbackId, achievementType, rank, formName):
        medal = dossiers_utils.getMedal(achievementType, rank)
        self.call('common.initForm' + formName, medal)

    @process
    def onVehicleInfo(self, callbackId, vehicleId, formName, isForCurrent=False):
        vehicle = getItemByCompact(vehicleId)
        response = []
        response.append(vehicle.longName)
        response.append(vehicle.description)
        response.append(vehicle.icon)
        response.append(vehicle.level)
        response.append(vehicle.nation)
        params = yield vehicle.getParams(None)
        response.append(len(params['parameters']))
        for paramType, paramValue in params['parameters']:
            response.append(paramType)
            response.append(paramValue)

        response.append(len(params['base']))
        response.extend(params['base'])
        response.append(len(params['stats']))
        for paramType, paramValue in params['stats']:
            response.append(paramType)
            response.append(paramValue)

        tankmen = yield Requester('tankman').getFromInventory()
        isCrew = hasattr(vehicle, 'crew') and len(vehicle.crew) != 0
        crewLen = len(vehicle.descriptor.type.crewRoles)
        response.append(crewLen)
        roles_list = []
        for i in range(crewLen):
            roles_list.append({'role': vehicle.descriptor.type.crewRoles[i][0],
             'tankman_id': vehicle.crew[i] if isCrew else ''})

        def __roles_sorting(first, second):
            if TankmenInterface.TANKMEN_ORDER[first['role']] < TankmenInterface.TANKMEN_ORDER[second['role']]:
                return -1
            if TankmenInterface.TANKMEN_ORDER[first['role']] > TankmenInterface.TANKMEN_ORDER[second['role']]:
                return 1

        roles_list.sort(__roles_sorting)
        for r in roles_list:
            response.append(convert(getSkillsConfig()[r['role']]['userString']))

        fmt_str = '%s %s (%d%%)'
        if isCrew and len(vehicle.crew) != 0:
            for r in roles_list:
                if r['tankman_id'] is not None:
                    for t in tankmen:
                        if t.inventoryId == r['tankman_id']:
                            response.append(fmt_str % (t.rank, t.lastname, t.roleLevel))

                else:
                    response.append('')

        else:
            for i in range(crewLen):
                response.append('')

        self.call('common.initForm' + formName, response)
        return

    @process
    def getExchangeXPInfo(self, callbackId, vehicleTypeId=None):
        if vehicleTypeId is None:
            vehicleTypeId = g_currentVehicle.vehicle.descriptor.type.compactDescr
        xps = yield StatsRequester().getVehicleTypeExperiences()
        xp = xps.get(vehicleTypeId, 0)
        rate = yield StatsRequester().getFreeXPConversion()
        self.call('common.setXPExchangeInfo', [xp, rate[0], rate[1]])
        return

    @process
    def onConvertXP(self, callbackId, xp, vehicleTypeId=None):
        Waiting.show('exchangeVehiclesXP')
        if vehicleTypeId is None:
            vehicleTypeId = g_currentVehicle.vehicle.descriptor.type.compactDescr
        price = yield StatsRequester().getFreeXPConversion()
        message = makeString('#system_messages:exchangeXP/server_error') % BigWorld.wg_getIntegralFormat(xp)
        success = yield StatsRequester().convertToFreeXP(int(xp), vehicleTypeId)
        if success:
            message = makeString('#system_messages:exchangeXP/success') % (str(BigWorld.wg_getIntegralFormat(xp)), formatPrice((0, price[1] * xp / price[0])))
            self.onXPConverted()
        SystemMessages.g_instance.pushI18nMessage(message, type=SystemMessages.SM_TYPE.FinancialTransactionWithGold if success else SystemMessages.SM_TYPE.Error)
        Waiting.hide('exchangeVehiclesXP')
        return

    @process
    def onXPToTmen(self, callbackId, isOn, vehicle=None):
        if vehicle is None:
            vehicle = g_currentVehicle.vehicle
        else:
            vehicle = getItemByCompact(vehicle)
        elite = yield vehicle.isElite()
        message = '#system_messages:XPToTmen/server_error'
        if not elite:
            return
        else:
            success = yield vehicle.setXPToTmen(isOn)
            if success:
                if isinstance(self.__mainInterface, main_interfaces.idict['hangar']):
                    self.__mainInterface.update()
                message = '#system_messages:XPToTmen/success' + str(isOn)
            SystemMessages.g_instance.pushI18nMessage(message, vehicle.name, type=SystemMessages.SM_TYPE.Information if success else SystemMessages.SM_TYPE.Error)
            return

    def __onVehicleBecomeElite(self, vehTypeCompDescr):
        from items.vehicles import getVehicleType
        type = getVehicleType(vehTypeCompDescr)
        self.call('common.EliteDialog', [type.userString])

    def getNations(self, callbackID):
        respond = [callbackID]
        for name in GUI_NATIONS:
            if name in nations.AVAILABLE_NAMES:
                respond.append(name)
                respond.append(nations.INDICES[name])

        self.respond(respond)

    def onPayment(self, callbackId):
        openPaymentWebsite()

    def onSteamPayment(self, callbackId, packet):

        def steamResponse(steamID, itemID, error):
            LOG_DEBUG('steamInitTxn erorr code: %d' % error)
            if error == 0:
                BigWorld.wg_addSteamCallback_MicroTxnAuthorizationResponse(self.__steamCallback)

        LOG_DEBUG('steamInitTxn initid: %s' % packet)
        BigWorld.player().steamInitTxn(BigWorld.wg_getSteamID(), packet, steamResponse)

    def __steamCallback(self, AppId, OrderId, Authorized):

        def steamResponse(steamID, itemID, error):
            LOG_DEBUG('steamFinalizeTxn erorr code: %d' % error)

        LOG_DEBUD('Steam response: ', AppId, OrderId, Authorized)
        BigWorld.wg_removeSteamCallback(self.__steamCallback)
        BigWorld.player().steamFinalizeTxn(BigWorld.wg_getSteamID(), OrderId, steamResponse)

    def onFinPasswordWebPage(self, callbackId):
        openFinPasswordWebsite()

    def onVoiceChatPTT(self, responceId, isDown):
        LOG_DEBUG('onVoiceChatPTT', isDown)
        import Vivox
        if Vivox.getResponseHandler().channelsMgr.currentChannel:
            Vivox.getResponseHandler().setMicMute(not isDown)

    def centerIsUnavailable(self, isFirst=False):
        isAvailable = not BigWorld.player().isLongDisconnectedFromCenter
        if isAvailable and not isFirst:
            SystemMessages.g_instance.pushI18nMessage('#menu:centerIsAvailable', type=SystemMessages.SM_TYPE.Information)
        elif not isAvailable:
            SystemMessages.g_instance.pushI18nMessage('#menu:centerIsUnAvailable', type=SystemMessages.SM_TYPE.Warning)
