# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/data_wrapper/stronghold_event.py
from collections import namedtuple
from gui.clans.data_wrapper.utils import FieldsCheckerMixin, fmtUnavailableValue
from shared_utils import makeTupleByDict
_StrongholdEventClanInfoData = namedtuple('_StrongholdEventClanInfoData', ['primetime_start', 'primetime_end'])
_StrongholdEventClanInfoData.__new__.__defaults__ = (0, 0)

class StrongholdEventClanInfoData(_StrongholdEventClanInfoData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('primetime_start',))
    def getPrimeTimeStart(self):
        return self.primetime_start

    @fmtUnavailableValue(fields=('primetime_end',))
    def getPrimeTimeEnd(self):
        return self.primetime_end


_StrongholdEventConfig = namedtuple('_StrongholdEventConfig', ['name',
 'vehicle_levels',
 'primetimes',
 'set_primetimes_roles',
 'reset_authority_role',
 'min_destroy_vehicle_for_victory',
 'min_destroy_vehicle_for_defeat',
 'visible_start_date',
 'event_start_date',
 'visible_end_date',
 'event_end_date',
 'show_top_medal',
 'unfreeze_vehicle_roles'])
_StrongholdEventConfig.__new__.__defaults__ = ('',
 [],
 [],
 '',
 '',
 0,
 0,
 0,
 0,
 0,
 0,
 False,
 [])

class StrongholdEventConfig(_StrongholdEventConfig, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('event_start_date',))
    def getStartDate(self):
        return self.event_start_date

    @fmtUnavailableValue(fields=('event_end_date',))
    def getEndDate(self):
        return self.event_end_date

    @fmtUnavailableValue(fields=('unfreeze_vehicle_roles',))
    def getUnfreezeVehicleRoles(self):
        return self.unfreeze_vehicle_roles


_StrongholdEventSettingsData = namedtuple('_StrongholdEventClanInfoData', ['event_config'])
_StrongholdEventSettingsData.__new__.__defaults__ = (None,)

class StrongholdEventSettingsData(_StrongholdEventSettingsData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('event_config',))
    def getEventConfig(self):
        return makeTupleByDict(StrongholdEventConfig, self.event_config)

    def getVisibleStartDate(self):
        return self.getEventConfig().getStartDate()

    def getVisibleEndDate(self):
        return self.getEventConfig().getEndDate()
