# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_modes/__init__.py
import typing
from fun_random_common.fun_constants import FunSubModeImpl
from fun_random.gui.feature.sub_modes.base_sub_mode import FunBaseSubMode
from fun_random.gui.feature.sub_modes.dev_sub_mode import FunDevSubMode
from fun_random.gui.feature.sub_modes.new_year_sub_mode import FunNewYearSubMode
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode
    from fun_random.helpers.server_settings import FunSubModeConfig
_SUB_MODE_IMPLS_MAP = {FunSubModeImpl.DEV_TEST: FunDevSubMode,
 FunSubModeImpl.NEW_YEAR: FunNewYearSubMode}

def createFunSubMode(subModeSettings):
    return _SUB_MODE_IMPLS_MAP.get(subModeSettings.client.subModeImpl, FunBaseSubMode)(subModeSettings)
