import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from selenium.webdriver.common.keys import Keys

def mimic(driver):
    actions = ActionChains(driver)
    
    behaviors = [
        "scroll",
        "move_mouse",
        "key_press",
        "click",
        "pause"
    ]
    
    selected_behaviors = random.sample(behaviors, random.choice([1, 2]))  # 1 ou 2 ações aleatórias
    
    if "scroll" in selected_behaviors:
        scroll_height = random.randint(300, 1500)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(1, 3))

    if "move_mouse" in selected_behaviors:
        screen_width = driver.execute_script("return window.innerWidth")
        screen_height = driver.execute_script("return window.innerHeight")
        mouse_x = random.randint(0, screen_width)
        mouse_y = random.randint(0, screen_height)
        actions.move_by_offset(mouse_x, mouse_y).perform()
        time.sleep(random.uniform(1, 3))

    if "key_press" in selected_behaviors:
        random_key = random.choice([Keys.TAB, Keys.ENTER, Keys.ARROW_DOWN, Keys.ARROW_UP])
        current_url = driver.current_url
        actions.send_keys(random_key).perform()
        time.sleep(random.uniform(1, 2))
        if driver.current_url != current_url:
            print("Página mudou. Retornando...")
            driver.back()
            time.sleep(random.uniform(1, 3))

    if "click" in selected_behaviors:
        clickable_elements = driver.find_elements(By.CSS_SELECTOR, 'a, button, [role="button"]')
        if clickable_elements:
            element = random.choice(clickable_elements)
            current_url = driver.current_url
            element.click()
            time.sleep(random.uniform(1, 3))
            if driver.current_url != current_url:
                print("Página mudou. Retornando...")
                driver.back()
                time.sleep(random.uniform(1, 3))

    if "pause" in selected_behaviors:
        time.sleep(random.uniform(2, 5))

# Configuração do Chrome Options
chrome_options = uc.ChromeOptions()
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
]
user_agent = random.choice(user_agents)
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-geolocation")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument(f'user-agent={user_agent}')    

# Inicializando o driver
driver = uc.Chrome(options=chrome_options)


driver.request_interceptor = lambda request: request.headers.update({
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.lowes.com"
})

# Alterando o comportamento de navegadores
driver.execute_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    Object.defineProperty(navigator, 'plugins', {get: () => [{name: 'Chrome PDF Viewer'}, {name: 'Native Client'}]});
""")
driver.set_page_load_timeout(30)
# Usando stealth para evitar a detecção de automação
stealth(driver, vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

# Navegar e tirar captura de tela
driver.get("https://www.lowes.com/search?searchTerm=front+load+washer")
try:
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "title")))
    mimic(driver)  # Ações aleatórias
    screenshot = driver.get_screenshot_as_png()
    with open("lowes_screenshot.png", "wb") as f:
        f.write(screenshot)
    print("Captura de tela salva com sucesso!")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
finally:
    driver.quit()
