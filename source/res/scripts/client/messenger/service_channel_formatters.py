# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/service_channel_formatters.py
# Compiled at: 2019-03-07 17:18:36
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_DEBUG
import account_helpers
import ArenaType
import BigWorld, offers
from constants import INVOICE_ASSET, AUTO_MAINTENANCE_TYPE, AUTO_MAINTENANCE_RESULT, PREBATTLE_TYPE, FINISH_REASON, KICK_REASON_NAMES, KICK_REASON
import dossiers
from helpers import i18n, html, getClientLanguage
from helpers import time_utils
from items import getTypeInfoByIndex, getTypeInfoByName
from items.vehicles import getVehicleType, getDictDescr
import enumerations
from messenger import getLongDatetimeFormat, g_settings, MESSENGER_I18N_FILE

def formatPrice(price, reverse=False):
    outPrice = []
    credits, gold = price[:2]
    if credits != 0 or gold == 0:
        cname = i18n.makeString('#menu:price/credits') + ': '
        cformatted = BigWorld.wg_getIntegralFormat(credits)
        outPrice.extend([cformatted, ' ', cname] if reverse else [cname, ' ', cformatted])
        if gold != 0:
            outPrice.append(', ')
    if gold != 0:
        gname = i18n.makeString('#menu:price/gold') + ': '
        gformatted = BigWorld.wg_getGoldFormat(gold)
        outPrice.extend([gformatted, ' ', gname] if reverse else [gname, ' ', gformatted])
    return ''.join(outPrice)


class ServiceChannelFormatter(object):

    def format(self, data, *args):
        return None

    def notify(self):
        return False


class ServerRebootFormatter(ServiceChannelFormatter):

    def format(self, message):
        if message.data:
            lDatetime = time_utils.utcToLocalDatetime(message.data)
            return g_settings.getHtmlTemplate('serverReboot') % (lDatetime.strftime('%c'),)
        else:
            return None
            return None


class ServerRebootCancelledFormatter(ServiceChannelFormatter):

    def format(self, message):
        if message.data:
            lDatetime = time_utils.utcToLocalDatetime(message.data)
            return g_settings.getHtmlTemplate('serverRebootCancelled') % (lDatetime.strftime('%c'),)
        else:
            return None
            return None


