# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_panel_view.py
from comp7.gui.shared.tooltips.comp7_tooltips import getRoleEquipmentTooltipParts
from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel_view import PrebattleAmmunitionPanelView, _R_SIMPLE_TOOLTIPS
from gui.impl.pub import SimpleToolTipWindow
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7PrebattleAmmunitionPanelView(PrebattleAmmunitionPanelView):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def createToolTip(self, event):
        if event.contentID in _R_SIMPLE_TOOLTIPS:
            window = SimpleToolTipWindow(event, self.getParentWindow())
            if window is not None:
                window.load()
                window.move(event.mouse.positionX, event.mouse.positionY)
                return window
        return super(Comp7PrebattleAmmunitionPanelView, self).createToolTip(event)

    def updateViewVehicle(self, vehicle, fullUpdate=True):
        super(Comp7PrebattleAmmunitionPanelView, self).updateViewVehicle(vehicle, fullUpdate)
        roleSkill, body = getRoleEquipmentTooltipParts(vehicle)
        if not roleSkill:
            return
        with self.viewModel.transaction() as tx:
            tx.roleSkillSlot.setRoleSkill(roleSkill.name)
            tx.roleSkillSlot.setTooltipHeader(roleSkill.userString)
            tx.roleSkillSlot.setTooltipBody(body or '')
