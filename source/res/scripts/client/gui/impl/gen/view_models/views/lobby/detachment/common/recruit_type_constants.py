# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/recruit_type_constants.py
from frameworks.wulf import ViewModel

class RecruitTypeConstants(ViewModel):
    __slots__ = ()
    COMMANDER = 'commander'
    DOG = 'dog'
    DRIVER = 'driver'
    GUNNER = 'gunner'
    LOADER = 'loader'
    RADIOMAN = 'radioman'

    def __init__(self, properties=0, commands=0):
        super(RecruitTypeConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(RecruitTypeConstants, self)._initialize()
