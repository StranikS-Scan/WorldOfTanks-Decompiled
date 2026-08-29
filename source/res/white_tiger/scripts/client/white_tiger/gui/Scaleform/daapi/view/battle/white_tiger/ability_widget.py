# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/ability_widget.py
from white_tiger.gui.Scaleform.daapi.view.meta.WTAbilityWidgetMeta import WTAbilityWidgetMeta
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_VIEW_ALIASES import WHITE_TIGER_BATTLE_VIEW_ALIASES
from white_tiger_common.wt_constants import WT_COMPONENT_CONSTANTS

class IComponentWidgetView(object):

    def show(self, useAnim):
        raise NotImplementedError

    def hide(self, useAnim):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError


class WhiteTigerAbilityWidgetView(WTAbilityWidgetMeta):

    def extendComponents(self, componentAlias):
        if componentAlias == WHITE_TIGER_BATTLE_VIEW_ALIASES.WT_MISSILE_WIDGET:
            self.as_addMissileWidgetS()
            abilityView = self.components.get(componentAlias)
            if abilityView:
                abilityView.as_setMaxAltitudeS(WT_COMPONENT_CONSTANTS.MISSILE_WIDGET_MAX_ALTITUDE)

    def show(self, abilityAlias, useAnim=False):
        abilityView = self.components.get(abilityAlias)
        if abilityView:
            abilityView.show(useAnim)

    def hide(self, abilityAlias, useAnim=False):
        abilityView = self.components.get(abilityAlias)
        if abilityView:
            abilityView.hide(useAnim)

    def update(self, abilityAlias, **kwargs):
        abilityView = self.components.get(abilityAlias)
        if abilityView:
            abilityView.update(**kwargs)
