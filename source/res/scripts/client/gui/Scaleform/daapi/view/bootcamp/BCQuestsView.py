# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCQuestsView.py
from gui.Scaleform.daapi.view.meta.BCQuestsViewMeta import BCQuestsViewMeta
from bootcamp.Bootcamp import g_bootcamp
from gui.shared.formatters.time_formatters import getTimeLeftInfo
from helpers.i18n import makeString
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class BCQuestsView(BCQuestsViewMeta):

    def __init__(self, ctx=None):
        super(BCQuestsView, self).__init__()

    def onCloseClicked(self):
        self.destroy()

    def _populate(self):
        super(BCQuestsView, self)._populate()
        bonuses = g_bootcamp.getBonuses()['battle'][g_bootcamp.getLessonNum()]
        timeKey, time = getTimeLeftInfo(bonuses.get('premium', 0) * 3600)
        voData = {'premiumText': time + ' ' + makeString('#menu:header/account/premium/%s' % timeKey),
         'goldText': str(bonuses['gold']),
         'showRewards': bonuses['showRewards'],
         'goldIcon': RES_ICONS.MAPS_ICONS_BOOTCAMP_REWARDS_BCGOLD,
         'premiumIcon': RES_ICONS.MAPS_ICONS_BOOTCAMP_REWARDS_BCPREMIUM3D}
        self.as_setDataS(voData)
