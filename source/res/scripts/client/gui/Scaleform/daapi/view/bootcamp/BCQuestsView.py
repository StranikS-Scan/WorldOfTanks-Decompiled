# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCQuestsView.py
import logging
from collections import namedtuple
from constants import PREMIUM_ENTITLEMENTS
from bootcamp.Bootcamp import g_bootcamp
from gui.impl import backport
from gui.impl.gen import R
from helpers.i18n import makeString
from helpers.time_utils import ONE_DAY
from gui.shared.formatters.time_formatters import getTimeLeftInfo
from gui.Scaleform.daapi.view.meta.BCQuestsViewMeta import BCQuestsViewMeta
_logger = logging.getLogger(__name__)
_PREMIUM_ICONS = {PREMIUM_ENTITLEMENTS.BASIC: R.images.gui.maps.icons.bootcamp.rewards.bcPremium3d(),
 PREMIUM_ENTITLEMENTS.PLUS: R.images.gui.maps.icons.bootcamp.rewards.bcPremiumPlus3d()}
_PremiumBonus = namedtuple('_PremiumBonus', ('type', 'amount'))

class BCQuestsView(BCQuestsViewMeta):

    def __init__(self, ctx=None):
        super(BCQuestsView, self).__init__()

    def onCloseClicked(self):
        self.destroy()

    def _populate(self):
        super(BCQuestsView, self)._populate()
        bonuses = g_bootcamp.getBonuses()['battle'][g_bootcamp.getLessonNum()]
        premiumBonuses = []
        for premiumType in PREMIUM_ENTITLEMENTS.ALL_TYPES:
            amount = bonuses.get(premiumType, 0)
            if amount != 0:
                premiumBonuses.append(_PremiumBonus(type=premiumType, amount=amount))

        if len(premiumBonuses) != 1:
            _logger.error('Incorrect premium bonuses')
            return
        timeKey, time = getTimeLeftInfo(premiumBonuses[0].amount * ONE_DAY)
        voData = {'premiumText': time + ' ' + makeString('#menu:header/account/premium/%s' % timeKey),
         'goldText': str(bonuses['gold']),
         'showRewards': bonuses['showRewards'],
         'premiumIcon': backport.image(_PREMIUM_ICONS[premiumBonuses[0].type]),
         'goldIcon': backport.image(R.images.gui.maps.icons.bootcamp.rewards.bcGold())}
        self.as_setDataS(voData)
