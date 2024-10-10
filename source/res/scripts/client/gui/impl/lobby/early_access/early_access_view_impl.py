# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_view_impl.py
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController

class EarlyAccessViewImpl(ViewImpl):
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def _onShown(self):
        super(EarlyAccessViewImpl, self)._onShown()
        self.__earlyAccessCtrl.hangarFeatureState.enter(self.layoutID)

    def _finalize(self):
        self.__earlyAccessCtrl.hangarFeatureState.exit(self.layoutID)
        super(EarlyAccessViewImpl, self)._finalize()
