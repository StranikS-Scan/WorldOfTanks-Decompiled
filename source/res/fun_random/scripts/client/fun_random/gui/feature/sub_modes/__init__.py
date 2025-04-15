# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_modes/__init__.py
import typing
from fun_random_common.fun_constants import FunSubModeImpl
from fun_random.gui.feature.sub_modes.base_sub_mode import FunBaseSubMode
from fun_random.gui.feature.sub_modes.dev_sub_mode import FunDevSubMode
from fun_random.gui.shared.fun_system_factory import registerFunRandomSubMode, collectFunRandomSubMode
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode
    from fun_random.helpers.server_settings import FunSubModeConfig

def registerFunRandomSubModes():
    registerFunRandomSubMode(FunSubModeImpl.DEV_TEST, FunDevSubMode)


def createFunSubMode(subModeSettings):
    return (collectFunRandomSubMode(subModeSettings.client.subModeImpl) or FunBaseSubMode)(subModeSettings)
