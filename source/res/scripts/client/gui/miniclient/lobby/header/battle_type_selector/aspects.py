# Embedded file name: scripts/client/gui/miniclient/lobby/header/battle_type_selector/aspects.py
from helpers import aop
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import text_styles, icons
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _DisabledSelectorItem

class _BattleTypeDisable(aop.Aspect):

    def __init__(self, battleTypeAttributes):
        self._battleTypeAttributes = battleTypeAttributes
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        cd.avoid()
        items = cd.args[0]
        items.append(_DisabledSelectorItem(*self._battleTypeAttributes))


class CommandBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_UNIT,
         PREBATTLE_ACTION_NAME.UNIT,
         2,
         SELECTOR_BATTLE_TYPES.UNIT))


class SortieBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_FORT,
         PREBATTLE_ACTION_NAME.FORT,
         4,
         SELECTOR_BATTLE_TYPES.SORTIE))


class TrainingBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_TRAINING, PREBATTLE_ACTION_NAME.TRAINING, 6))


class SpecialBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_SPEC, PREBATTLE_ACTION_NAME.SPEC_BATTLE, 5))


class CompanyBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_COMPANY, PREBATTLE_ACTION_NAME.COMPANY, 3))


class FalloutBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_FALLOUT, PREBATTLE_ACTION_NAME.FALLOUT, 2))


class OnBattleTypeSelectorPopulate(aop.Aspect):

    def atReturn(self, cd):
        cd.self.as_showMiniClientInfoS('{0} {1}'.format(icons.alert(-3), text_styles.main(_ms('#miniclient:battle_type_select_popover/message'))), _ms('#miniclient:personal_quests_welcome_view/continue_download'))