class BattleResultsFormatter(ServiceChannelFormatter):
    __battleResultKeys = {-1: 'battleDefeatResult',
     0: 'battleDrawGameResult',
     1: 'battleVictoryResult'}
    __i18n_penalty = i18n.makeString('#%s:serviceChannelMessages/battleResults/penaltyForDamageAllies' % MESSENGER_I18N_FILE)
    __i18n_contribution = i18n.makeString('#%s:serviceChannelMessages/battleResults/contributionForDamageAllies' % MESSENGER_I18N_FILE)
    __i18n_actions = {'action': i18n.makeString('#%s:serviceChannelMessages/battleResults/action' % MESSENGER_I18N_FILE),
     'actions': i18n.makeString('#%s:serviceChannelMessages/battleResults/actions' % MESSENGER_I18N_FILE),
     'actionCredits': i18n.makeString('#%s:serviceChannelMessages/battleResults/actionsResultsCredits' % MESSENGER_I18N_FILE),
     'actionGold': i18n.makeString('#%s:serviceChannelMessages/battleResults/actionsResultsGold' % MESSENGER_I18N_FILE),
     'actionFreeXP': i18n.makeString('#%s:serviceChannelMessages/battleResults/actionsResultsFreeXP' % MESSENGER_I18N_FILE)}

    def notify(self):
        return True

    def format(self, message):
        battleResult = message.data
        arenaTypeID = battleResult.get('arenaTypeID', 0)
        areaneType = ArenaType.g_cache.get(arenaTypeID) if arenaTypeID > 0 else None
        arenaCreateTime = battleResult.get('arenaCreateTime', None)
        if arenaCreateTime and areaneType:
            createdAtStr = getLongDatetimeFormat(arenaCreateTime)
            mTemplate = g_settings.getHtmlTemplate(self.__battleResultKeys[battleResult['isWinner']])
            vehicle = 'N/A'
            vehicleCompDescr = battleResult.get('vehTypeCompDescr', None)
            if vehicleCompDescr:
                vt = getVehicleType(vehicleCompDescr)
                vehicle = vt.userString
            xp = battleResult.get('xp')
            xpStr = 'N/A' if xp is None else BigWorld.wg_getIntegralFormat(xp)
            xpStrEx = self.__makeXpExString(xp, battleResult)
            credits = battleResult.get('credits')
            creditsStr = 'N/A' if credits is None else BigWorld.wg_getIntegralFormat(credits)
            creditsStrEx = self.__makeCreditsExString(credits, battleResult)
            actionsStrEx = self.__makeActionsString(battleResult)
            achieves = self.__makeAchievementsString(battleResult)
            return mTemplate % (i18n.makeString(areaneType.name),
             createdAtStr,
             vehicle,
             xpStr,
             xpStrEx,
             creditsStr,
             creditsStrEx,
             actionsStrEx,
             achieves) + self.__makeVehicleLockString(vehicle, battleResult)
        else:
            return
            return

    def __makeVehicleLockString(self, vehicle, battleResult):
        expireTime = battleResult.get('vehTypeUnlockTime', 0)
        if not expireTime:
            return ''
        return g_settings.getHtmlTemplate('battleResultLocks') % (vehicle, BigWorld.wg_getShortTimeFormat(expireTime) + ' ' + BigWorld.wg_getShortDateFormat(expireTime))

    def __makeXpExString(self, xp, battleResult):
        if not xp:
            return ''
        exStrings = []
        penalty = battleResult.get('xpPenalty', 0)
        if penalty > 0:
            exStrings.append(self.__i18n_penalty % BigWorld.wg_getIntegralFormat(penalty))
        if battleResult['isWinner'] == 1:
            xpFactor = battleResult.get('dailyXPFactor', 1)
            if xpFactor > 1:
                exStrings.append(i18n.makeString('#%s:serviceChannelMessages/battleResults/doubleXpFactor' % MESSENGER_I18N_FILE) % xpFactor)
        if len(exStrings):
            return ' ({0:>s})'.format('; '.join(exStrings))

    def __makeCreditsExString(self, credits, battleResult):
        if not credits:
            return ''
        exStrings = []
        penalty = sum([battleResult.get('creditsPenalty', 0), battleResult.get('creditsContributionOut', 0)])
        if penalty > 0:
            exStrings.append(self.__i18n_penalty % BigWorld.wg_getIntegralFormat(penalty))
        contribution = battleResult.get('creditsContributionIn', 0)
        if contribution > 0:
            exStrings.append(self.__i18n_contribution % BigWorld.wg_getIntegralFormat(contribution))
        if len(exStrings):
            return ' ({0:>s})'.format('; '.join(exStrings))

    def __makeActionsString(self, battleResult):
        factors = []
        for factorName in ('xpFactor', 'freeXPFactor', 'creditsFactor'):
            f = battleResult.get(factorName, 1.0)
            if f != 1.0:
                if factorName == 'xpFactor':
                    factors.append('xp(x%s)' % f)
                if factorName == 'creditsFactor':
                    factors.append('credits(x%s)' % f)
                if factorName == 'freeXPFactor':
                    factors.append('freeXP(x%s)' % f)

        bonus = []
        for bonusName in ('actionCredits', 'actionGold', 'actionFreeXP'):
            b = battleResult.get(bonusName, 0)
            if b:
                bonus.append(self.__i18n_actions.get(bonusName) % BigWorld.wg_getIntegralFormat(b))

        if bonus or factors:
            actions = battleResult.get('actions', [])
            actionsNames = []
            for action in actions:
                actionName = action.get(getClientLanguage(), '')
                if not actionName:
                    actionName = action.values()[0]
                actionsNames.append(actionName)

            i18nKey = 'actions' if len(actionsNames) > 1 else 'action'
            return g_settings.getHtmlTemplate('battleResultActions') % self.__i18n_actions.get(i18nKey) % (', '.join(bonus + factors), ', '.join(actionsNames))

    def __makeAchievementsString(self, battleResult):
        records = battleResult.get('popUpRecords')
        if records is None or not len(records):
            return ''
        else:
            achieveList = []
            for recordIdx, value in records:
                achieveKey = dossiers.RECORD_NAMES[recordIdx]
                achieveI18n = i18n.makeString('#achievements:%s' % achieveKey)
                rule = AchievementsFormatRulesDict.get(achieveKey)
                if rule:
                    achieveList.append(rule(achieveI18n, value))
                else:
                    achieveList.append(achieveI18n)

            return g_settings.getHtmlTemplate('battleResultAchieves') % ', '.join(achieveList)


AchievementsFormatRules = enumerations.Enumeration('Achievement format rules', [('showRank', lambda key, count: key % i18n.makeString('#achievements:achievement/rank%d' % int(count)))], instance=enumerations.CallabbleEnumItem)
AchievementsFormatRulesDict = {'medalKay': AchievementsFormatRules.showRank,
 'medalCarius': AchievementsFormatRules.showRank,
 'medalKnispel': AchievementsFormatRules.showRank,
 'medalPoppel': AchievementsFormatRules.showRank,
 'medalAbrams': AchievementsFormatRules.showRank,
 'medalLeClerc': AchievementsFormatRules.showRank,
 'medalLavrinenko': AchievementsFormatRules.showRank,
 'medalEkins': AchievementsFormatRules.showRank}

