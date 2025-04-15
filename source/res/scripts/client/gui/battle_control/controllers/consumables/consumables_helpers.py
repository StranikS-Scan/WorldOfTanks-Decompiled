# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/consumables_helpers.py
from collections import namedtuple
from soft_exception import SoftException
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.battle_control.controllers.consumables import equipment_ctrl
EMPTY_KEY = 'default'
_CtrlTypeData = namedtuple('_CtrlTypeData', ('recording', 'replaying'))
_CtrlTypeData.__new__.__defaults__ = (None,) * len(_CtrlTypeData._fields)

class _CtrlTypeMap(dict):

    def __getitem__(self, key):
        return dict.__getitem__(self, self.__find(key))

    def __setitem__(self, key, value):
        if isinstance(value, _CtrlTypeData):
            dict.__setitem__(self, key, value)
        else:
            raise TypeError('Value should be ctrlTypeData. ')

    def extend(self, **kwargs):
        if kwargs:
            key = kwargs.get('bonusType', EMPTY_KEY)
            if key not in self:
                self[key] = _CtrlTypeData(*kwargs.get('controllers', ()))
            else:
                raise SoftException('CtrlMap already has key {key}. '.format(key=key))

    def __find(self, key):
        return next((k for k in self.iterkeys() if ARENA_BONUS_TYPE_CAPS.checkAny(key, k)), EMPTY_KEY) if key not in self else key


g_equipmentCtrlMap = _CtrlTypeMap({EMPTY_KEY: _CtrlTypeData(equipment_ctrl.EquipmentsController, equipment_ctrl.EquipmentsReplayPlayer)})
