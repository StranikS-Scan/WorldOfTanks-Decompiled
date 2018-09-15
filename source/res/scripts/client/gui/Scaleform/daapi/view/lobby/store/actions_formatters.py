# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/actions_formatters.py
from operator import methodcaller
from gui.Scaleform.daapi.view.lobby.store.action_composer import ActionComposer
from gui.Scaleform.daapi.view.lobby.store.actions_helpers import getActionInfoData, getAnnouncedActionInfo
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events.settings import visitEventGUI
from helpers import i18n
from shared_utils import findFirst
__LOWER_BETTER_STEPS = ('set_EconomicsPrices', 'mul_EconomicsPrices', 'mul_GoodiePrice', 'mul_GoodiePriceAll', 'set_GoodiePrice', 'mul_CamouflagePriceFactor', 'mul_EmblemPriceFactorByGroups', 'mul_EquipmentPrice', 'mul_EquipmentPriceAll', 'set_EquipmentPrice', 'mul_HornPrice', 'mul_HornPriceAll', 'set_HornPrice', 'mul_OptionalDevicePrice', 'mul_OptionalDevicePriceAll', 'set_OptionalDevicePrice', 'cond_ShellGoldPrice', 'mul_ShellPrice', 'mul_ShellPriceAll', 'mul_ShellPriceNation', 'set_ShellPrice', 'cond_VehPrice', 'mul_VehPrice', 'mul_VehPriceAll', 'mul_VehPriceNation', 'set_VehPrice', 'cond_VehRentPrice', 'mul_VehRentPrice', 'mul_VehRentPriceAll', 'mul_VehRentPriceNation')
__MORE_BETTER_STEPS = ('set_EconomicsParams', 'mul_EconomicsParams')
_INTERSECTED_ACTIONS_LIST = __LOWER_BETTER_STEPS + __MORE_BETTER_STEPS

class ACTIONS_SIZE(object):
    HERO = 'hero'
    NORMAL = 'normal'
    SMALL = 'small'
    COMING_SOON = 'coming_soon'


class _ACTIONS_PRIORITY_LEVEL(object):
    PRIORITY_1 = 1
    PRIORITY_2 = 2
    PRIORITY_3 = 3
    PRIORITY_4 = 4
    ALL_VISIBLE = (PRIORITY_1, PRIORITY_2, PRIORITY_3)


_pl = _ACTIONS_PRIORITY_LEVEL
_ACTIONS_PRIORITY_MAPPING = {_pl.PRIORITY_1: ACTIONS_SIZE.HERO,
 _pl.PRIORITY_2: ACTIONS_SIZE.NORMAL,
 _pl.PRIORITY_3: ACTIONS_SIZE.SMALL,
 _pl.PRIORITY_4: ACTIONS_SIZE.COMING_SOON}

class _VISIBLE_CARDS(object):
    ACTIONS = 'actions'
    ANNOUNCED = 'announced'


class _LAYOUT_TEMPLATE_FIELDS(object):
    TITLE = 'title'
    CARDS = 'cards'
    HEROCARD = 'heroCard'
    COLUMNLEFT = 'columnLeft'
    COLUMNRIGHT = 'columnRight'
    COMINGSOON = 'comingSoon'
    EMPTY = 'empty'
    INFO = 'info'
    BTNLABEL = 'btnLabel'


_ltf = _LAYOUT_TEMPLATE_FIELDS

def _dumpLayoutSkeleton():
    return {_ltf.TITLE: MENU.STORETAB_ACTIONS,
     _ltf.CARDS: {_ltf.HEROCARD: None,
                  _ltf.COLUMNLEFT: None,
                  _ltf.COLUMNRIGHT: None,
                  _ltf.COMINGSOON: None},
     _ltf.EMPTY: {_ltf.INFO: i18n.makeString(QUESTS.ACTION_EMPTY_INFO),
                  _ltf.BTNLABEL: i18n.makeString(QUESTS.ACTION_EMPTY_BTNLABEL)}}


_FORMATTABLE_FIELDS = (_ltf.HEROCARD,
 _ltf.COLUMNLEFT,
 _ltf.COLUMNRIGHT,
 _ltf.COMINGSOON)

