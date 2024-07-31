# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from iosanita.policy import _
from iosanita.policy.controlpanels.settings import IIoSanitaSettings


class IoSanitaSettingsForm(RegistryEditForm):
    schema = IIoSanitaSettings
    id = "iosanita-settings"
    label = _("IoSanita Settings")


class IoSanitaSettingsView(ControlPanelFormWrapper):
    """ """

    form = IoSanitaSettingsForm
