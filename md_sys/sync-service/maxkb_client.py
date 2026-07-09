import logging
import threading
import requests
import config

logger = logging.getLogger(__name__)


class MaxKBClient:
    def __init__(self):
        self.base_url = config.MAXKB_URL.rstrip("/")
        self.admin_path = "/admin"
        self._token = None
        self._token_lock = threading.Lock()

    def _login(self) -> str:
        url = f"{self.base_url}{self.admin_path}/api/user/login"
        resp = requests.post(url, json={
            "username": config.MAXKB_USERNAME,
            "password": config.MAXKB_PASSWORD,
        }, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        token = data.get("data", {}).get("token")
        if not token:
            raise ValueError(f"MaxKB login failed: {data}")
        logger.info("MaxKB login successful")
        return token

    def _get_token(self) -> str:
        with self._token_lock:
            if self._token is None:
                self._token = self._login()
            return self._token

    def _refresh_token(self):
        with self._token_lock:
            self._token = None
        self._get_token()

    def _url(self, path: str) -> str:
        ws = config.MAXKB_WORKSPACE_ID
        kb = config.MAXKB_KNOWLEDGE_ID
        return f"{self.base_url}{self.admin_path}/api/workspace/{ws}/knowledge/{kb}/{path.lstrip('/')}"

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        token = self._get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers
        kwargs.setdefault("timeout", 30)
        resp = requests.request(method, url, **kwargs)
        if resp.status_code == 401:
            self._refresh_token()
            headers["Authorization"] = f"Bearer {self._get_token()}"
            resp = requests.request(method, url, **kwargs)
        return resp

    def _extract_data(self, result):
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        return result

    def _get(self, path: str, params: dict = None):
        resp = self._request("GET", self._url(path), params=params)
        resp.raise_for_status()
        return self._extract_data(resp.json())

    def _post(self, path: str, data: dict = None):
        resp = self._request("POST", self._url(path), json=data)
        resp.raise_for_status()
        return self._extract_data(resp.json())

    def _put(self, path: str, data: dict = None):
        resp = self._request("PUT", self._url(path), json=data)
        resp.raise_for_status()
        return self._extract_data(resp.json())

    def _delete(self, path: str):
        resp = self._request("DELETE", self._url(path))
        resp.raise_for_status()
        return resp.json() if resp.text else {}

    def list_documents(self) -> list[dict]:
        result = self._get("/document")
        return result if isinstance(result, list) else result.get("data", [])

    def create_document(self, name: str, paragraphs: list[dict]) -> dict:
        body = {"name": name, "paragraphs": paragraphs}
        return self._post("/document", body)

    def batch_create_documents(self, docs: list[dict]) -> list:
        return self._put("/document/batch_create", docs)

    def delete_document(self, document_id: str):
        try:
            self._delete(f"/document/{document_id}")
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Delete document {document_id} failed: {e}")

    def batch_delete_documents(self, id_list: list[str]):
        if not id_list:
            return
        self._put("/document/batch_delete", {"id_list": id_list})
