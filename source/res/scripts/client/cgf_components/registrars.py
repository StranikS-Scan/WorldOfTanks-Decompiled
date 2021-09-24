# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/registrars.py
from constants import IS_EDITOR, IS_CLIENT
from cgf_script.managers_registrator import registerManager, Rule
if IS_EDITOR:

    class EventBattleRule(Rule):
        category = 'GameLogic'


    class WtBombRule(Rule):
        category = 'GameLogic'


    class PortalRule(Rule):
        category = 'GameLogic'


    class WTSoundsRule(Rule):
        category = 'GameLogic'


if IS_CLIENT:
    from cgf_components import wt_sounds_manager
    from cgf_components.arena_manager import ArenaManager
    from cgf_components.portal_manager import PortalSelectionManager
    from cgf_components.sound_manager import SoundComponentManager
    from cgf_components.bomb_managers import BombPickUpManager, BombDeployManager, BombCarryManager
    from cgf_components.bomb_managers import BombAbsorptionAreaManager, BombCapturedManager
    from cgf_components.escape_ability import AnimatorEventManager

    class EventBattleRule(Rule):
        category = 'GameLogic'

        @registerManager(AnimatorEventManager)
        def reg2(self):
            return None

        @registerManager(ArenaManager)
        def reg3(self):
            return None


    class WtBombRule(Rule):
        category = 'GameLogic'

        @registerManager(BombAbsorptionAreaManager)
        def reg1(self):
            return None

        @registerManager(BombCapturedManager)
        def reg2(self):
            return None

        @registerManager(BombPickUpManager)
        def reg3(self):
            return None

        @registerManager(BombDeployManager)
        def reg4(self):
            return None

        @registerManager(BombCarryManager)
        def reg5(self):
            return None


    class PortalRule(Rule):
        category = 'GameLogic'

        @registerManager(PortalSelectionManager)
        def reg1(self):
            return None


    class WTSoundsRule(Rule):
        category = 'GameLogic'

        @registerManager(SoundComponentManager)
        def reg1(self):
            return None

        @registerManager(wt_sounds_manager.LanguageSwitchManager)
        def reg2(self):
            return None

        @registerManager(wt_sounds_manager.VehicleSwitchManager)
        def reg3(self):
            return None

        @registerManager(wt_sounds_manager.EndBattleSoundManager)
        def reg4(self):
            return None

        @registerManager(wt_sounds_manager.VehicleKilledSoundManager)
        def reg5(self):
            return None

        @registerManager(wt_sounds_manager.GeneratorCaptureSoundManager)
        def reg6(self):
            return None

        @registerManager(wt_sounds_manager.FolloweeSoundManager)
        def reg7(self):
            return None

        @registerManager(wt_sounds_manager.ShieldSoundManager)
        def reg8(self):
            return None

        @registerManager(wt_sounds_manager.BossAbilitySoundManager)
        def reg9(self):
            return None

        @registerManager(wt_sounds_manager.CaptureLootSoundManager)
        def reg10(self):
            return None

        @registerManager(wt_sounds_manager.ShootingSoundManager)
        def reg11(self):
            return None

        @registerManager(wt_sounds_manager.SpawnSoundManager)
        def reg12(self):
            return None

        @registerManager(wt_sounds_manager.GameplayEnterSoundPlayer)
        def reg13(self):
            return None
