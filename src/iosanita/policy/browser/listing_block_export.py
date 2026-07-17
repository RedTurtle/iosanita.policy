import io
import json
from iosanita.contenttypes.browser.export_view import (
    ExportViewDownload as BaseExportViewDownload,
)
from iosanita.contenttypes.browser.export_view import IExportViewTraverser
from plone import api
from Products.Five.browser import BrowserView
from rer.blocks2html.blocks_converter import blocks_to_html
from zoneinfo import ZoneInfo
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import csv as csv_mod
from io import StringIO

import re
from datetime import datetime
from zExceptions import NotFound


class IListingBlockExportViewTraverser(IExportViewTraverser):
    """Marker interface for ListingBlockExport views"""


@implementer(IListingBlockExportViewTraverser)
class ListingBlockExportViewTraverser(BrowserView):
    """View that can be traversed by @@download"""


@implementer(IPublishTraverse)
class ListingBlockExportViewDownload(BaseExportViewDownload):

    def __call__(self):
        self._request = self.request
        self._block = self._extract_block()
        items = self.get_data()
        self.columns = self.get_columns(data=items)
        self.headers = self.get_headers()
        return super().__call__()
    
    def _extract_block(self):
        block_id = self._request.form.get("block_id", "")
        if not block_id:
            raise NotFound("block_id missing")
        context = self.context.context
        blocks = getattr(context, "blocks", {}) or {}
        block = blocks.get(block_id)
        if not block:
            raise NotFound(f"Block {block_id} not found")
        return block

    def get_data(self):
        querystring = self._block.get("querystring", {})
        search_payload = json.dumps(
            {
                "query": querystring.get("query", []),
                "sort_on": querystring.get("sort_on", ""),
                "sort_order": querystring.get("sort_order", "ascending"),
                "fullobjects": True,
                "b_size": 100000,
            }
        ).encode("utf-8")

        original_method = self._request.method
        try:
            self._request.method = "POST"
            self._request["BODY"] = search_payload
            self._request.stdin = io.BytesIO(search_payload)

            service = queryMultiAdapter(
                (api.portal.get(), self._request),
                name="POST_application_json_@querystring-search",
            )
            if service is None:
                raise Exception("@querystring-search service not found")
            service.check_permission()
            result = service.reply()
        finally:
            self._request.method = original_method

        return result.get("items", [])

    def _html_to_text(self, html):
        if not html:
            return ""
        try:
            transforms = api.portal.get_tool("portal_transforms")
            data = transforms.convertTo(
                "text/plain",
                html,
                mimetype="text/html",
                encoding="utf-8",
            )
            return data.getData().strip()
        except Exception:
            return html

    def get_columns(self, data=None):
        """ """
        columns = [
            {
                "title": col.get("title", col.get("field", "")),
                "key": col.get("field", ""),
            }
            for col in self._block.get("columns", [])
        ]

        if not columns and data:
            columns = [{"title": k, "key": k} for k in data[0].keys()]

        keys = [c["key"] for c in columns]
        if "title" not in keys:
            columns.insert(0, {"title": "Titolo", "key": "title"})

        return columns

    def get_headers(self, data=None):
        return [col["title"] for col in self.columns]

    def format_row(self, item):
        """ """
        row = [item.get("@id", "")]
        for col in self.columns:
            row.append(self._format_value(item.get(col["key"], "")))
        return row

    def get_csv(self, data, **kwargs):

        sep = kwargs.get("sep", ",")
        encoding = kwargs.get("encoding", "utf-8-sig")

        csv_buffer = StringIO()
        csv_writer = csv_mod.writer(
            csv_buffer, delimiter=sep, quoting=csv_mod.QUOTE_ALL
        )

        csv_writer.writerow(["URL"] + [col["title"] for col in self.columns])

        for item in data:
            full_row = self.format_row(item)
            csv_writer.writerow(full_row)

        csv_data = csv_buffer.getvalue()
        csv_bytes = (
            b"\xef\xbb\xbf" + csv_data.encode("utf-8")
            if encoding == "utf-8-sig"
            else csv_data.encode(encoding)
        )

        response = self.request.response
        response.setHeader(
            "Content-Disposition", f"attachment;filename={self.get_filename()}"
        )
        response.setHeader("Content-Type", f"text/csv; charset={encoding}")
        return csv_bytes

    def _format_value(self, value):
        if value is None:
            return ""
        if isinstance(value, dict) and "blocks" in value:
            html = blocks_to_html(
                context=self.context.context,
                blocks=value.get("blocks", {}),
                blocks_layout=value.get("blocks_layout", {}),
            )
            return self._html_to_text(html)
        if isinstance(value, dict) and "download" in value:
            url = value["download"]
            title = value.get("title", value.get("filename", url))
            if self.export_type == "pdf":
                return f'<a href="{url}">{title}</a>'
            return url
        if isinstance(value, dict):
            return value.get("title", value.get("token", ""))
        if isinstance(value, list):
            if not value:
                return ""
            if isinstance(value[0], dict):
                if "@id" in value[0] and "title" in value[0]:
                    if self.export_type == "pdf":
                        return ", ".join(
                            f'<a href="{v["@id"]}">{v["title"]}</a>' for v in value
                        )
                    return ", ".join(v["@id"] for v in value)
                return ", ".join(v.get("title", str(v)) for v in value)
            return ", ".join(str(v) for v in value)
        if isinstance(value, str):
            if re.match(r"^\d{4}-\d{2}-\d{2}", value):
                try:
                    dt = datetime.fromisoformat(value)
                    if dt.tzinfo is not None:
                        dt = dt.astimezone(ZoneInfo("Europe/Rome"))
                    if dt.hour or dt.minute:
                        return dt.strftime("%d/%m/%Y %H:%M")
                    return dt.strftime("%d/%m/%Y")
                except ValueError:
                    pass

        return str(value)

    def pdf_title(self):
        block_title = self._block.get("title", "")
        site_title = api.portal.get_registry_record("plone.site_title")
        if site_title and block_title:
            return f"{site_title}: {block_title}"
        return site_title or block_title or api.portal.get().Title()

    def get_html_for_pdf(self, data):
        rows = [self.format_row(item) for item in data]
        view = api.content.get_view(
            name="export_pdf_template", context=self, request=self._request
        )
        return view(rows=rows, headers=self.headers)

    def pdf_description(self):
        return None
