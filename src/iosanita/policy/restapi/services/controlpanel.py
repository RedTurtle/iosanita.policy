# -*- coding: utf-8 -*-
from iosanita.policy.controlpanels.settings import IIoSanitaSettings
from iosanita.policy.controlpanels.settings import (
    IoSanitaSettingsControlpanel,
)
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, Interface)
@implementer(IoSanitaSettingsControlpanel)
class IoSanitaSettings(RegistryConfigletPanel):
    schema = IIoSanitaSettings
    configlet_id = "IoSanitaSettings"
    configlet_category_id = "Products"
    schema_prefix = None
