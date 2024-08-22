# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/service_record/context.py
from gui.impl.lobby.crew.container_vews.common.base_personal_case_context import BasePersonalCaseContext

class ServiceRecordViewContext(BasePersonalCaseContext):
    __slots__ = ('_dossier',)

    def __init__(self, tankmanID):
        self._dossier = None
        super(ServiceRecordViewContext, self).__init__(tankmanID)
        return

    @property
    def dossier(self):
        return self._dossier

    def update(self, tankmanID=None):
        if tankmanID:
            super(ServiceRecordViewContext, self).update(tankmanID)
            self._dossier = self.itemsCache.items.getTankmanDossier(tankmanID)
