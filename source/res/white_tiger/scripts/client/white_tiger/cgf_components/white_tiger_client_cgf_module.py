# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/white_tiger_client_cgf_module.py
from __future__ import absolute_import
import CGF
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.registration import bonusCapsPredicate, registerModule
from white_tiger.cgf_components.arena_manager import WTArenaSystem
from white_tiger.cgf_components.collision_components import CollisionSystem, WTProjectileTarget, DynamicCollisionComponent
from white_tiger.cgf_components.generator_components import WTGeneratorActivationComponent, WTGeneratorCapturedComponent
from white_tiger.cgf_components.sound_components import WTSoundNotification, WTConditionalSound2D, WTConditionalSound3D, WTVehicleSound, WTVehicleSoundComponent
from white_tiger.cgf_components.sound_components_manager import SoundSystem
from white_tiger.cgf_components.sound_event_managers import WTLanguageSwitchSystem, WTPlayerExperienceSwitchSystem, WTVehicleSwitchSystem, WTEndBattleSoundSystem, WTShieldSoundSystem, WTGeneratorCaptureSoundSystem, WTVehicleKilledSoundSystem, WTBossAbilitySoundSystem, WTShootingSoundSystem, WTHarrierRespawnSoundSystem, WTGameplayEnterSoundPlayer, WTOvertimeSoundPlayer
from white_tiger.cgf_components.sound_helper_components import WTBossImpulse, WTGeneratorEmerging, WTMinibossImpulse, WTStunnedByBoss, WTHarrierRespawnComponent

@registerModule
class ClientWhiteTigerModule(object):
    name = 'White Tiger Client Module'
    group = 'White Tiger'
    systems = [CGF.RegisterSystem(WTArenaSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(CollisionSystem, domain=CGF.Domain.Client | CGF.Domain.Editor, updateAfter=(CGF.TransformUpdateSystem,), predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(SoundSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTLanguageSwitchSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTPlayerExperienceSwitchSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTVehicleSwitchSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTEndBattleSoundSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTShieldSoundSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTGeneratorCaptureSoundSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,), predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTVehicleKilledSoundSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTBossAbilitySoundSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTShootingSoundSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTHarrierRespawnSoundSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTGameplayEnterSoundPlayer, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID)),
     CGF.RegisterSystem(WTOvertimeSoundPlayer, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, spaceID))]
    components = [WTProjectileTarget,
     DynamicCollisionComponent,
     WTSoundNotification,
     WTConditionalSound2D,
     WTConditionalSound3D,
     WTVehicleSound,
     WTVehicleSoundComponent,
     WTBossImpulse,
     WTGeneratorEmerging,
     WTMinibossImpulse,
     WTStunnedByBoss,
     WTHarrierRespawnComponent,
     WTGeneratorActivationComponent,
     WTGeneratorCapturedComponent]
