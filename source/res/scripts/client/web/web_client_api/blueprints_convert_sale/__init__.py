# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/blueprints_convert_sale/__init__.py
import BigWorld
from gui.shared.gui_items.processors.blueprints_convert_sale import ProcessExchangeBlueprintsProcessor
from nations import NAMES as NATION_NAMES
from helpers import dependency
from gui.server_events.bonuses import getNonQuestBonuses, VehicleBlueprintBonus
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2c, w2capi, W2CSchema, Field
_MAX_VISIBLE_NATION_ICONS = 2
_BCS_ACTION_POSTFIX = '_BCS'

def wrap(data):
    result = {}
    for optionType, optionTypeItems in data.iteritems():
        typeBonuses = {}
        for optionID, optionItems in optionTypeItems.iteritems():
            optionItemsList = []
            items, limit = optionItems
            for itemName, itemValue in items.iteritems():
                optionItemsList.extend(getNonQuestBonuses(itemName, itemValue))

            typeBonuses[optionID] = {'items': optionItemsList,
             'limit': limit}

        result[optionType] = typeBonuses

    return result


class _GetOfferByCategorySchema(W2CSchema):
    category = Field(required=True, type=basestring)


class _ExchangeBlueprintSchema(W2CSchema):
    offerID = Field(required=True, type=int)
    count = Field(required=False, type=int)


@w2capi(name='blueprints_convert_sale', key='action')
class BlueprintsConvertSaleWebApi(object):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)

    @w2c(W2CSchema, 'get_blueprint_exchange_categories')
    def getBlueprintExchangeCategories(self, _):
        config = self._lobbyContext.getServerSettings().getBlueprintsConvertSaleConfig()
        options = wrap(config.getOptions())
        categories = {}
        for optType, optData in options.iteritems():
            nations = set()
            limit = []
            for _, optItem in optData.iteritems():
                for item in optItem.get('items', []):
                    if isinstance(item, VehicleBlueprintBonus):
                        nations.add(item.getImageCategory())

                limit.append(optItem.get('limit', 0))

            nations = list(nations)
            if len(nations) > _MAX_VISIBLE_NATION_ICONS:
                nations = ['national']
            categories[optType] = {'id': optType,
             'currencies': list(nations),
             'isLQO': any(limit)}

        return categories

    @w2c(_GetOfferByCategorySchema, 'get_blueprint_offer_by_category')
    def getBlueprintOfferByCategory(self, cmd):
        config = self._lobbyContext.getServerSettings().getBlueprintsConvertSaleConfig()
        options = wrap(config.getOptions())
        limits = BigWorld.player().platformBlueprintsConvertSaleLimits
        category = options.get(cmd.category, {})
        result = []
        for optionID, optionData in category.iteritems():
            configLimit = optionData.get('limit', 0)
            if configLimit > 0:
                if optionID in limits:
                    limit = configLimit - limits[optionID]
                else:
                    limit = configLimit
            else:
                limit = -1
            itemDef = {'id': optionID,
             'limit': limit}
            for item in optionData.get('items', []):
                if isinstance(item, VehicleBlueprintBonus):
                    price = str(-item.getValue()[1])
                    nation = item.getImageCategory()
                    itemDef.update({'price': [{'currency': nation,
                                'balance': price}],
                     'nation': nation})
                ebData = item.getWrappedEpicBonusList()
                if ebData:
                    extraData = ebData[-1]['value'] if cmd.category == 'premium' else ebData[-1]['id']
                    itemDef.update({'extraData': extraData})

            result.append(itemDef)

        return result

    @w2c(W2CSchema, 'get_blueprint_balance')
    def getBlueprintBalance(self, _):
        balance = [{'currency': 'intelligence',
          'balance': self._itemsCache.items.blueprints.getIntelligenceData()}]
        fragments = self._itemsCache.items.blueprints.getAllNationalFragmentsData()
        for nameID, value in fragments.iteritems():
            balance.append({'currency': NATION_NAMES[nameID],
             'balance': value})

        return balance

    @w2c(W2CSchema, 'get_blueprint_exchange_end_time')
    def getExchangeEndTime(self, _):
        actions = self._eventsCache.getActions()
        for aName, aData in actions.iteritems():
            if aName.endswith(_BCS_ACTION_POSTFIX):
                milliseconds = round(aData.getFinishTimeLeft(), 3) * 1000
                return int(milliseconds)

    @w2c(_ExchangeBlueprintSchema, 'blueprint_do_exchange')
    def doExchangeBlueprints(self, cmd):
        success, error = False, ''
        offerID = cmd.offerID
        count = cmd.count if hasattr(cmd, 'count') and cmd.count else 1
        processor = ProcessExchangeBlueprintsProcessor(offerID, count)
        response = yield processor.request()
        if response:
            success, error = response.success, response.userMsg
        else:
            error = 'Undefined server error'
        yield {'success': success,
         'error': error}