class AchievementsFormatter(ServiceChannelFormatter):
    __i18nKeyMask = '#achievements:%s'

    def format(self, message):
        achievementsData = message.data
        records = achievementsData.get('records') if achievementsData is not None else None
        if records:
            aTemplate = g_settings.getHtmlTemplate('battleResultAchieves')
            achieveList = []
            for recordIdx, value in records:
                achieveKey = dossiers.RECORD_NAMES[recordIdx]
                achieveI18n = i18n.makeString(self.__i18nKeyMask % achieveKey)
                rule = AchievementsFormatRulesDict.get(achieveKey)
                if rule:
                    achieveList.append(rule(achieveI18n, value))
                else:
                    achieveList.append(achieveI18n)

            return aTemplate % ', '.join(achieveList)
        else:
            return
            return


class AutoMaintenanceFormatter(ServiceChannelFormatter):
    __messages = {AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairError',
                                                 AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadError',
                                                 AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipError'},
     AUTO_MAINTENANCE_RESULT.OK: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairSuccess',
                                  AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadSuccess',
                                  AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipSuccess'},
     AUTO_MAINTENANCE_RESULT.NOT_PERFORMED: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairSkipped',
                                             AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadSkipped',
                                             AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipSkipped'}}

    def notify(self):
        return True

    def format(self, message):
        vehicleCompDescr = message.data.get('vehTypeCD', None)
        result = message.data.get('result', None)
        type = message.data.get('typeID', None)
        cost = message.data.get('cost', (0, 0))
        if vehicleCompDescr is not None and result is not None and type is not None:
            vt = getVehicleType(vehicleCompDescr)
            if type == AUTO_MAINTENANCE_TYPE.REPAIR:
                formatMsgType = 'RepairSysMessage'
            else:
                formatMsgType = 'PurchaseForCreditsSysMessage' if cost[1] == 0 else 'PurchaseForGoldSysMessage'
            msg = i18n.makeString(self.__messages[result][type]) % vt.userString
            if result == AUTO_MAINTENANCE_RESULT.OK:
                templateName = formatMsgType
            elif result == AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS:
                templateName = 'ErrorSysMessage'
            else:
                templateName = 'WarningSysMessage'
            template = g_settings.getHtmlTemplate(templateName)
            if result == AUTO_MAINTENANCE_RESULT.OK:
                msg = msg + formatPrice((abs(cost[0]), abs(cost[1])))
            return template % msg
        else:
            return
            return


class GoldReceivedFormatter(ServiceChannelFormatter):

    def format(self, message):
        data = message.data
        gold = data.get('gold', None)
        credits = data.get('credits', None)
        freeXp = data.get('freeXp', None)
        transactionTime = data.get('date', None)
        if transactionTime:
            transactionDatetimeStr = getLongDatetimeFormat(transactionTime)
            if credits:
                return g_settings.getHtmlTemplate('moneyReceived') % (transactionDatetimeStr,
                 BigWorld.wg_getGoldFormat(account_helpers.convertGold(gold)),
                 BigWorld.wg_getIntegralFormat(credits),
                 BigWorld.wg_getIntegralFormat(freeXp))
            return g_settings.getHtmlTemplate('goldReceived') % (transactionDatetimeStr, BigWorld.wg_getGoldFormat(account_helpers.convertGold(gold)))
        else:
            return


class GiftReceivedFormatter(ServiceChannelFormatter):
    __handlers = {'money': ('_GiftReceivedFormatter__formatMoneyGiftMsg', '%sReceivedAsGift'),
     'xp': ('_GiftReceivedFormatter__formatXPGiftMsg', 'xpReceivedAsGift'),
     'premium': ('_GiftReceivedFormatter__formatPremiumGiftMsg', 'premiumReceivedAsGift'),
     'item': ('_GiftReceivedFormatter__formatItemGiftMsg', 'itemReceivedAsGift'),
     'vehicle': ('_GiftReceivedFormatter__formatVehicleGiftMsg', 'vehicleReceivedAsGift')}

    def format(self, message):
        data = message.data
        type = data.get('type')
        if type is not None:
            handlerName, templateKey = self.__handlers.get(type, (None, None))
            if handlerName is not None:
                return getattr(self, handlerName)(templateKey, data)
        return

    def __formatMoneyGiftMsg(self, templateKey, data):
        credits = data.get('credits', 0)
        gold = data.get('gold', 0)
        message = None
        if credits > 0 and gold > 0:
            message = g_settings.getHtmlTemplate(templateKey % 'creditsAndGold') % (BigWorld.wg_getGoldFormat(gold), BigWorld.wg_getIntegralFormat(credits))
        elif credits > 0:
            message = g_settings.getHtmlTemplate(templateKey % 'credits') % BigWorld.wg_getIntegralFormat(credits)
        elif gold > 0:
            message = g_settings.getHtmlTemplate(templateKey % 'gold') % BigWorld.wg_getGoldFormat(gold)
        return message

    def __formatXPGiftMsg(self, templateKey, data):
        xp = data.get('amount', 0)
        fXp = BigWorld.wg_getIntegralFormat(xp)
        if xp > 0:
            return g_settings.getHtmlTemplate(templateKey) % fXp
        else:
            return None

    def __formatPremiumGiftMsg(self, templateKey, data):
        days = data.get('amount', 0)
        if days > 0:
            return g_settings.getHtmlTemplate(templateKey) % days
        else:
            return None

    def __formatItemGiftMsg(self, templateKey, data):
        amount = data.get('amount', 0)
        itemTypeIdx = data.get('itemTypeIdx')
        itemCompactDescr = data.get('itemCD')
        if amount > 0 and itemTypeIdx is not None and itemCompactDescr is not None:
            typeString = getTypeInfoByIndex(itemTypeIdx)['userString']
            userString = getDictDescr(itemCompactDescr)['userString']
            return g_settings.getHtmlTemplate(templateKey) % (typeString, userString, amount)
        else:
            return

    def __formatVehicleGiftMsg(self, templateKey, data):
        vehicleCompDescr = data.get('typeCD', None)
        if vehicleCompDescr is not None:
            return g_settings.getHtmlTemplate(templateKey) % getVehicleType(vehicleCompDescr).userString
        else:
            return


class InvoiceReceivedFormatter(ServiceChannelFormatter):
    __assetHandlers = {INVOICE_ASSET.GOLD: '_InvoiceReceivedFormatter__formatAmount',
     INVOICE_ASSET.CREDITS: '_InvoiceReceivedFormatter__formatAmount',
     INVOICE_ASSET.PREMIUM: '_InvoiceReceivedFormatter__formatAmount',
     INVOICE_ASSET.FREE_XP: '_InvoiceReceivedFormatter__formatAmount',
     INVOICE_ASSET.DATA: '_InvoiceReceivedFormatter__formatData'}
    __operationTemplateKeys = {INVOICE_ASSET.GOLD: 'goldAccruedInvoiceReceived',
     INVOICE_ASSET.CREDITS: 'creditsAccruedInvoiceReceived',
     INVOICE_ASSET.PREMIUM: 'premiumAccruedInvoiceReceived',
     INVOICE_ASSET.FREE_XP: 'freeXpAccruedInvoiceReceived',
     INVOICE_ASSET.GOLD | 16: 'goldDebitedInvoiceReceived',
     INVOICE_ASSET.CREDITS | 16: 'creditsDebitedInvoiceReceived',
     INVOICE_ASSET.PREMIUM | 16: 'premiumDebitedInvoiceReceived',
     INVOICE_ASSET.FREE_XP | 16: 'freeXpDebitedInvoiceReceived',
     INVOICE_ASSET.GOLD | 256: 'goldCompensationInvoiceReceived',
     INVOICE_ASSET.CREDITS | 256: 'creditsCompensationInvoiceReceived'}
    __messageTemplateKeys = {INVOICE_ASSET.GOLD: 'financialInvoiceReceived',
     INVOICE_ASSET.CREDITS: 'financialInvoiceReceived',
     INVOICE_ASSET.PREMIUM: 'premiumInvoiceReceived',
     INVOICE_ASSET.FREE_XP: 'freeXpInvoiceReceived',
     INVOICE_ASSET.DATA: 'dataInvoiceReceived'}
    __i18nPiecesString = i18n.makeString('#{0:>s}:serviceChannelMessages/invoiceReceived/pieces'.format(MESSENGER_I18N_FILE))

    def __getOperationTimeString(self, data):
        operationTime = data.get('at', None)
        if operationTime:
            fDatetime = getLongDatetimeFormat(time_utils.makeLocalServerTime(operationTime))
        else:
            fDatetime = 'N/A'
        return fDatetime

    def __getFinOperationString(self, assetType, amount, subKey=0):
        if not subKey:
            templateKey = 0 if amount > 0 else 16
            templateKey |= assetType
        else:
            templateKey = assetType | subKey
        if assetType == INVOICE_ASSET.GOLD:
            fAmount = BigWorld.wg_getGoldFormat(abs(amount))
        else:
            fAmount = BigWorld.wg_getIntegralFormat(abs(amount))
        templateName = self.__operationTemplateKeys[templateKey]
        return g_settings.getHtmlTemplate(templateName) % fAmount

    def __getItemsString(self, items):
        accrued = []
        debited = []
        for itemCompactDescr, count in items.iteritems():
            if count:
                try:
                    item = getDictDescr(itemCompactDescr)
                    itemString = '{0:>s} "{1:>s}" - {2:d} {3:>s}'.format(getTypeInfoByName(item['itemTypeName'])['userString'], item['userString'], count, self.__i18nPiecesString)
                    if count > 0:
                        accrued.append(itemString)
                    else:
                        debited.append(itemString)
                except:
                    LOG_ERROR('itemCompactDescr can not parse ', itemCompactDescr)
                    LOG_CURRENT_EXCEPTION()

        result = ''
        if len(accrued):
            result = g_settings.getHtmlTemplate('itemsAccruedInvoiceReceived') % ', '.join(accrued)
        if len(debited):
            if len(result):
                result += '<br/>'
            result += g_settings.getHtmlTemplate('itemsDebitedInvoiceReceived') % ', '.join(debited)
        return result

    def __getVehiclesString(self, vehicles, exclude=None, template='vehiclesAccruedInvoiceReceived'):
        vehNames = []
        if exclude is None:
            exclude = []
        for vehCompDescr in vehicles:
            if vehCompDescr is not None:
                if vehCompDescr in exclude:
                    continue
                try:
                    vehNames.append(getVehicleType(vehCompDescr).userString)
                except:
                    LOG_ERROR('vehicleCompDescr can not parse ', vehCompDescr)
                    LOG_CURRENT_EXCEPTION()

        result = ''
        if len(vehNames):
            result = g_settings.getHtmlTemplate(template) % ', '.join(vehNames)
        return result

    def __getL10nDescription(self, data):
        l10nDescr = data.get('data', {}).get('localized_description')
        descr = ''
        if l10nDescr is not None and len(l10nDescr):
            descr = html.htmlEscape(l10nDescr.get(getClientLanguage(), l10nDescr.values()[0]).get('description', u'').encode('utf-8'))
            if len(descr):
                descr = '<br/>' + descr
        return descr

    def __makeComptnDict(self, data):
        result = {}
        for items, comptn in data.get('compensation', []):
            for key, data in items.iteritems():
                exKey = 'ex_{0:>s}'.format(key)
                result.setdefault(exKey, [])
                result[exKey].extend(data)

            for key, data in comptn.iteritems():
                result.setdefault(key, 0)
                try:
                    result[key] += data
                except TypeError:
                    LOG_CURRENT_EXCEPTION()

        return result

    def __formatAmount(self, assetType, data):
        amount = data.get('amount', None)
        if amount is None:
            return
        else:
            fDatetime = self.__getOperationTimeString(data)
            l10nDescr = self.__getL10nDescription(data)
            templateName = self.__messageTemplateKeys[assetType]
            return g_settings.getHtmlTemplate(templateName) % (fDatetime, l10nDescr, self.__getFinOperationString(assetType, amount))

    def __formatData(self, assetType, data):
        dataEx = data.get('data', {})
        if dataEx is None or not len(dataEx):
            return
        else:
            fDatetime = self.__getOperationTimeString(data)
            l10nDescr = self.__getL10nDescription(data)
            operations = []
            comptnDict = self.__makeComptnDict(data)
            gold = dataEx.get('gold')
            if gold is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.GOLD, gold))
            credits = dataEx.get('credits')
            if credits is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.CREDITS, credits))
            freeXp = dataEx.get('freeXP')
            if freeXp is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.FREE_XP, freeXp))
            premium = dataEx.get('premium')
            if premium is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.PREMIUM, premium))
            items = dataEx.get('items', {})
            if items is not None and len(items) > 0:
                operations.append(self.__getItemsString(items))
            vehicles = dataEx.get('vehicles', {})
            if vehicles is not None and len(vehicles) > 0:
                exclude = comptnDict.get('ex_vehicles', [])
                result = self.__getVehiclesString(vehicles, exclude=exclude)
                if len(result):
                    operations.append(result)
                if len(exclude):
                    operations.append(self.__getVehiclesString(exclude, template='vehiclesInHangarInvoiceReceived'))
            comptnGold = comptnDict.get('gold')
            if comptnGold is not None and comptnGold > 0:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.GOLD, comptnGold, subKey=256))
            comptnCredits = comptnDict.get('credits')
            if comptnCredits is not None and comptnCredits > 0:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.CREDITS, comptnCredits, subKey=256))
            templateName = self.__messageTemplateKeys[assetType]
            return g_settings.getHtmlTemplate(templateName) % (fDatetime, l10nDescr, '<br/>'.join(operations))

    def format(self, message):
        LOG_DEBUG('invoiceReceived', message)
        data = message.data
        assetType = data.get('assetType', -1)
        handler = self.__assetHandlers.get(assetType)
        if handler is not None:
            return getattr(self, handler)(assetType, data)
        else:
            return
            return


