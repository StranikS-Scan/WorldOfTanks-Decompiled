# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/effects/components.py
import CGF
import GenericComponents
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class WTAnimatorLinkComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'White Tiger'
    linkToAnimator = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Link to Animator', value=GenericComponents.AnimatorComponent)


@registerComponent
class WTAnomalyDisappearComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'White Tiger'
    prefab = ComponentProperty(type=CGFMetaTypes.STRING, editorName='prefab', value='', annotations={'path': '*.prefab'})


@registerComponent
class WTAnomalyBinocularComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'White Tiger'
    binocularsEffects = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='binoculars effects')
