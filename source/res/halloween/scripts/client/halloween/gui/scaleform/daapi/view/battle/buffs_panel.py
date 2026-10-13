# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/buffs_panel.py
from __future__ import absolute_import
import BigWorld
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import TOOLTIP_FORMAT
from gui.impl.gen import R
from gui.impl import backport
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from helpers import dependency
from HWBuffPanelComponent import HWBuffPanelComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from halloween.gui.scaleform.daapi.view.battle.anomalies_utils import anomalyHeader, anomalyBody
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from halloween.gui.scaleform.daapi.view.meta.BuffsPanelMeta import BuffsPanelMeta

def findBuffsPanelComponents():
    player = BigWorld.player()
    if not player:
        return []
    vehicle = BigWorld.entities.get(player.playerVehicleID)
    if not vehicle:
        return []
    return [ c for c in vehicle.dynamicComponents.values() if isinstance(c, HWBuffPanelComponent) ]


class BuffsPanel(BuffsPanelMeta):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    hwAnomaliesCtrl = dependency.descriptor(IHalloweenAnomaliesController)
    ICONS_PATH = R.images.halloween.gui.maps.icons.anomalies.s_36x36

    def __init__(self):
        super(BuffsPanel, self).__init__()
        self._buffs = set()
        self._buffsState = {}

    def _populate(self):
        super(BuffsPanel, self)._populate()
        hwBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onApplyBuff += self.__handleBuffApply
            hwBattleGuiCtrl.onUnapplyBuff += self.__handleBuffUnApply
            hwBattleGuiCtrl.onBuffStateChanged += self.__handleBuffStateChanged
        g_playerEvents.onAvatarReady += self.__onAvatarReady

    def _dispose(self):
        hwBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onApplyBuff -= self.__handleBuffApply
            hwBattleGuiCtrl.onUnapplyBuff -= self.__handleBuffUnApply
            hwBattleGuiCtrl.onBuffStateChanged -= self.__handleBuffStateChanged
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self._buffs.clear()
        super(BuffsPanel, self)._dispose()

    def __init(self):
        buffComponents = findBuffsPanelComponents()
        for component in buffComponents:
            self.__addBuffToPanel(component.buffKey)

    def __onAvatarReady(self):
        self.__init()

    def __handleBuffUnApply(self, ctx):
        buff = ctx['buffKey']
        if buff in self._buffs:
            self.as_removeBuffSlotS(buff)
            self._buffs.remove(buff)

    def __addBuffToPanel(self, buffKey):
        if buffKey in self._buffs:
            return
        headerText = anomalyHeader(buffKey)
        bodyText = anomalyBody(buffKey)
        tooltip = TOOLTIP_FORMAT.format(headerText, bodyText)
        iconRes = self.ICONS_PATH.dyn(buffKey)
        icon = backport.image(iconRes()) if iconRes.exists() else ''
        self._buffs.add(buffKey)
        self.as_addBuffSlotS(buffKey, icon, tooltip)
        if buffKey in self._buffsState:
            self.as_setBuffEnabledS(buffKey, self._buffsState[buffKey])

    def __handleBuffApply(self, ctx):
        self.__addBuffToPanel(ctx['buffKey'])

    def __handleBuffStateChanged(self, ctx):
        buff = ctx['buffKey']
        state = ctx['isActive']
        self._buffsState[buff] = state
        self.as_setBuffEnabledS(buff, state)