class AdminMessageFormatter(ServiceChannelFormatter):

    def format(self, message):
        if message.data:
            return g_settings.getHtmlTemplate('adminMessage') % message.data.decode('utf-8')
        else:
            return None
            return None


class AccountTypeChangedFormatter(ServiceChannelFormatter):

    def format(self, message):
        data = message.data
        isPremium = data.get('isPremium', None)
        expiryTime = data.get('expiryTime', None)
        if isPremium is not None:
            accountTypeName = i18n.makeString('#menu:accountTypes/premium') if isPremium else i18n.makeString('#menu:accountTypes/base')
            expiryDatetime = getLongDatetimeFormat(expiryTime) if expiryTime else None
            if expiryDatetime:
                return g_settings.getHtmlTemplate('accountTypeChangedWithExpiration') % (accountTypeName, expiryDatetime)
            else:
                return g_settings.getHtmlTemplate('accountTypeChanged') % (accountTypeName,)
        return


class PremiumActionFormatter(ServiceChannelFormatter):
    _templateKey = None

    def _getMessage(self, isPremium, expiryTime):
        pass

    def format(self, message):
        data = message.data
        isPremium = data.get('isPremium', None)
        expiryTime = data.get('expiryTime', None)
        if isPremium is not None:
            return self._getMessage(isPremium, expiryTime)
        else:
            return


