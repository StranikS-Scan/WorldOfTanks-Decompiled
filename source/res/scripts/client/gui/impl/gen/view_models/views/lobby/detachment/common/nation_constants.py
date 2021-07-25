# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/nation_constants.py
from frameworks.wulf import ViewModel

class NationConstants(ViewModel):
    __slots__ = ()
    CHINA = 'china'
    CZECH = 'czech'
    FRANCE = 'france'
    GERMANY = 'germany'
    ITALY = 'italy'
    JAPAN = 'japan'
    POLAND = 'poland'
    SWEDEN = 'sweden'
    UK = 'uk'
    USA = 'usa'
    USSR = 'ussr'

    def __init__(self, properties=0, commands=0):
        super(NationConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NationConstants, self)._initialize()
