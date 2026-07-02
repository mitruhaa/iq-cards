import re
import threading

import pytest
from werkzeug.serving import make_server

from .conftest import write_import


pytest.importorskip("playwright")
from playwright.sync_api import expect, sync_playwright


SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>'


class LiveServer(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.server = make_server("127.0.0.1", 0, app)
        self.port = self.server.server_port

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()


@pytest.fixture()
def live_server(app):
    try:
        server = LiveServer(app)
    except PermissionError as exc:
        pytest.skip(f"Local test server sockets are not available: {exc}")
    server.start()
    yield f"http://127.0.0.1:{server.port}"
    server.stop()


def test_study_flow_in_browser(app, live_server, tmp_path):
    write_import(
        app,
        [
            {"question": "Capital?", "answer": {"text": "Rome", "images": []}},
            {
                "question": "Shape?",
                "answer": {"text": "Triangle", "images": ["triangle.svg"]},
            },
        ],
        {"triangle.svg": SVG},
    )

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:
            pytest.skip(f"Playwright Chromium is not installed: {exc}")

        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            console_errors = []
            page.on(
                "console",
                lambda message: console_errors.append(message.text)
                if message.type == "error"
                else None,
            )
            page.goto(live_server)
            expect(page.get_by_role("heading", name="No cards yet")).to_be_visible()
            page.screenshot(path=tmp_path / "empty.png", full_page=True)

            page.get_by_role("button", name="Import cards").first.click()
            expect(page.get_by_text("2 cards in deck")).to_be_visible()
            expect(page.get_by_text("Capital?")).to_be_visible()
            page.screenshot(path=tmp_path / "question.png", full_page=True)

            page.get_by_role("button", name="Reveal answer").click()
            expect(page.locator("#flashcard")).to_have_class(re.compile("is-flipped"))
            expect(page.get_by_text("Rome")).to_be_visible()
            page.screenshot(path=tmp_path / "answer.png", full_page=True)

            page.get_by_role("button", name="Correct", exact=True).click()
            page.get_by_role("button", name="Reveal answer").click()
            page.get_by_role("button", name="Incorrect", exact=True).click()
            expect(page.get_by_role("heading", name="Session complete")).to_be_visible()
            expect(page.locator("#summaryCorrect")).to_have_text("1")
            expect(page.locator("#summaryTotal")).to_have_text("2")
            expect(page.locator("#summaryPercent")).to_have_text("50%")
            page.screenshot(path=tmp_path / "summary.png", full_page=True)

            assert console_errors == []
        finally:
            browser.close()
