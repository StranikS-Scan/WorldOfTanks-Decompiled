# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/BoosterInfoWindow.py
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.meta.BoosterInfoMeta import BoosterInfoMeta
from gui.Scaleform.framework.entities.View import View
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.goodies import IGoodiesCache

class BoosterInfoWindow(BoosterInfoMeta):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, ctx=None):
        super(BoosterInfoWindow, self).__init__()
        self.boosterID = ctx.get('boosterID')

    def onCancelClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(View, self)._populate()
        booster = self.goodiesCache.getBooster(self.boosterID)
        self.as_setBoosterInfoS({'windowTitle': _ms(MENU.BOOSTERS_COMMON_NAME),
         'name': booster.userName,
         'icon': booster.icon,
         'parameters': [{'value': booster.getFormattedValue(),
                         'type': '{}\n'.format(_ms(MENU.BOOSTERS_COMMON_EFFECT_VALUE))}, {'value': booster.getEffectTimeStr(hoursOnly=True),
                         'type': _ms(MENU.BOOSTERS_COMMON_EFFECT_TIME)}]})
