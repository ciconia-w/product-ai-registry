import re


class ProductMixin:
    """Mixin class for product-related operations."""

    def list_products(self):
        """List all products."""
        path = "/product-all.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def browse_product(self, product_id):
        """Browse stories/bugs in a product."""
        path = f"/product-browse-{product_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def view_product(self, product_id):
        """View product details."""
        path = f"/product-view-{product_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def create_product(self, product_name, product_code, description, uid):
        """Create a new product (requires permission)."""
        path = "/product-create.html"
        headers = {}
        body = {
        "name": product_name,
        "code": product_code,
        "line": "0",
        "PO": "",
        "QD": "",
        "RD": "",
        "type": "normal",
        "status": "normal",
        "desc": description,
        "acl": "open",
        "uid": uid,
    }
        return self._request("POST", path, headers=headers, body=body, content_type="application/x-www-form-urlencoded")

    def product_plans(self):
        """List plans in a product."""
        path = f"/product-plan-{product_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def product_releases(self):
        """List releases in a product."""
        path = f"/product-release-{product_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)
