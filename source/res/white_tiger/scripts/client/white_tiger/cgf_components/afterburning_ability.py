# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/afterburning_ability.py
from __future__ import absolute_import
import CGF
import GenericComponents
from cgf_script.registration import ComponentProperty, registerComponent, registerModule
from CustomEffectManager import CustomEffectManager

@registerComponent
class CustomEffectsModifier(object):
    value = ComponentProperty(type=CGF.PropertyType.Int, editorName='Value', value=0)
    key = ComponentProperty(type=CGF.PropertyType.String, editorName='Key', value='')


class CustomEffectsModifierSystem(CGF.System):
    ModifierActivated = CGF.ActivateReaction(CGF.ReactRo(CustomEffectsModifier), CGF.ReactRo(GenericComponents.RedirectorComponent))
    ModifierDeactivated = CGF.DeactivateReaction(CGF.ReactRo(CustomEffectsModifier), CGF.Ro(GenericComponents.RedirectorComponent))
    EffectManagerAccess = CGF.AccessReaction(CGF.Rw(CustomEffectManager))
    Reactions = CGF.Reactions(ModifierDeactivated, ModifierActivated, EffectManagerAccess)

    def update(self):
        effectManagerAccess = self.reaction(self.EffectManagerAccess)
        for modifier, redirector in self.reaction(self.ModifierDeactivated):
            self.onRemoved(modifier, redirector, effectManagerAccess)

        for modifier, redirector in self.reaction(self.ModifierActivated):
            self.onAdded(modifier, redirector, effectManagerAccess)

    def onAdded(self, modifier, redirector, effectManagerAccess):
        effectMgr = effectManagerAccess.find(redirector.redirectionTarget)
        if effectMgr is not None:
            effectMgr.variables[modifier.key] = modifier.value
        return

    def onRemoved(self, modifier, redirector, effectManagerAccess):
        effectMgr = effectManagerAccess.find(redirector.redirectionTarget)
        if effectMgr is not None:
            effectMgr.variables[modifier.key] = 0
        return


@registerModule
class AfterburningModule(object):
    group = 'GameLogic'
    systems = [CGF.RegisterSystem(CustomEffectsModifierSystem, domain=CGF.Domain.ClientEditor)]
    components = [CustomEffectsModifier]
