# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_view_impl.py
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IHangarFeatureStateController

class EarlyAccessViewImpl(ViewImpl):
    __hangarFeatureStateController = dependency.descriptor(IHangarFeatureStateController)

    def _initialize(self):
        super(EarlyAccessViewImpl, self)._initialize()
        self.__hangarFeatureStateController.enter(self.layoutID)

    def _finalize(self):
        self.__hangarFeatureStateController.exit(self.layoutID)
        super(EarlyAccessViewImpl, self)._finalize()
