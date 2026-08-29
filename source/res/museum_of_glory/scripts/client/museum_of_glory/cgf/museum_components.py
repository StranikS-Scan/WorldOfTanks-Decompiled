# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/cgf/museum_components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class MuseumTankBack(object):
    domain = CGF.DomainOption.DomainClient


@registerComponent
class TankObjectSoundComponent(object):
    domain = CGF.DomainOption.DomainClient


@registerComponent
class MuseumTankLightFade(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    isFadeIn = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='is FadeIn', value=True)
