# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/prb_control/prb_config.py
from constants_utils import ConstInjector
from gui.prb_control import settings
ATTR_NAME = 'COSMIC_EVENT'

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    COSMIC_EVENT = 'cosmic_event'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    COSMIC_EVENT = 4294967296L


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    COSMIC_EVENT = 'CosmicEventBattle'
