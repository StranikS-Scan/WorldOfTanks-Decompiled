# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/visual_script_ext/wt_sound_notifications_context.py
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE
from visual_script.context import vse_func_call, vse_get_property
from visual_script_client.contexts.sound_notifications_context import SoundNotificationsContext
from cgf_components import wt_helpers
from constants import IS_CLIENT
import random
if IS_CLIENT:
    from cgf_components.wt_sounds_manager import getAllSwitches as getWtSwitches

class WTSoundNotificationsContext(SoundNotificationsContext):

    @vse_get_property(SLOT_TYPE.INT, display_name='GetHuntersCount', description='Returns amount of alive hunters', aspects=[ASPECT.CLIENT])
    def getHuntersCount(self):
        return wt_helpers.getHuntersCount()

    @vse_get_property(SLOT_TYPE.FLOAT, display_name='GetPlayerVehicleHealthPercent', description='Returns player vehicle health percent', aspects=[ASPECT.CLIENT])
    def getPlayerVehicleHealthPercent(self):
        return wt_helpers.getPlayerVehicleHealthPercent()

    @vse_get_property(SLOT_TYPE.INT, display_name='GetPlayerLives', description='Returns player lives', aspects=[ASPECT.CLIENT])
    def getPlayerLives(self):
        return wt_helpers.getPlayerLives()

    @vse_get_property(SLOT_TYPE.FLOAT, display_name='GetBossVehicleHealthPercent', description='Returns boss vehicle health percent', aspects=[ASPECT.CLIENT])
    def getBossVehicleHealthPercent(self):
        return wt_helpers.getBossVehicleHealthPercent()

    @vse_get_property(SLOT_TYPE.FLOAT, display_name='GetBattleTimeLeft', description='Returns battle left time', aspects=[ASPECT.CLIENT])
    def getBattleTimeLeft(self):
        return wt_helpers.getBattleTimeLeft()

    @vse_get_property(SLOT_TYPE.INT, display_name='GetDestroyedGeneratorsCount', description='Returns destroyed generator count', aspects=[ASPECT.CLIENT])
    def getDestroyedGeneratorsCount(self):
        return wt_helpers.getDestroyedGeneratorsCount()

    @vse_get_property(SLOT_TYPE.INT, display_name='GetCampCount', description='Returns max camp index', aspects=[ASPECT.CLIENT])
    def getCampCount(self):
        return wt_helpers.getCampCount()

    @vse_get_property(SLOT_TYPE.BOOL, display_name='GetKilledByBoss', description='For destroyed vehicle returns True if killer is boss', aspects=[ASPECT.CLIENT])
    def getKilledByBoss(self):
        return wt_helpers.getKilledByBoss()

    @vse_get_property(SLOT_TYPE.BOOL, display_name='GetIsBoss', description='Returns True if player is boss', aspects=[ASPECT.CLIENT])
    def isBoss(self):
        return wt_helpers.isBoss()

    @vse_get_property(SLOT_TYPE.BOOL, display_name='GetHasDebuff', description='Returns True if boss have debuff', aspects=[ASPECT.CLIENT])
    def getHasDebuff(self):
        return wt_helpers.getHasDebuff()

    @vse_get_property(SLOT_TYPE.INT, display_name='GetTotalPlayerDamage', description='Returns damage caused by player', aspects=[ASPECT.CLIENT])
    def getTotalPlayerDamage(self):
        return wt_helpers.getTotalPlayerDamage()

    @vse_func_call(SLOT_TYPE.SOUND, (SLOT_TYPE.SOUND,), display_name='SetEventSwitches', description='Sets event switches if needed', aspects=[ASPECT.CLIENT])
    def setEventSwitches(self, sound):
        if wt_helpers.isEventBattle():
            for name, value in getWtSwitches().iteritems():
                sound.setSwitch(name, value)

        return sound

    @vse_func_call(SLOT_TYPE.STR, (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetEventInfoString', description='Returns Event info from sound_notifications.xml by eventName', aspects=[ASPECT.CLIENT])
    def getEventInfoString(self, eventName, parameter):
        value = ''
        soundNotifications = self.getSoundNotifications()
        if soundNotifications:
            value = soundNotifications.getEventInfo(eventName, parameter)
            array = value.split()
            if len(array) > 1:
                value = random.choice(array)
        return value
