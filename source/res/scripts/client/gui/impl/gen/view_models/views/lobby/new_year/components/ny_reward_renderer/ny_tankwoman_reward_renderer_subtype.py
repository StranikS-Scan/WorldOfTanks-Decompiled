# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_reward_renderer/ny_tankwoman_reward_renderer_subtype.py
from frameworks.wulf import ViewModel

class NyTankwomanRewardRendererSubtype(ViewModel):
    __slots__ = ()
    SUBTYPE_TANKWOMAN = 'tankwoman'
    SUBTYPE_TALISMAN = 'freeTalisman'
    STATE_LOCKED = 'locked'
    STATE_OPENED = 'opened'
    STATE_RECEIVED = 'received'

    def __init__(self, properties=0, commands=0):
        super(NyTankwomanRewardRendererSubtype, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NyTankwomanRewardRendererSubtype, self)._initialize()
