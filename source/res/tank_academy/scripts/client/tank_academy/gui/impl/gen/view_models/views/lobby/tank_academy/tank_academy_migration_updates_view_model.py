# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_migration_updates_view_model.py
from frameworks.wulf import ViewModel

class TankAcademyMigrationUpdatesViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(TankAcademyMigrationUpdatesViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(TankAcademyMigrationUpdatesViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