class PremiumBoughtFormatter(PremiumActionFormatter):
    _templateKey = 'premiumBought'

    def _getMessage(self, isPremium, expiryTime):
        result = None
        if isPremium is True and expiryTime > 0:
            expiryDatetime = getLongDatetimeFormat(expiryTime)
            result = g_settings.getHtmlTemplate(self._templateKey) % expiryDatetime
        return result


class PremiumExtendedFormatter(PremiumBoughtFormatter):
    _templateKey = 'premiumExtended'


class PremiumExpiredFormatter(PremiumActionFormatter):
    _templateKey = 'premiumExpired'

    def _getMessage(self, isPremium, expiryTime):
        result = None
        if isPremium is False:
            result = g_settings.getHtmlTemplate(self._templateKey)
        return result


class WaresSoldFormatter(ServiceChannelFormatter):

    def notify(self):
        return True

    def format(self, message):
        if message.data:
            offer = offers._makeOutOffer(message.data)
            return g_settings.getHtmlTemplate('waresSoldAsGold') % (BigWorld.wg_getGoldFormat(offer.srcWares), offer.dstName, offer.fee)
        else:
            return None
            return None


class WaresBoughtFormatter(ServiceChannelFormatter):

    def notify(self):
        return True

    def format(self, message):
        if message.data:
            offer = offers._makeInOffer(message.data)
            return g_settings.getHtmlTemplate('waresBoughtAsGold') % (offer.srcName, BigWorld.wg_getGoldFormat(offer.srcWares))
        else:
            return None
            return None


