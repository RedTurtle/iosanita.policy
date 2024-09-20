from plone.restapi.serializer.controlpanels import ControlpanelSerializeToJson
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from iosanita.policy.interfaces import IIoSanitaSettingsControlpanel
from plone import api
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import getMultiAdapter

import json


@implementer(ISerializeToJson)
@adapter(IIoSanitaSettingsControlpanel)
class IoSanitaControlpanelSerializeToJson(ControlpanelSerializeToJson):
    def __call__(self):
        """
        Convert json data into a string
        """
        json_data = super().__call__()
        search_sections = json.loads(json_data["data"].get("search_sections", "{}"))

        for section in search_sections:
            # expand stored data
            for item in section.get("items", []):
                expanded_links = []
                for link_url in item.get("linkUrl", []):
                    section = api.content.get(UID=link_url.get("UID", ""))
                    if not section:
                        continue
                    item_infos = getMultiAdapter(
                        (section, self.request),
                        ISerializeToJsonSummary,
                    )()
                    expanded_links.append(item_infos)
                item["linkUrl"] = expanded_links

        json_data["data"]["search_sections"] = json.dumps(search_sections)
        return json_data
