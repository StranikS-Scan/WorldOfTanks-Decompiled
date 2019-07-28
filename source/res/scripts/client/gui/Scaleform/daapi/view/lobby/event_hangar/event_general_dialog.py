# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_hangar/event_general_dialog.py
import math
from gui.Scaleform.daapi.view.meta.EventGeneralDialogMeta import EventGeneralDialogMeta
from gui.Scaleform.daapi import LobbySubView
from helpers import dependency, int2roman
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters.currency import getBWFormatter
from gui.server_events.awards_formatters import AWARDS_SIZES, getEventAwardFormatter
from gui.shared.gui_items.processors import plugins
from gui.shared.money import Money
_MAX_PROGRESS = 100
_EMPTY_BONUS_LABEL = 'x1'

class EventGeneralDialog(LobbySubView, EventGeneralDialogMeta):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, ctx=None, *args, **kwargs):
        super(EventGeneralDialog, self).__init__(*args, **kwargs)
        self._general = self.gameEventController.getGeneral(ctx['generalId'])

    def closeView(self):
        self.destroy()

    def generalBuyLevel(self, level):
        self._general.buy(level)

    def _populate(self):
        super(EventGeneralDialog, self)._populate()
        self._general.onItemsUpdated += self._updateData
        self._updateData()

    def _dispose(self):
        self._general.onItemsUpdated -= self._updateData
        super(EventGeneralDialog, self)._dispose()

    def _updateData(self):
        generalID = self._general.getID()
        generalName = backport.text(R.strings.event.progress.general.num(generalID).name())
        background = backport.image(R.images.gui.maps.icons.event.progress.dyn('specialOfferBg{}'.format(generalID))())
        self.as_setDataS({'header': backport.text(R.strings.event.general_buy_page.header(), generalName=generalName),
         'text': backport.text(R.strings.event.general_buy_page.text(), generalName=generalName),
         'background': background,
         'levels': [ self._getLevelData(level + 1) for level in xrange(self._general.getMaxLevel()) ]})

    def _getLevelData(self, level):
        generalID = self._general.getID()
        generalName = backport.text(R.strings.event.progress.general.num(generalID).name())
        progressItem = None
        if len(self._general.items) >= level:
            progressItem = self._general.items[level]
        isBonusReached = False
        rewards = []
        bonus = []
        if progressItem is not None:
            rewards = self._getRewardsVO(progressItem.getBonuses())
            buyBonusQuest = progressItem.getCorrespondBonusQuest()
            if buyBonusQuest is not None:
                isBonusReached = buyBonusQuest.isCompleted()
                bonus = self._getRewardsVO(buyBonusQuest.getBonuses())
        isReached = progressItem is not None and self._general.items[level].isCompleted()
        if isReached:
            header = backport.text(R.strings.event.general_buy_page.level.reached(), generalName=generalName, level=int2roman(level + 1))
        else:
            header = backport.text(R.strings.event.general_buy_page.level.notReached(), generalName=generalName, level=int2roman(level + 1))
        costCurrency, cost = self._general.getCurrentCostForLevel(level)
        oldCostCurrency, oldCost = self._general.getOldCostForLevel(level)
        buyEnabled = cost is not None and not isBonusReached
        hasDiscount = buyEnabled and cost is not None and oldCost is not None and oldCost > cost
        if hasDiscount:
            discount = int(math.ceil((oldCost - cost) * _MAX_PROGRESS / float(oldCost)))
        else:
            discount = 0
        status = ''
        if isBonusReached:
            status = backport.text(R.strings.event.general_buy_page.level_bought())
        canBuy = not isBonusReached and buyEnabled and plugins.MoneyValidator(Money(**{costCurrency: cost})).validate().success
        return {'header': header,
         'bundleName': backport.text(R.strings.event.general_buy_page.level.num(level).bundleName()),
         'level': level,
         'rewardTaken': isBonusReached,
         'buyEnabled': buyEnabled,
         'canBuy': canBuy,
         'reached': isReached,
         'status': status,
         'discount': '-{}%'.format(discount),
         'cost': self._getCostFormatted(costCurrency, cost),
         'oldCost': self._getCostFormatted(oldCostCurrency, oldCost),
         'hasDiscount': hasDiscount,
         'rewards': rewards,
         'bonus': bonus}

    def _getCostFormatted(self, currency, amount):
        return None if currency is None or amount is None else getBWFormatter(currency)(amount)

    def _getRewardsVO(self, bonuses):
        return [ {'icon': bonus.images[AWARDS_SIZES.SMALL],
         'overlayType': bonus.overlayType.get(AWARDS_SIZES.SMALL, '') if bonus.overlayType else '',
         'label': bonus.label or _EMPTY_BONUS_LABEL,
         'tooltip': bonus.tooltip,
         'specialArgs': bonus.specialArgs,
         'specialAlias': bonus.specialAlias,
         'isSpecial': bonus.isSpecial} for bonus in getEventAwardFormatter().format(bonuses) ]
