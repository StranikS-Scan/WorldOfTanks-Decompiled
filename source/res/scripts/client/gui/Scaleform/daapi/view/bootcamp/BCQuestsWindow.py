# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCQuestsWindow.py
from gui.Scaleform.daapi.view.meta.BCQuestsWindowMeta import BCQuestsWindowMeta
from debug_utils import LOG_DEBUG
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.BootcampGarage import g_bootcampGarage

class BCQuestsWindow(BCQuestsWindowMeta):

    def __init__(self, ctx=None):
        super(BCQuestsWindow, self).__init__()

    def _populate(self):
        super(BCQuestsWindow, self)._populate()
        bonuses = g_bootcamp.getBonuses()['battle'][g_bootcamp.getLessonNum()]
        bonuses['premium_text'] = self.getPremiumTimeString(bonuses.get('premium', 0) * 3600)
        self.as_setDataS(bonuses)
        g_bootcampGarage.runViewAlias('hangar')

    def getPremiumTimeString(self, timeInSeconds):
        import math
        from helpers import i18n, time_utils
        if timeInSeconds > time_utils.ONE_DAY:
            time = math.ceil(timeInSeconds / time_utils.ONE_DAY)
            timeMetric = i18n.makeString('#menu:header/account/premium/days')
        else:
            time = math.ceil(timeInSeconds / time_utils.ONE_HOUR)
            timeMetric = i18n.makeString('#menu:header/account/premium/hours')
        return str(int(time)) + ' ' + timeMetric

    def _dispose(self):
        super(BCQuestsWindow, self)._dispose()

    def onCloseClicked(self):
        self.destroy()
        from bootcamp.BootcampGarage import g_bootcampGarage
        g_bootcampGarage.runViewAlias('hangar')
