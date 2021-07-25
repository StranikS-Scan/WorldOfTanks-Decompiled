# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/role_description.py
import typing
from constants import ROLE_TYPE_TO_LABEL, ACTION_TYPE_TO_LABEL, ARENA_PERIOD
from items.vehicles import getActionsByRole
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.Scaleform.daapi.view.meta.RoleDescriptionMeta import RoleDescriptionMeta
from gui.Scaleform.daapi.view.battle.shared.hint_panel.plugins import RoleHelpPlugin
_ROLE_HTML_TEMPLATE = 'html_templates:vehicleRoles/roleDescription'
if typing.TYPE_CHECKING:
    from typing import Dict
    from items.vehicles import VehicleDescriptor

class RoleDescription(RoleDescriptionMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RoleDescription, self).__init__()
        self.__isActive = False

    def _populate(self):
        super(RoleDescription, self)._populate()
        vehicle = self.__sessionProvider.shared.vehicleState.getControllingVehicle()
        typeDescriptor = vehicle.typeDescriptor
        vehicleCD = typeDescriptor.type.compactDescr
        if RoleHelpPlugin.isAvailableInSettings(vehicleCD):
            self.__setData(typeDescriptor)
            self.__addListeners()

    def _dispose(self):
        self.__removeListeners()
        super(RoleDescription, self)._dispose()

    def __addListeners(self):
        g_eventBus.addListener(GameEvent.ROLE_HINT_TOGGLE, self.__handleRoleHintToggled, EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        self.__isActive = True

    def __removeListeners(self):
        if self.__isActive:
            self.__isActive = False
            g_eventBus.removeListener(GameEvent.ROLE_HINT_TOGGLE, self.__handleRoleHintToggled, EVENT_BUS_SCOPE.BATTLE)
            g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange

    def __onArenaPeriodChange(self, period, *_):
        if self.__isActive and period == ARENA_PERIOD.BATTLE:
            self.__hide()

    def __setData(self, typeDescriptor):
        roleId = typeDescriptor.role
        roleName = ROLE_TYPE_TO_LABEL[roleId]
        roleExp = R.strings.menu.roleExp
        roleStr = backport.text(roleExp.roleGroupName.dyn(roleName, '')())
        classWithRole = backport.text(roleExp.roleName.dyn(roleName, '')(), groupName=makeHtmlString(_ROLE_HTML_TEMPLATE, 'role', {'role': roleStr}))
        title = makeHtmlString(_ROLE_HTML_TEMPLATE, 'className', {'className': classWithRole})
        actions = getActionsByRole(roleId)
        self.as_setDataS({'roleIcon': backport.image(R.images.gui.maps.icons.roleExp.roles.c_100x100.dyn(roleName, '')()),
         'roleDescription': title,
         'roleActions': [ self.__getRoleActionVO(action) for action in actions ]})

    @staticmethod
    def __getRoleActionVO(action):
        actionLbl = ACTION_TYPE_TO_LABEL[action]
        return {'image': backport.image(R.images.gui.maps.icons.roleExp.actions.c_128x128.dyn(actionLbl, '')()),
         'description': backport.text(R.strings.menu.roleExp.action.dyn(actionLbl, '')())}

    def __hide(self):
        self.__removeListeners()
        self.as_setVisibleS(False)

    def __handleRoleHintToggled(self, event):
        if event.ctx.get('isShown', False):
            self.as_setVisibleS(True)
        else:
            self.__hide()