class PrebattleFormatter(ServiceChannelFormatter):
    __battleTypeByPrebattleType = {PREBATTLE_TYPE.TOURNAMENT: 'tournament',
     PREBATTLE_TYPE.CLAN: 'clan'}
    _battleFinishReasonKeys = {}
    _defaultBattleFinishReasonKey = ('base', True)

    def notify(self):
        return True

    def _getIconId(self, type):
        iconId = 'BattleResultIcon'
        if type == PREBATTLE_TYPE.CLAN:
            iconId = 'ClanBattleResultIcon'
        elif type == PREBATTLE_TYPE.TOURNAMENT:
            iconId = 'TournamentBattleResultIcon'
        return iconId

    def _makeBattleTypeString(self, type):
        typeString = self.__battleTypeByPrebattleType.get(type, 'prebattle')
        key = '#{0:>s}:serviceChannelMessages/prebattle/battleType/{1:>s}'.format(MESSENGER_I18N_FILE, typeString)
        return i18n.makeString(key)

    def _makeDescriptionString(self, data, showBattlesCount=True):
        if data.has_key('localized_data') and len(data['localized_data']):
            description = account_helpers.AccountPrebattle.AccountPrebattle.getPrebattleDescription(data).encode('utf-8')
            description = html.htmlEscape(description)
        else:
            type = data.get('type')
            description = self._makeBattleTypeString(type)
        battlesLimit = data.get('battlesLimit', 0)
        if showBattlesCount and battlesLimit > 1:
            battlesCount = data.get('battlesCount')
            if battlesCount > 0:
                key = '#{0:>s}:serviceChannelMessages/prebattle/numberOfBattle'.format(MESSENGER_I18N_FILE)
                numberOfBattleString = i18n.makeString(key, battlesCount)
                description = '{0:>s} {1:>s}'.format(description, numberOfBattleString)
            else:
                LOG_WARNING('Invalid value of battlesCount ', battlesCount)
        return description

    def _getOpponentsString(self, opponents):
        firstOpponent = opponents.get('1', {}).get('name', '').encode('utf-8')
        secondOpponent = opponents.get('2', {}).get('name', '').encode('utf-8')
        result = ''
        if len(firstOpponent) > 0 and len(secondOpponent) > 0:
            result = g_settings.getHtmlTemplate('prebattleOpponents') % (html.htmlEscape(firstOpponent), html.htmlEscape(secondOpponent))
        return result

    def _getBattleResultString(self, winner, team):
        result = 'undefined'
        if 3 > winner > -1 and team in (1, 2):
            if not winner:
                result = 'draftGame'
            else:
                result = 'defeat' if team != winner else 'win'
        return result

    def _makeBattleResultString(self, finishReason, winner, team):
        finishString, showResult = self._battleFinishReasonKeys.get(finishReason, self._defaultBattleFinishReasonKey)
        if showResult:
            resultString = self._getBattleResultString(winner, team)
            key = '#{0:>s}:serviceChannelMessages/prebattle/finish/{1:>s}/{2:>s}'.format(MESSENGER_I18N_FILE, finishString, resultString)
        else:
            key = '#{0:>s}:serviceChannelMessages/prebattle/finish/{1:>s}'.format(MESSENGER_I18N_FILE, finishString)
        return i18n.makeString(key)


