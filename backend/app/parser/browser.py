import os
import xvfbwrapper
from playwright.sync_api import sync_playwright


class Browser:
    """Управление виртуальным дисплеем и браузером (Playwright + Xvfb)."""

    def __init__(
        self,
        headless: bool = True,
        viewport: dict = None,
        locale: str = "ru-RU",
        timezone: str = "Europe/Moscow",
    ):
        self.headless = headless
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.locale = locale
        self.timezone = timezone

        self._vdisplay = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    def start(self):
        """Запускает Xvfb и браузер, возвращает page."""
        if not self.headless and os.name == "posix":
            print("🖥️  Запускаем виртуальный дисплей...")
            self._vdisplay = xvfbwrapper.Xvfb(
                width=1920, height=1080, colordepth=24
            )
            self._vdisplay.start()

        print("🌐 Запускаем Chrome...")
        self._playwright = sync_playwright().start()

        launch_args = []
        if not self.headless and self._vdisplay:
            launch_args.append(f"--display=:{self._vdisplay.new_display}")

        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            channel='chrome',
            args=launch_args,
            )

        self._context = self._browser.new_context(
            viewport=self.viewport,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            locale=self.locale,
            timezone_id=self.timezone,
        )

        self._page = self._context.new_page()
        return self._page

    @property
    def page(self):
        return self._page

    def stop(self):
        """Закрывает браузер и виртуальный дисплей."""
        try:
            if self._page:
                self._page.close()
        except Exception:
            pass
        try:
            if self._context:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        try:
            if self._vdisplay:
                self._vdisplay.stop()
        except Exception:
            pass
        print("🖥️  Браузер остановлен")