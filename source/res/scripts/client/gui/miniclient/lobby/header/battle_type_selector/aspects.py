# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/lobby/header/battle_type_selector/aspects.py
from helpers import aop
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import text_styles, icons
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _DisabledSelectorItem, _RankedItem

class _BattleTypeDisable(aop.Aspect):

    def __init__(self, battleTypeAttributes, disabledSelectorClazz=_DisabledSelectorItem):
        self._battleTypeAttributes = battleTypeAttributes
        self._disabledSelectorClazz = disabledSelectorClazz
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        cd.avoid()
        items = cd.args[0]
        items.append(self._disabledSelectorClazz(*self._battleTypeAttributes))


class _DisabledRankedItem(_RankedItem):

    def update(self, state):
        pass

    def select(self):
        pass


class RankedBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED, PREBATTLE_ACTION_NAME.RANKED, 1), disabledSelectorClazz=_DisabledRankedItem)


class CommandBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_UNIT,
         PREBATTLE_ACTION_NAME.E_SPORT,
         3,
         SELECTOR_BATTLE_TYPES.UNIT))


class SortieBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_STRONGHOLDS,
         PREBATTLE_ACTION_NAME.FORT2,
         5,
         SELECTOR_BATTLE_TYPES.SORTIE))


class TrainingBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_TRAINING, PREBATTLE_ACTION_NAME.TRAININGS_LIST, 7))


class SpecialBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_SPEC, PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST, 6))


class CompanyBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_COMPANY, PREBATTLE_ACTION_NAME.COMPANIES_LIST, 4))


class FalloutBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_FALLOUT, PREBATTLE_ACTION_NAME.FALLOUT, 3))


class StrongholdBattle(_BattleTypeDisable):

    def __init__(self):
        _BattleTypeDisable.__init__(self, (MENU.HEADERBUTTONS_BATTLE_TYPES_FALLOUT, PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST, 4))


class OnBattleTypeSelectorPopulate(aop.Aspect):

    def atReturn(self, cd):
        cd.self.as_showMiniClientInfoS('{0} {1}'.format(icons.alert(-3), text_styles.main(_ms('#miniclient:battle_type_select_popover/message'))), _ms('#miniclient:personal_quests_welcome_view/continue_download'))
