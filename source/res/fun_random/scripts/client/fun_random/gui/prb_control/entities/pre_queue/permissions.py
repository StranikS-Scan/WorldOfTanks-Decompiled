# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/pre_queue/permissions.py
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions

class FunRandomPermissions(PreQueuePermissions, FunSubModesWatcher):

    @hasDesiredSubMode(defReturn=False)
    def canCreateSquad(self):
        return super(FunRandomPermissions, self).canCreateSquad()
