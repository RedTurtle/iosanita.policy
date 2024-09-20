from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.controlpanels import ControlpanelDeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import adapter
from zope.interface import implementer
from iosanita.policy.interfaces import IIoSanitaSettingsControlpanel


@implementer(IDeserializeFromJson)
@adapter(IIoSanitaSettingsControlpanel)
class IoSanitaControlpanelDeserializeFromJson(ControlpanelDeserializeFromJson):
    def __call__(self):
        """
        Convert json data into a string
        """
        super().__call__()

        req = json_body(self.controlpanel.request)
        proxy = self.registry.forInterface(self.schema, prefix=self.schema_prefix)

        search_sections = req.get("search_sections", [])
        for section in search_sections:
            # simplify stored data
            for item in section.get("items", []):
                fixed_urls = [
                    {"UID": x.get("UID", "")}
                    for x in item.get("linkUrl", [])
                    if x.get("UID", "")
                ]
                item["linkUrl"] = fixed_urls

        setattr(proxy, "search_sections", search_sections)
