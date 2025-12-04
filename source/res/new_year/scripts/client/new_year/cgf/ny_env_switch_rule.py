# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/ny_env_switch_rule.py
import CGF
from new_year.skeletons.new_year import INewYearEnvironmentSwitchController
from helpers import dependency

class NewYearEnvironmentLoader(CGF.ComponentManager):
    __nyEnvSwitcherController = dependency.descriptor(INewYearEnvironmentSwitchController)

    def activate(self):
        self.__nyEnvSwitcherController.applyCurrentEnvironment()
