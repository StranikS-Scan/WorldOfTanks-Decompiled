# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_repository/__init__.py
from typing import TYPE_CHECKING
from shared_utils import getFullClassName
from skeletons.account_helpers.settings_repository import ISettingsRepository, SettingsTarget
if TYPE_CHECKING:
    from typing import Dict, List
    from dependency_injection_container import DependencyManager

def getSettingsRepositoryConfig(manager):
    from account_helpers.settings_repository.settings_repository import SettingsRepository
    repository = SettingsRepository()
    manager.addInstance(ISettingsRepository, repository, finalizer='fini')
    repository.init()


def getRegisteredSerializable():
    from gui.impl.lobby.customization.customization_carousel_helpers import _CustomizationFiltersSettingsSerializable
    from gui.impl.lobby.customization.settings_constants import CustomizationSettingsSerializable
    from gui.impl.lobby.customization.context.styled_mode import StyledMode2D, StyledMode3D
    from gui.shared.system_factory import collectExtensionSettingsProvidersSerializable
    registered = collectExtensionSettingsProvidersSerializable()
    registered.setdefault(SettingsTarget.CLIENT, []).extend([ getFullClassName(c) for c in [_CustomizationFiltersSettingsSerializable,
     CustomizationSettingsSerializable,
     StyledMode2D,
     StyledMode3D] ])
    return registered
