r"""Automated pytest + WebTest REST API test suite (Spring JUnit + MockMvc equivalent).

Run with:
    .\test.bat
or:
    ..\.venv\Scripts\pytest -v
"""

import os

from paste.deploy import loadapp
import pytest
from webtest import TestApp

PHASE6_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="module")
def client():
    """Boot the real Zope 5 WSGI app in-process (like Spring @SpringBootTest + MockMvc)."""
    os.makedirs(os.path.join(PHASE6_DIR, "var"), exist_ok=True)
    prev_cwd = os.getcwd()
    os.chdir(PHASE6_DIR)
    try:
        wsgi_app = loadapp("config:etc/zope.ini", relative_to=PHASE6_DIR)
        yield TestApp(wsgi_app)
    finally:
        os.chdir(prev_cwd)


def test_health_returns_up_and_request_id(client):
    res = client.get("/@@api-health", headers={"X-Request-Id": "req-001"})
    assert res.status_int == 200
    assert res.headers["X-Request-Id"] == "req-001"
    assert res.json["status"] == "ok"
    assert res.json["data"]["status"] == "UP"
    assert "engineering" in res.json["data"]["indexedDepartments"]


def test_indexed_search_by_dept_and_skill(client):
    res = client.get("/@@api-employees?dept=Engineering&skill=MySQL")
    assert res.status_int == 200
    codes = sorted(e["empCode"] for e in res.json["data"]["items"])
    assert codes == ["EMP-0002", "EMP-0004"]


def test_create_employee_updates_catalog_index(client):
    res = client.post_json(
        "/@@api-employees",
        {
            "empCode": "EMP-0099",
            "nameEn": "Taro Yamada",
            "nameJa": "山田 太郎",
            "departmentEn": "Engineering",
            "departmentJa": "開発部",
            "role": "SRE",
            "skills": ["Nginx", "MySQL"],
        },
    )
    assert res.status_int == 201
    assert res.json["data"]["empCode"] == "EMP-0099"

    # Immediately searchable via the B-Tree skill index!
    search = client.get("/@@api-employees?skill=Nginx")
    assert search.status_int == 200
    assert [e["empCode"] for e in search.json["data"]["items"]] == ["EMP-0099"]


def test_not_found_returns_json_error(client):
    res = client.get("/@@api-employees/EMP-4040", expect_errors=True)
    assert res.status_int == 404
    assert res.json["status"] == "error"
    assert res.json["error"]["code"] == "E_NOT_FOUND"