class PrebattleArenaFinishFormatter(PrebattleFormatter):
    _battleFinishReasonKeys = {FINISH_REASON.TECHNICAL: ('technical', True),
     FINISH_REASON.FAILURE: ('failure', False),
     FINISH_REASON.UNKNOWN: ('failure', False)}

    def format(self, message):
        LOG_DEBUG('prbArenaFinish', message)
        data = message.data
        type = data.get('type')
        winner = data.get('winner')
        team = data.get('team')
        wins = data.get('wins')
        finishReason = data.get('finishReason')
        createTime = data.get('createTime')
        if None in [type,
         winner,
         team,
         wins,
         finishReason,
         createTime]:
            return
        else:
            iconId = self._getIconId(type)
            description = self._makeDescriptionString(data)
            opponents = self._getOpponentsString(data.get('opponents', {}))
            if message.createdAt is not None:
                fCreateTime = message.createdAt.strftime('%c')
            else:
                LOG_WARNING('Invalid value of created_at = None')
                import time
                fCreateTime = getLongDatetimeFormat(time.time())
            battleResult = self._makeBattleResultString(finishReason, winner, team)
            subtotal = ''
            battlesLimit = data.get('battlesLimit', 0)
            if battlesLimit > 1:
                battlesCount = data.get('battlesCount', -1)
                winsLimit = data.get('winsLimit', -1)
                if battlesCount == battlesLimit or winsLimit == wins[1] or winsLimit == wins[2]:
                    playerTeamWins = wins[team]
                    otherTeamWins = wins[2 if team == 1 else 1]
                    if winsLimit > 0 and playerTeamWins < winsLimit and otherTeamWins < winsLimit:
                        winner = None
                    elif playerTeamWins == otherTeamWins:
                        winner = 0
                    else:
                        winner = 1 if wins[1] > wins[2] else 2
                    sessionResult = self._makeBattleResultString(-1, winner, team)
                    subtotal = g_settings.getHtmlTemplate('prebattleTotal') % (sessionResult, wins[1], wins[2])
                else:
                    subtotal = g_settings.getHtmlTemplate('prebattleSubtotal') % (wins[1], wins[2])
            return g_settings.getHtmlTemplate('prebattleArenaFinish') % (iconId,
             description,
             fCreateTime,
             opponents,
             battleResult,
             subtotal)


class PrebattleKickFormatter(PrebattleFormatter):

    def format(self, message):
        data = message.data
        type = data.get('type')
        kickReason = data.get('kickReason')
        if type > 0 and kickReason > 0:
            key = '#system_messages:prebattle/kick/type/unknown'
            if type == PREBATTLE_TYPE.SQUAD:
                key = '#system_messages:prebattle/kick/type/squad'
            elif type == PREBATTLE_TYPE.COMPANY:
                key = '#system_messages:prebattle/kick/type/team'
            typeString = i18n.makeString(key)
            kickName = KICK_REASON_NAMES[kickReason]
            key = '#system_messages:prebattle/kick/reason/{0:>s}'.format(kickName)
            reasonString = i18n.makeString(key)
            return g_settings.getHtmlTemplate('prebattleKick') % (typeString, reasonString)
        else:
            return None
            return None


