# -*- coding: utf-8 -*-

from . import logger
from iosanita.policy.interfaces import IIoSanitaSettings
from plone import api

import json


def upgrade(setup_tool=None):
    """ """
    logger.info("Running upgrade (Python): Fix contatti_testata structure")
    value = (
        api.portal.get_registry_record("contatti_testata", interface=IIoSanitaSettings)
        or ""  # noqa
    )
    if not value:
        return

    value = json.loads(value)
    value = [
        {
            "rootPath": "/",
            "items": value,
        },
    ]

    api.portal.set_registry_record(
        "contatti_testata", json.dumps(value), interface=IIoSanitaSettings
    )
