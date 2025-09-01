# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/battle/ammunition_panel/prebattle_ammunition_panel_view.py
from comp7_core.gui.shared.tooltips.comp7_core_tooltips import getRoleEquipmentTooltipParts
from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel_view import PrebattleAmmunitionPanelView, _R_SIMPLE_TOOLTIPS
from gui.impl.pub import SimpleToolTipWindow

class Comp7CorePrebattleAmmunitionPanelView(PrebattleAmmunitionPanelView):
    __slots__ = ()

    @property
    def _modeController(self):
        raise NotImplementedError

    def createToolTip(self, event):
        if event.contentID in _R_SIMPLE_TOOLTIPS:
            window = SimpleToolTipWindow(event, self.getParentWindow())
            if window is not None:
                window.load()
                window.move(event.mouse.positionX, event.mouse.positionY)
                return window
        return super(Comp7CorePrebattleAmmunitionPanelView, self).createToolTip(event)

    def updateViewVehicle(self, vehicle, fullUpdate=True):
        super(Comp7CorePrebattleAmmunitionPanelView, self).updateViewVehicle(vehicle, fullUpdate)
        roleSkill, body = getRoleEquipmentTooltipParts(vehicle, self._modeController)
        if not roleSkill:
            return
        with self.viewModel.transaction() as tx:
            tx.roleSkillSlot.setRoleSkill(roleSkill.name)
            tx.roleSkillSlot.setTooltipHeader(roleSkill.userString)
            tx.roleSkillSlot.setTooltipBody(body or '')
