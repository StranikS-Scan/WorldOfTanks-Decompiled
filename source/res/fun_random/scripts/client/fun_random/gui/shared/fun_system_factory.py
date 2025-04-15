# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/shared/fun_system_factory.py
from gui.shared.system_factory import CollectEventsManager

class FunFactoryConstants(object):
    PRESETS_CONFIG = 0
    SUB_MODE = 1
    BATTLE_RESULTS_SUB_FORMATTER = 2
    BATTLE_RESULTS_PRESENTER = 3


__collectFunRandomEM = CollectEventsManager()

def registerPresetConfigPath(configPath):

    def onCollect(ctx):
        ctx['presetConfigs'].append(configPath)

    __collectFunRandomEM.addListener(FunFactoryConstants.PRESETS_CONFIG, onCollect)


def collectPresetConfigs():
    return __collectFunRandomEM.handleEvent(FunFactoryConstants.PRESETS_CONFIG, {'presetConfigs': []})['presetConfigs']


def registerFunRandomSubMode(subModeImpl, subMode):

    def onCollect(ctx):
        ctx[subModeImpl] = subMode

    __collectFunRandomEM.addListener((FunFactoryConstants.SUB_MODE, subModeImpl), onCollect)


def collectFunRandomSubMode(subModeImpl):
    return __collectFunRandomEM.handleEvent((FunFactoryConstants.SUB_MODE, subModeImpl), {}).get(subModeImpl)


def registerBattleResultsMessageSubFormatter(arenaGuiType, battleResultsFormatterCls):

    def onCollect(ctx):
        ctx['battleResultsSubFormatter'] = battleResultsFormatterCls

    __collectFunRandomEM.addListener((FunFactoryConstants.BATTLE_RESULTS_SUB_FORMATTER, arenaGuiType), onCollect)


def collectBattleResultsMessageSubFormatter(arenaGuiType):
    return __collectFunRandomEM.handleEvent((FunFactoryConstants.BATTLE_RESULTS_SUB_FORMATTER, arenaGuiType), ctx={}).get('battleResultsSubFormatter')


def registerFunBattleResultsPresenter(subModeImpl, presenterCls):

    def onCollect(ctx):
        ctx[subModeImpl] = presenterCls

    __collectFunRandomEM.addListener((FunFactoryConstants.BATTLE_RESULTS_PRESENTER, subModeImpl), onCollect)


def collectFunBattleResultsPresenter(subModeImpl):
    return __collectFunRandomEM.handleEvent((FunFactoryConstants.BATTLE_RESULTS_PRESENTER, subModeImpl), {}).get(subModeImpl)
