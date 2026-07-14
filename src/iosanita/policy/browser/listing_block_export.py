import io
import json
from iosanita.contenttypes.browser.export_view import (
    ExportViewDownload as BaseExportViewDownload,
)
from iosanita.contenttypes.browser.export_view import IExportViewTraverser
from plone import api
from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


class IListingBlockExportViewTraverser(IExportViewTraverser):
    """
    Marker interface for ListingBlockExport views
    """


@implementer(IListingBlockExportViewTraverser)
class ListingBlockExportViewTraverser(BrowserView):
    """
    View that can be traversed by @@download
    """


@implementer(IPublishTraverse)
class ListingBlockExportViewDownload(BaseExportViewDownload):
    """ """

    def __call__(self):
        self._request = self.request
        self._block = self._extract_block()
        self._items = self.get_data()
        self.columns = self.get_columns(data=self._items)
        self.headers = self.get_headers()
        return super().__call__()

    def _extract_block(self):
        """ """
        block_id = self._request.form.get("block_id", "")
        if not block_id:
            raise Exception("block_id missing")

        context = self.context.context
        blocks = getattr(context, "blocks", {}) or {}

        block = blocks.get(block_id)
        if not block:
            raise Exception(f"Block {block_id} not found")

        return block

    def get_data(self):
        """ """
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

        if not columns or columns[0].get("key") != "@id":
            columns.insert(0, {"title": "URL", "key": "@id"})

        return columns

    def get_headers(self, data=None):
        columns = self.columns
        headers = [column["title"] for column in columns]
        return headers

    def format_row(self, item):
        """ """
        row = []
        for col in self.columns:
            value = item.get(col["key"], "")
            if col["key"] != "@id":
                value = self._format_value(value)
            row.append(value)

        return row

    def _format_value(self, value):
        """"""
        if value is None:
            return ""
        if isinstance(value, dict):
            return value.get("title", "")
        if isinstance(value, list):
            if not value:
                return ""
            if isinstance(value[0], dict):
                return ", ".join(v.get("title", str(v)) for v in value)
            return ", ".join(str(v) for v in value)
        return str(value)

    def pdf_title(self):
        block_title = self._block.get("title", "")
        site_title = api.portal.get_registry_record("plone.site_title")
        if site_title and block_title:
            return f"{site_title}: {block_title}"
        return site_title or block_title or api.portal.get().Title()

    def get_html_for_pdf(self, data):
        """
        Generate HTML data from the provided data.
        """
        rows = [self.format_row(item) for item in data]
        view = api.content.get_view(
            name="export_pdf_template", context=self, request=self._request
        )
        return view(rows=rows, headers=self.headers)

    def pdf_description(self):
        return None