class PrebattleDestructionFormatter(PrebattleFormatter):
    _battleFinishReasonKeys = {KICK_REASON.ARENA_CREATION_FAILURE: ('failure', False),
     KICK_REASON.AVATAR_CREATION_FAILURE: ('failure', False),
     KICK_REASON.VEHICLE_CREATION_FAILURE: ('failure', False),
     KICK_REASON.PREBATTLE_CREATION_FAILURE: ('failure', False),
     KICK_REASON.BASEAPP_CRASH: ('failure', False),
     KICK_REASON.CELLAPP_CRASH: ('failure', False),
     KICK_REASON.UNKNOWN_FAILURE: ('failure', False),
     KICK_REASON.CREATOR_LEFT: ('creatorLeft', False),
     KICK_REASON.PLAYERKICK: ('playerKick', False),
     KICK_REASON.TIMEOUT: ('timeout', False)}

    def format(self, message):
        LOG_DEBUG('prbDestruction', message)
        data = message.data
        type = data.get('type')
        team = data.get('team')
        wins = data.get('wins')
        createTime = data.get('createTime')
        kickReason = data.get('kickReason')
        if None in [type,
         team,
         wins,
         createTime,
         kickReason]:
            return
        else:
            iconId = self._getIconId(type)
            description = self._makeDescriptionString(data, showBattlesCount=False)
            opponents = self._getOpponentsString(data.get('opponents', {}))
            if message.createdAt is not None:
                fCreateTime = message.createdAt.strftime('%c')
            else:
                LOG_WARNING('Invalid value of created_at = None')
                import time
                fCreateTime = getLongDatetimeFormat(time.time())
            playerTeamWins = wins[team]
            otherTeamWins = wins[2 if team == 1 else 1]
            winsLimit = data.get('winsLimit')
            if winsLimit > 0 and playerTeamWins < winsLimit and otherTeamWins < winsLimit:
                winner = None
            elif playerTeamWins == otherTeamWins:
                winner = 0
            else:
                winner = 1 if wins[1] > wins[2] else 2
            battleResult = self._makeBattleResultString(kickReason, winner, team)
            total = ''
            if data.get('battlesLimit', 0) > 1:
                total = '({0:d}:{1:d})'.format(wins[1], wins[2])
            return g_settings.getHtmlTemplate('prebattleDestruction') % (iconId,
             description,
             fCreateTime,
             opponents,
             battleResult,
             total)


class VehCamouflageTimedOutFormatter(ServiceChannelFormatter):

    def notify(self):
        return True

    def format(self, message):
        data = message.data
        formatted = None
        vehTypeCompDescr = data.get('vehTypeCompDescr')
        if vehTypeCompDescr is not None:
            vType = getVehicleType(vehTypeCompDescr)
            if vType is not None:
                formatted = g_settings.getHtmlTemplate('vehCamouflageTimedOut') % vType.userString
        return formatted


class ClientSysMessageFormatter(ServiceChannelFormatter):
    __templateKey = '%sSysMessage'

    def format(self, data, auxData):
        type = auxData[0]
        templateKey = self.__templateKey % type
        template = g_settings.getHtmlTemplate(templateKey)
        result = None
        if template != templateKey:
            result = template % data
        else:
            LOG_ERROR('Not found template:', templateKey, type)
        return result


class PremiumAccountExpiryFormatter(ServiceChannelFormatter):

    def format(self, data, auxData):
        template = g_settings.getHtmlTemplate('durationOfPremiumAccounExpires')
        return template % getLongDatetimeFormat(data)


class AOGASNotifyFormatter(ServiceChannelFormatter):

    def format(self, data, auxData):
        data = i18n.makeString('#AOGAS:%s' % data.name())
        return g_settings.getHtmlTemplate('AOGASNotify') % data


class VehicleTypeLockExpired(ServiceChannelFormatter):

    def format(self, message):
        if message.data:
            vehTypeCompDescr = message.data.get('vehTypeCompDescr')
            if vehTypeCompDescr is None:
                return g_settings.getHtmlTemplate('vehiclesAllLockExpired')
            else:
                vehDescr = getVehicleType(vehTypeCompDescr).userString
                return g_settings.getHtmlTemplate('vehicleLockExpired') % (vehDescr,)
        else:
            return
        return
