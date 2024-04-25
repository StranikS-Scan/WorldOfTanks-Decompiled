# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/role_notification.py
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.Scaleform.daapi.view.meta.HBRoleNotificationMeta import HBRoleNotificationMeta
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from items import vehicles

class HBRoleNotification(HBRoleNotificationMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(HBRoleNotification, self)._populate()
        g_eventBus.addListener(events.HBRoleSkillEvents.UNLOCK_PROGRESS_CHANGED, self.__onRoleSkillProgressChanged, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        g_eventBus.removeListener(events.HBRoleSkillEvents.UNLOCK_PROGRESS_CHANGED, self.__onRoleSkillProgressChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        super(HBRoleNotification, self)._dispose()

    def __onRoleSkillProgressChanged(self, event):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl.isInPostmortem:
            return
        else:
            value = event.ctx.get('value', 0.0)
            if value >= 1:
                roleAbilityId = event.ctx.get('roleAbilityId', 0)
                equipmentsCache = vehicles.g_cache.equipments()
                equipment = equipmentsCache.get(roleAbilityId)
                if equipment is not None:
                    iconName = equipment.icon[0]
                    self.as_showS(backport.image(R.images.historical_battles.gui.maps.icons.artefact.c_104x104.dyn(iconName)()), equipment.userString.upper(), backport.text(R.strings.hb_artefacts.role.unlocked()))
            return
