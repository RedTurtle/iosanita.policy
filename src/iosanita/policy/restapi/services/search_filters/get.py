# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from iosanita.policy.interfaces import IIoSanitaSettings
from plone import api
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from zope.component import getMultiAdapter

import json


class SearchFiltersGET(Service):
    def reply(self):
        return {
            "sections": self.get_section_data(field_id="search_sections"),
        }

    def get_section_data(self, field_id):
        try:
            values = api.portal.get_registry_record(
                field_id, interface=IIoSanitaSettings, default="[]"
            )
        except KeyError:
            return []
        utils = api.portal.get_tool(name="plone_utils")

        sections = []
        for setting in json.loads(values or "[]"):
            items = []
            for section_settings in setting.get("items") or []:
                for uid in section_settings.get("linkUrl") or []:
                    try:
                        section = api.content.get(UID=uid)
                    except Unauthorized:
                        # private folder
                        continue
                    if not section:
                        continue
                    item_infos = getMultiAdapter(
                        (section, self.request),
                        ISerializeToJsonSummary,
                    )()
                    children = section.listFolderContents(
                        contentFilter={"portal_type": utils.getUserFriendlyTypes()}
                    )
                    item_infos["items"] = [
                        getMultiAdapter(
                            (x, self.request),
                            ISerializeToJsonSummary,
                        )()
                        for x in children
                    ]
                    item_infos["title"] = section_settings.get("title", "")
                    items.append(item_infos)
            if items:
                sections.append(
                    {
                        "rootPath": setting.get("rootPath", ""),
                        "items": items,
                    }
                )
        return sections