class ActionCardFormatter(object):
    __slots__ = ('discount',)

    def __init__(self):
        self.discount = None
        super(ActionCardFormatter, self).__init__()
        return

    def format(self, discount):
        """Format action cards for view
        :param discount:
        :return: packed vo's
        """
        self.discount = discount
        result = self._packGui()
        self.discount = None
        return result

    def _packGui(self):
        assert self.discount
        data = {'id': self.discount.getID(),
         'title': self.discount.getTitle(),
         'time': self.discount.getActionTime(),
         'header': self._getHeaderData(),
         'isNew': self.discount.getIsNew(),
         'picture': self.discount.getPicture(),
         'tooltipInfo': self.discount.getTooltipInfo(),
         'discount': self.discount.getDiscount(),
         'battleQuestsInfo': self.discount.getBattleQuestsInfo(),
         'linkBtnLabel': self.discount.getLinkBtnLabel(),
         'actionBtnLabel': self.discount.getActionBtnLabel(),
         'storeItemDescr': self._getTableData(),
         'triggerChainID': self.discount.getTriggerChainID()}
        data.update(self._getExtras())
        return data

    def _getHeaderData(self):
        assert self.discount
        return self.discount.getAutoDescription(useBigIco=True)

    def _getTableData(self):
        assert self.discount
        return {'descr': self._getDescription(),
         'tableOffers': self.discount.getTableData()}

    def _getExtras(self):
        return {}

    def _getDescription(self):
        return self.discount.getAdditionalDescription(useBigIco=False)


class HeroCardFormatter(ActionCardFormatter):

    def _getExtras(self, *args, **kwargs):
        return {'linkage': STORE_CONSTANTS.ACTION_CARD_HERO_LINKAGE}

    def _getDescription(self):
        return self.discount.getAdditionalDescription(useBigIco=False, forHeroCard=True)


class NormalCardFormatter(ActionCardFormatter):

    def _getExtras(self, *args, **kwargs):
        return {'linkage': STORE_CONSTANTS.ACTION_CARD_NORMAL_LINKAGE}


class SmallCardFormatter(ActionCardFormatter):

    def _getHeaderData(self):
        assert self.discount
        return self.discount.getAutoDescription(useBigIco=False)

    def _getExtras(self, *args, **kwargs):
        return {'linkage': STORE_CONSTANTS.ACTION_CARD_SMALL_LINKAGE}


class ComingSoonCardFormatter(ActionCardFormatter):

    def _getHeaderData(self):
        assert self.discount
        return self.discount.getComingSoonDescription()

    def _getExtras(self, *args, **kwargs):
        return {'linkage': STORE_CONSTANTS.ACTION_COMING_SOON_LINKAGE}


