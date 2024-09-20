# -*- coding: utf-8 -*-
from iosanita.policy.interfaces import IIoSanitaSettings
from plone import api
from plone.restapi.services import Service

import json


class SearchFiltersGET(Service):
    def reply(self):
        return {
            "quick_search": self.get_data_from_registry(field_id="quick_search"),
        }

    def get_data_from_registry(self, field_id):
        try:
            values = api.portal.get_registry_record(
                field_id, interface=IIoSanitaSettings, default="[]"
            )
        except KeyError:
            return []
        return json.loads(values or "[]")
