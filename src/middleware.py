import requests
from typing import Dict, Any, Optional

class BackendMiddleware:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _handle_request(
            self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, token: Optional[str] = None
    ) -> Any:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(method, url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise ValueError(f"HTTP error occurred: {http_err}") from http_err
        except Exception as err:
            raise ValueError(f"An error occurred: {err}") from err

    def register_user(self, username: str, password: str, is_admin: int) -> Any:
        data = {"username": username, "password": password, "is_admin": is_admin}
        return self._handle_request("POST", "/register", data)

    def login_user(self, username: str, password: str) -> Any:
        data = {"username": username, "password": password}
        return self._handle_request("POST", "/login", data)

    def get_user_details(self, token: str) -> Any:
        return self._handle_request("GET", "/users/me", token=token)

    def create_product(self, token: str, name: str, price: float, stock: int, category: str, expiration_date: str) -> Any:
        data = {
            "name": name,
            "price": price,
            "stock": stock,
            "category": category,
            "expiration_date": expiration_date,
        }
        return self._handle_request("POST", "/products", data, token)

    def get_products(self, token: Optional[str] = None) -> Any:
        return self._handle_request("GET", "/products", token=token)

    def add_to_basket(self, token: str, product_id: int, quantity: int) -> Any:
        data = {"product_id": product_id, "quantity": quantity}
        return self._handle_request("POST", "/basket/items", data, token)

    def get_basket(self, token: str) -> Any:
        return self._handle_request("GET", "/basket", token=token)

    def update_basket_item(self, token: str, item_id: int, quantity: int) -> Any:
        data = {"product_id": item_id, "quantity": quantity}
        return self._handle_request("PUT", f"/basket/items/{item_id}", data, token)

    def delete_basket_item(self, token: str, item_id: int) -> Any:
        return self._handle_request("DELETE", f"/basket/items/{item_id}", token=token)

    def checkout_basket(self, token: str) -> Any:
        return self._handle_request("POST", "/basket/checkout", token=token)
