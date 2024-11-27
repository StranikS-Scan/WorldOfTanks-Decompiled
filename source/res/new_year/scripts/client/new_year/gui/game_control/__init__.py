# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/__init__.py


def registerNewYearGameControllers():
    from gui.shared.system_factory import registerFestivityFactory, registerGameControllers
    from new_year.skeletons.new_year import INewYearCraftMachineController, INewYearSurpriseMachine, INewYearRaccoonController, INewYearBubbleNavigationController
    from new_year.gui.game_control.ny_factory import NewYearFactory
    from new_year.gui.game_control.craft_machine_controller import NewYearCraftMachineController
    from new_year.gui.game_control.surprise_machine_controller import NewYearSurpriseMachine
    from new_year.gui.game_control.ny_raccoon_controller import NewYearRaccoonController
    from new_year.gui.shared.ny_bubble_navigation_controller import NewYearBubbleNavigationController
    registerFestivityFactory(NewYearFactory)
    registerGameControllers([(INewYearCraftMachineController, NewYearCraftMachineController, False),
     (INewYearSurpriseMachine, NewYearSurpriseMachine, False),
     (INewYearRaccoonController, NewYearRaccoonController, False),
     (INewYearBubbleNavigationController, NewYearBubbleNavigationController, False)])
