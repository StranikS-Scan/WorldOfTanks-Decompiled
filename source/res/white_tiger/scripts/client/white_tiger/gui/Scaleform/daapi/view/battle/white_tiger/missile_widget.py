# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/missile_widget.py
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.ability_widget import IComponentWidgetView
from white_tiger.gui.Scaleform.daapi.view.meta.WTMissileWidgetMeta import WTMissileWidgetMeta

class WhiteTigerMissileWidgetView(WTMissileWidgetMeta, IComponentWidgetView):

    def show(self, useAnim=False):
        self.as_showS(useAnim)

    def hide(self, useAnim=False):
        self.as_hideS(useAnim)

    def update(self, **kwargs):
        if 'distance' in kwargs:
            self.as_setRangeS(kwargs['distance'])
        if 'altitude' in kwargs:
            self.as_setAltitudeS(kwargs['altitude'])
