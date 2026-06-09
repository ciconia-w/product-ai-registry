#!/usr/bin/env python3
"""
PMS Search Mixin — support for bySearch queries and saved query management.

Provides:
- browse_by_search(product_id, query_id): Browse stories by a saved search query
- list_saved_queries(module='story'): List available saved queries for a module
- browse_by_search_bugs(product_id, query_id): Browse bugs by saved search query (if applicable)
"""

import re
from bs4 import BeautifulSoup


class SearchMixin:
    """Mixin class for search/query-related operations."""

    def browse_by_search(self, product_id, query_id, branch=0, browse_type='allstory'):
        """Browse product stories filtered by a saved search (bySearch) query.

        The bySearch-{queryID} interface uses pre-saved search conditions stored
        in the Zentao database, accessible via query IDs found in the UI.

        Args:
            product_id: Product ID
            query_id: Saved query ID (numeric, e.g. 506)
            branch: Product branch (default 0)
            browse_type: Fallback browse type if query not found (default 'allstory')

        Returns:
            Raw HTML string of the browse page with filtered results,
            or a redirect to login page if session expired.

        Examples:
            >>> client.browse_by_search(493, 506)  # "控制中心需求池"
        """
        path = f"/product-browse-{product_id}-{branch}-bySearch-{query_id}.html"

        try:
            html = self._request("GET", path)

            # Check if redirect to login or deny page
            if isinstance(html, str) and len(html) < 200:
                if 'user-login' in html or 'user-deny' in html:
                    return None

            return html

        except Exception:
            return None

    def list_saved_queries(self, module='story', query_id=None):
        """List available saved queries for a given module.

        Retrieves queries from the user's saved query list in the Zentao UI.

        Args:
            module: Module type — 'story', 'bug', 'task', etc. (default 'story')
            query_id: Optional starting query ID (some endpoints need a reference)

        Returns:
            List of dicts with 'id' and 'name' keys, or None on failure.

        Examples:
            >>> client.list_saved_queries('story')
            [{'id': 506, 'name': '控制中心需求池'}, ...]
        """
        try:
            if query_id:
                path = f"/search-ajaxGetQuery-{module}-{query_id}.html"
            else:
                path = f"/search-ajaxGetQuery-{module}.html"

            html = self._request("GET", path)
            if not html or len(html) < 50:
                return []

            queries = []
            # Parse the <li> entries: <a href='javascript:executeQuery(ID)'...>NAME
            for m in re.finditer(r"executeQuery\((\d+)\)[^>]*>([^<]+)", html):
                qid = int(m.group(1))
                qname = m.group(2).strip()
                if qname:
                    queries.append({'id': qid, 'name': qname})

            return queries

        except Exception:
            return []

    def browse_by_search_bugs(self, product_id, query_id, branch=0):
        """Browse product bugs filtered by a saved search (bySearch) query.

        Args:
            product_id: Product ID
            query_id: Saved query ID
            branch: Product branch (default 0)

        Returns:
            Raw HTML string or None
        """
        path = f"/product-browse-{product_id}-{branch}-bySearch-{query_id}.html"

        try:
            html = self._request("GET", path)

            if isinstance(html, str) and len(html) < 200:
                if 'user-login' in html or 'user-deny' in html:
                    return None

            return html

        except Exception:
            return None