class ActionsBuilder(object):

    def __init__(self):
        super(ActionsBuilder, self).__init__()
        self.__formatters = {ACTIONS_SIZE.HERO: HeroCardFormatter(),
         ACTIONS_SIZE.NORMAL: NormalCardFormatter(),
         ACTIONS_SIZE.SMALL: SmallCardFormatter(),
         ACTIONS_SIZE.COMING_SOON: ComingSoonCardFormatter()}
        self.__visibleCards = {_VISIBLE_CARDS.ACTIONS: [],
         _VISIBLE_CARDS.ANNOUNCED: []}

    @classmethod
    def getAllVisibleDiscounts(cls, actions, entities, announced, sorting=False):
        """
        :param actions: actions list from server
        :param entities: dict
            {'actionsEntities': (index from 'actions', index from 'step', intersected actions (bool)),
             'actions': (list of active actions),
             'steps': (list of active steps),
            }
        :param announced: future actions
        :param sorting: if vlaue equals True than each list of discounts should be sorted,
            otherwise - don't sort list of discounts. For example, if number of discount is needed
            only, sorting is pointless.
        :return: dict of actions for view
        """
        visibleCards = cls._getAllVisibleDiscounts(actions, entities, announced)
        if sorting:
            visibleCards[_VISIBLE_CARDS.ACTIONS] = sorted(visibleCards[_VISIBLE_CARDS.ACTIONS], key=methodcaller('getFinishTime'))
            visibleCards[_VISIBLE_CARDS.ANNOUNCED] = sorted(visibleCards[_VISIBLE_CARDS.ANNOUNCED], key=methodcaller('getStartTime'))
        return visibleCards

    def createLayoutTemplate(self, allCards):
        """Create template layout sorted by priority and view position
        :param allCards: All action for view
        :return: dict _LAYOUT_TEMPLATE
        """
        template = _dumpLayoutSkeleton()
        cards = template[_ltf.CARDS]
        actionCards = allCards[_VISIBLE_CARDS.ACTIONS]
        futureCards = allCards[_VISIBLE_CARDS.ANNOUNCED]
        if futureCards:
            cards[_ltf.COMINGSOON] = [futureCards[0]]
        if len(actionCards) == 1:
            actionCards[0].visualPriority = _pl.PRIORITY_1
            cards[_ltf.HEROCARD] = actionCards
            return template
        if len(actionCards) == 2:
            actionCards[0].visualPriority = _pl.PRIORITY_2
            actionCards[1].visualPriority = _pl.PRIORITY_2
            cards[_ltf.COLUMNLEFT] = [actionCards[0]]
            cards[_ltf.COLUMNRIGHT] = [actionCards[1]]
            return template
        priorities = {k:[] for k in _ACTIONS_PRIORITY_MAPPING}
        for item in actionCards:
            if item.visualPriority in priorities:
                priorities[item.visualPriority].append(item)

        priority1 = priorities[_pl.PRIORITY_1]
        priority2 = priorities[_pl.PRIORITY_2]
        priority3 = priorities[_pl.PRIORITY_3]
        if len(priority1) > 1:
            priority2 = priority1[1:] + priority2[:]
            priority1 = [priority1[0]]
        if not priority3 and len(priority2) % 2 != 0:
            priority3 = priority2[-2:]
            priority2 = priority2[:-2]
        elif not priority2 and len(priority3) % 2 != 0:
            priority2 = [priority3[0]]
            priority3 = priority3[1:]
        elif len(priority2) % 2 != 0 and len(priority3) % 2 != 0:
            priority2.append(priority3[0])
            priority3 = priority3[1:]
        elif len(priority2) % 2 == 0 and len(priority3) % 2 != 0:
            priority3 = [priority2[-1]] + priority3[:]
            priority2 = priority2[:-1]
        priority1 = self.__setVisualPriority(priority1, _pl.PRIORITY_1)
        priority2 = self.__setVisualPriority(priority2, _pl.PRIORITY_2)
        priority3 = self.__setVisualPriority(priority3, _pl.PRIORITY_3)
        cards[_ltf.HEROCARD] = priority1
        cards[_ltf.COLUMNLEFT] = priority2[::2]
        cards[_ltf.COLUMNRIGHT] = priority2[1::2]
        if len(priority2) % 2 != 0:
            cards[_ltf.COLUMNRIGHT].extend(priority3[:2])
            priority3 = priority3[2:]
        cards[_ltf.COLUMNLEFT].extend(priority3[::2])
        cards[_ltf.COLUMNRIGHT].extend(priority3[1::2])
        return template

    def getSuitableFormatter(self, discount):
        priority = discount.visualPriority
        return self.__formatters[_ACTIONS_PRIORITY_MAPPING[priority]] if priority in _ACTIONS_PRIORITY_MAPPING else None

    def format(self, actions, entities, announced):
        self.__visibleCards = self.getAllVisibleDiscounts(actions, entities, announced)
        template = self.createLayoutTemplate(self.__visibleCards)
        cards = template[_ltf.CARDS]
        for field in _FORMATTABLE_FIELDS:
            discounts = cards[field]
            result = []
            if discounts:
                for discount in discounts:
                    formatter = self.getSuitableFormatter(discount)
                    if formatter:
                        result.append(formatter.format(discount))

            cards[field] = result or None

        if cards[_ltf.HEROCARD]:
            cards[_ltf.HEROCARD] = cards[_ltf.HEROCARD][0]
        if cards[_ltf.COMINGSOON]:
            cards[_ltf.COMINGSOON] = cards[_ltf.COMINGSOON][0]
        if not any(cards.values()):
            template[_ltf.CARDS] = None
        return template

    def markVisited(self, actionID):
        cards = self.__visibleCards[_VISIBLE_CARDS.ACTIONS]
        visitedCard = findFirst(lambda x: x.getID() == actionID, cards)
        if visitedCard:
            visitEventGUI(visitedCard)

    @classmethod
    def _getAllVisibleDiscounts(cls, actions, entities, announced):
        """
        :param actions: actions list from server
        :param entities: dict
            {'actionsEntities': (index from 'actions', index from 'step', intersected actions (bool)),
             'actions': (list of active actions),
             'steps': (list of active steps),
            }
        :param announced: future actions
        :return: dict of actions for view
        """
        composer = ActionComposer()
        visibleCards = {_VISIBLE_CARDS.ACTIONS: [],
         _VISIBLE_CARDS.ANNOUNCED: []}
        if actions:
            affectedActions = set()
            actionEntities = entities.get('actionEntities', None)
            actionNames = entities.get('actions', None)
            actionSteps = entities.get('steps', None)
            if actionEntities and actionNames and actionSteps:
                for name, step, _ in actionEntities.values():
                    affectedActions.add((actionNames[name], actionSteps[step]))

            for action in actions:
                for actionInfo in getActionInfoData(action):
                    if actionInfo.visualPriority not in _ACTIONS_PRIORITY_LEVEL.ALL_VISIBLE:
                        continue
                    aiName = actionInfo.event.getID()
                    aiStep = actionInfo.discount.getName()
                    if not actionInfo.isDiscountVisible():
                        continue
                    if aiStep in _INTERSECTED_ACTIONS_LIST:
                        if (aiName, aiStep) in affectedActions:
                            composer.add(actionInfo)
                    composer.add(actionInfo)

        visibleCards[_VISIBLE_CARDS.ACTIONS] = composer.getActions()
        for announce in announced:
            infoList = getAnnouncedActionInfo(announce)
            if infoList:
                visibleCards[_VISIBLE_CARDS.ANNOUNCED].append(infoList)

        return visibleCards

    def __setVisualPriority(self, items, priority):
        """Set new visual priority according template rules"""
        for item in items:
            item.visualPriority = priority

        return items
