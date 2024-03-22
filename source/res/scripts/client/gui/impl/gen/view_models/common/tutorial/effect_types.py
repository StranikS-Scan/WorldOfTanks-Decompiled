# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/tutorial/effect_types.py
from frameworks.wulf import ViewModel

class EffectTypes(ViewModel):
    __slots__ = ()
    HINT = 'hint'
    DISPLAY = 'display'
    ENABLED = 'enabled'
    OVERLAY = 'overlay'

    def __init__(self, properties=0, commands=0):
        super(EffectTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(EffectTypes, self)._initialize()
