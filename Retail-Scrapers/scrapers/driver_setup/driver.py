import random, time, os
from typing import List, Optional
from logging import Logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium_stealth import stealth
import undetected_chromedriver as uc
from selenium.common.exceptions import (
    WebDriverException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    MoveTargetOutOfBoundsException,
    TimeoutException,
) 
import undetected_chromedriver as uc

class StealthBrowser:
    """
    A stealth-enabled Selenium wrapper that includes random delays, mouse movements, and typing to mimic human behavior.
    """

    def __init__(self, logger: Logger, proxies: Optional[List[str]] = None) -> None:
        """
        Initialize the StealthBrowser.

        Args:
            proxies (Optional[List[str]]): A list of proxy strings to randomly choose from.
            logger (Logger): A logger instance for logging.
        """
        self.logger = logger
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'        ]
        self.proxies = proxies or []
        self.driver = self.launch()

    def _get_random_user_agent(self) -> str:
        """
        Selects a random User-Agent string.

        Returns:
            str: A user agent string.
        """
        return random.choice(self.user_agents)

    def _get_random_proxy(self) -> Optional[str]:
        """
        Selects a random proxy from the provided list.

        Returns:
            Optional[str]: A proxy string or None.
        """
        return random.choice(self.proxies) if self.proxies else None

    def launch(self) -> uc.Chrome:
        """
        Launches the Chrome browser with stealth settings and optional proxy.

        Returns:
            webdriver.Chrome: The Selenium Chrome driver instance.
        """
        options = uc.ChromeOptions() or Options()
        ua = self._get_random_user_agent()
        proxy = self._get_random_proxy()

        flags = [
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "--disable-geolocation",
            "--disable-notifications",
            "--disable-media-stream",
            "--disable-popup-blocking",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--user-agent={ua}",
            "--lang=pt-BR",
            "--window-size=1920,1080",
            "--use-gl=angle",  # or "desktop"
            "--enable-webgl",
            "--ignore-gpu-blocklist",
            "--disable-software-rasterizer",

        ]
        for flag in flags:
            options.add_argument(flag)

        if proxy:
            options.add_argument(f"--proxy-server={proxy}")

        # self.driver = webdriver.Chrome(options=options)
        self.driver = uc.Chrome(options=options, use_subprocess=True)
        self._apply_stealth()
        return self.driver

    def _apply_stealth(self) -> None:
        """
        Applies stealth settings and fingerprint spoofing using `selenium-stealth`.
        """
        driver = self.driver
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        })

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": self._early_injection_script()
        })
        driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "America/Sao_Paulo"})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"}
        })

        stealth(driver,
                vendor="Google Inc.",
                webgl_vendor="Google Inc.",
                renderer="ANGLE (Intel, Intel(R) UHD Graphics 620, D3D11)",
                platform="Win32",
                fix_hairline=True,
                languages=["pt-BR", "en-US"],
                webgl=True)

    def _early_injection_script(self) -> str:
        """
        Loads a JavaScript file to inject early in the page lifecycle.

        Returns:
            str: JavaScript code as a string.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        injection_path = os.path.join(script_dir, "injection2.js")
        with open(injection_path, "r", encoding="utf-8") as f:
            return f.read()

    def _random_sleep(self, min_sec=0.1, max_sec=0.3) -> None:
        """
        Sleeps for a random time between min_sec and max_sec to simulate human-like delays.
        """
        time.sleep(random.uniform(min_sec, max_sec))


    def move_mouse_to_element(self, element: WebElement) -> None:
        """
        Safely scrolls to the element and moves the mouse to its center using a smooth path.
        """
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self._random_sleep(0.2, 0.4)
            size = element.size
            offset_x = size['width'] // 2
            offset_y = size['height'] // 2

            ActionChains(self.driver)\
                .move_to_element_with_offset(element, offset_x, offset_y)\
                .pause(random.uniform(0.1, 0.3))\
                .perform()

            self.logger.debug(f"Moved mouse to element at offset ({offset_x}, {offset_y}).")

        except MoveTargetOutOfBoundsException as e:
            self.logger.warning(f"Mouse move failed: Target out of bounds. {e}")
        except WebDriverException as e:
            self.logger.exception(f"WebDriver error while moving mouse: {e}")

    def human_click(self, element: WebElement) -> None:
        """
        Simulates a human-like click on a web element.
        """
        try:
            self.move_mouse_to_element(element)
            self._random_sleep(0.1, 0.3)
            element.click()
            self.logger.debug("Clicked element successfully.")
            self._random_sleep()
        except ElementClickInterceptedException as e:
            self.logger.warning(f"Click intercepted: {e}")
        except ElementNotInteractableException as e:
            self.logger.warning(f"Element not interactable: {e}")
        except WebDriverException as e:
            self.logger.exception(f"WebDriver error during click: {e}")

    def human_type(self, element: WebElement, text: str) -> None:
        """
        Simulates typing into an element with human-like delays.
        """
        try:
            self.move_mouse_to_element(element)
            self._random_sleep(0.2, 0.5)
            element.click()
            for char in text:
                element.send_keys(char)
                delay = random.uniform(0.05, 0.2)
                time.sleep(delay)
                self.logger.debug(f"Typed '{char}' with delay {delay:.2f}s")
            self._random_sleep()
            self.logger.debug(f"Finished typing: '{text}'")
        except ElementNotInteractableException as e:
            self.logger.warning(f"Cannot type into element: {e}")
        except WebDriverException as e:
            self.logger.exception(f"Typing failed due to WebDriver error: {e}")

    def human_scroll(self, pixels: int = 500) -> None:
        """
        Scrolls the page in a human-like way.
        """
        try:
            scroll_steps = random.randint(3, 6)
            scroll_chunk = pixels / scroll_steps
            for i in range(scroll_steps):
                self.driver.execute_script(f"window.scrollBy(0, {scroll_chunk});")
                self.logger.debug(f"Scrolled step {i+1}/{scroll_steps} by {scroll_chunk:.0f} pixels.")
                self._random_sleep(0.2, 0.5)
            self.logger.debug(f"Total scrolled: {pixels} pixels in {scroll_steps} steps.")
        except WebDriverException as e:
            self.logger.exception(f"Scroll failed due to WebDriver error: {e}")

    def quit(self) -> None:
        """
        Quits the browser session and cleans up.
        """
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser session terminated successfully.")
        except WebDriverException as e:
            self.logger.exception(f"Error during browser quit: {e}")
        finally:
            self.driver = None