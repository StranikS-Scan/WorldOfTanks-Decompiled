# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/shared/fun_system_factory.py
from __future__ import absolute_import
from gui.shared.system_factory import CollectEventsManager

class FunFactoryConstants(object):
    SUB_MODE = 0
    BATTLE_RESULTS_SUB_FORMATTER = 1
    BATTLE_RESULTS_SUB_PRESENTER = 2
    BATTLE_RESULTS_SOUND_ENV = 3
    MODE_ASSETS_PACK_CONFIG_PATH = 4


__collectFunRandomEM = CollectEventsManager()

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


def registerBattleResultsSubPresenter(subModeImpl, subPresenterCls, viewCls):

    def onCollect(ctx):
        ctx['battleResultsSubPresenters'][subModeImpl] = (subPresenterCls, viewCls)

    __collectFunRandomEM.addListener(FunFactoryConstants.BATTLE_RESULTS_SUB_PRESENTER, onCollect)


def collectBattleResultsSubPresenters():
    return __collectFunRandomEM.handleEvent(FunFactoryConstants.BATTLE_RESULTS_SUB_PRESENTER, {'battleResultsSubPresenters': {}})['battleResultsSubPresenters']


def registerBattleResultsSoundEnv(arenaGuiType, battleResultsSoundEnvCls):

    def onCollect(ctx):
        ctx['battleResultsSoundEnv'] = battleResultsSoundEnvCls

    __collectFunRandomEM.addListener((FunFactoryConstants.BATTLE_RESULTS_SOUND_ENV, arenaGuiType), onCollect)


def collectBattleResultsSoundEnv(arenaGuiType):
    return __collectFunRandomEM.handleEvent((FunFactoryConstants.BATTLE_RESULTS_SOUND_ENV, arenaGuiType), ctx={}).get('battleResultsSoundEnv')


def registerModeAssetsPackConfigPath(assetsPointer, path):

    def onCollect(ctx):
        ctx['modeAssetsPackConfigPath'] = path

    __collectFunRandomEM.addListener((FunFactoryConstants.MODE_ASSETS_PACK_CONFIG_PATH, assetsPointer), onCollect)


def collectModeAssetsPackConfigPath(assetsPointer):
    return __collectFunRandomEM.handleEvent((FunFactoryConstants.MODE_ASSETS_PACK_CONFIG_PATH, assetsPointer), ctx={}).get('modeAssetsPackConfigPath', '')
