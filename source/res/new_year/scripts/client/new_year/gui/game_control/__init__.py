# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/__init__.py


def registerNewYearGameControllers():
    from gui.shared.system_factory import registerFestivityFactory, registerGameControllers
    from new_year.skeletons.new_year import INewYearSurpriseMachine, IRaccoonAnimationController, INewYearEnvironmentSwitchController, INewYearCurrencyController, INewYearTamagotchiController, IOldManController
    from new_year.gui.game_control.ny_factory import NewYearFactory
    from new_year.gui.game_control.surprise_machine_controller import NewYearSurpriseMachine
    from new_year.gui.game_control.ny_raccoon_animation_controller import RaccoonAnimationController
    from new_year.gui.impl.lobby.new_year.env_switcher.ny_environment_switcher_controller import NewYearEnvironmentSwitcherController
    from new_year.gui.game_control.ny_currency_controller import NewYearCurrencyController
    from new_year.gui.game_control.ny_tamagotchi_controller import NewYearTamagotchiController
    from new_year.gui.game_control.oldman_controller import OldManController
    registerFestivityFactory(NewYearFactory)
    registerGameControllers([(INewYearSurpriseMachine, NewYearSurpriseMachine, False),
     (IRaccoonAnimationController, RaccoonAnimationController, False),
     (INewYearEnvironmentSwitchController, NewYearEnvironmentSwitcherController, False),
     (INewYearCurrencyController, NewYearCurrencyController, False),
     (INewYearTamagotchiController, NewYearTamagotchiController, False),
     (IOldManController, OldManController, False)])
