from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import pandas as pd
import random
import wakepy
from urllib.parse import urljoin

BASE_URL = "https://www.masterswholesale.com"

mode = wakepy.keep.presenting()


#-----------------------------------------------------Personalization Variables---------------------------------------------------------------------#
url = "https://www.masterswholesale.com/catalog/special/manufacturer/jennair?srsltid=AfmBOooQ_5zSzBLkFme64gNXr24joyi5ncdVFvJn2y9B-AD5FMN5P86C"


#-----------------------------------------------------Do Not Modify if no changes are required------------------------------------------------------#

# Global Variables
next_page = None
links = []
products_data = []
main_headers = ["Link", "Name", "SKU", "Price", "Five Star", "Review Amount", "Image Link", 'Description', 'More Images Links', 'Videos Links'] 
#Links - test and speed process
real_links = "statics/product_link.csv"
#Outputs
real_output_path= 'outputs/JennAir/masters_wholesales.csv'
#other paths
old_file = 'statics/old_file.csv'
#Force run
no_file = "statics/no_file.csv"

def run()-> None:
    global next_page
    global products_data
    global links
    global main_headers
    global real_links
    global real_output_path
    global old_file
    global no_file
    #-------------------------------------------------------Driver CONFIGURATION-------------------------------------------------------------------------#
    chrome_options = Options()
    user_agents = [
        # Add your list of user agents here
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]
    user_agent = random.choice(user_agents)
    #-------------------------------------------------------Driver CONFIGURATION-------------------------------------------------------------------------#
    chrome_options = Options()
    # start the browser window in maximized mode
    chrome_options.add_argument("--start-maximized")
    # disable the AutomationControlled feature of Blink rendering engine
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-geolocation")
    chrome_options.add_argument("--disable-notifications")
    # disable pop-up blocking
    chrome_options.add_argument("--disable-popup-blocking")
    #run in incognito mode
    chrome_options.add_argument("--incognito")
    # disable extensions
    chrome_options.add_argument("--disable-extensions")
    #run in headless mode
    # chrome_options.add_argument("--headless") #improve efficiency, decrease trustability
    # disable sandbox mode
    # chrome_options.add_argument('--no-sandbox')
    # disable shared memory usage
    chrome_options.add_argument('--disable-dev-shm-usage')
    # rotate user agents 
    chrome_options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(options=chrome_options)

    # Change the property value of the navigator for webdriver to undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    stealth(driver,
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)


    #----------------------------------------------------------------Functions-------------------------------------------------------------------------#
    def item_adjust(item: str):
        item = item.replace(" ", ".")
        return item

    def process_product(driver, link):
        global products_data, main_headers
        driver.get(link)
        
        product_info = {'Link': link}
        
        # Obter informações do produto
        try:
            product_name_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            product_info['Name'] = product_name_element.text
        except Exception as e:
            product_info['Name'] = ""
            print("Error getting product name:", e)

        try:
            product_sku_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, item_adjust("h6")))
            )
            product_info['SKU'] = product_sku_element.text
        except Exception as e:
            product_info['SKU'] = ""
            print("Error getting product SKU:", e)

        try:
            product_image_link = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust('lazyload-wrapper')))
            )
            product_info['Image Link'] = product_image_link.get_dom_attribute('src')
        except Exception as e:
            product_info['Image Link'] = ""
            print("Error getting product image link:", e)

        try:
            
            five_star = driver.find_element(By.CLASS_NAME, item_adjust("MuiRating-root MuiRating-sizeLarge MuiRating-readOnly"))
            product_info['Five Star'] = five_star.text.replace(" Stars", "")
        except Exception as e:
            product_info['Five Star'] = ""
            print("Error getting five star rating:", e)

        try:
            review_amount = driver.find_element(
                By.XPATH, item_adjust('//*[@id="__next"]/div[4]/div/div[3]/div[1]/div[3]/div[2]/section/section/div[1]/button/span/span/span[3]')
            ).text.replace('(', '').replace(')', '')
            product_info['Review Amount'] = review_amount
        except Exception as e:
            product_info['Review Amount'] = ""
            print("Error getting review amount:", e)

        try:
            price = driver.find_element(By.TAG_NAME, "h3").text
            product_info['Price'] = price
        except Exception as e:
            product_info['Price'] = ""

        # Obter os comentários
        try:
            driver.find_element(By.XPATH, '//*[@id="product-overview-section"]/div/button[4]').click()
            outer_identifier_to_list = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust("MuiContainer-root MuiContainer-maxWidthXl")))
            )
            list_of_comments = outer_identifier_to_list.find_element(By.TAG_NAME, "ul")
            comments = list_of_comments.find_elements(By.TAG_NAME, "li")
            comment_obj = []

            for comment in comments:
                review = {
                    "Link": link,
                    "Product Name": product_info['Name'],
                    "SKU": product_info['SKU'],
                    "Image Link": product_info['Image Link'],
                    "Five Star": product_info['Five Star'],
                    "Review Amount": product_info['Review Amount'],
                    "Price": product_info['Price'],
                    "comment_id": comment.find_element(By.TAG_NAME, "div").text,
                    "comment_5_star": comment.find_element(By.CLASS_NAME, item_adjust("MuiRating-root MuiRating-readOnly")).get_dom_attribute("aria-label").replace(" Stars", ""),
                    "comment_date": comment.find_element(By.TAG_NAME, "h6").text,
                    "comment_title": comment.find_element(By.TAG_NAME, 'p').text,
                    "comment_text": comment.find_element(By.CLASS_NAME, item_adjust("MuiTypography-root MuiTypography-body2")).text,
                    "comment_sum": comment.find_element(By.CLASS_NAME, item_adjust('MuiTypography-root MuiTypography-subtitle2 MuiTypography-colorTextSecondary')).text,
                }
                comment_obj.append(review)

            # Adicionar as reviews à lista de dados do produto
            products_data.extend(comment_obj)

        except Exception as e:
            print("Error getting comments:", e)

    def process_products(driver):
        global links
        links = pd.Series(links).drop_duplicates().tolist()
        links = [link for link in links if link]  # Remover valores inválidos

        for idx, link in enumerate(links, start=1):
            if not link:  # Ignora valores inválidos
                print(f"Skipping invalid link at index {idx}, link: {link}")
                continue
            try:
                process_product(driver, link)
                print(f"Processing {idx}/{len(links)}: {link}")
            except Exception as e:
                print(f"Error getting into link:{link}\nReason: {e}")
                continue

        links.clear()

    # Start
    def scrape_page(driver):
        """
        Scrapes the current page for product links and returns the next page button if available.

        Returns:
            WebElement: The next page button element if found, otherwise None.
        """
        global links
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("Scrolled to bottom of the page.")

            tags = []
            try:
                products_outer = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH,'//*[@id="__next"]/div[4]/div/div[5]/div[3]/div[2]'))
                )
                try:
                    tags_web = products_outer.find_elements(By.TAG_NAME, 'a')
                    for tag_web in tags_web:
                        tags.append(tag_web.get_dom_attribute("href") if tag_web.get_dom_attribute("href") else None)
                    print("Found tag in product.")
                except NoSuchElementException as e:
                    print(f"Error finding tag in product: {e}")
                
                links = [urljoin(BASE_URL, tag) for tag in tags if tag]
            except Exception as e:
                print(f"Error finding products: {e}")

            print(f"Captured {len(links)} new links from the current page.")
            
            try:
                btn_next_page = driver.find_element(By.XPATH, '//*[@id="__next"]/div[4]/div/div[5]/div[3]/div[3]/div/div/button[8]')
            except NoSuchElementException:
                btn_next_page = None
            return btn_next_page

        except Exception as e:
            print("Unable to run the code, error:", e)

    global products_data
    try:
        driver.get(url)
        driver.implicitly_wait(20)  # Esperar o carregamento da página
        print("Page loaded.")

        try:
            # Carregar links existentes, se houver
            links = pd.read_csv(no_file)
            links = links["Product Links"].to_list()

            if links == None:
                while scrape_page(driver) is not None:
                    while True:
                        scrape_page(driver)
                        try:
                            next_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[4]/div/div[5]/div[3]/div[3]/div/div/button[8]'))
                            )
                            next_button.click()
                            print("Navigated to the next page.")
                        except NoSuchElementException:
                            print("No more pages to navigate.")
                            break
                        except Exception as e:
                            print("Error navigating to the next page:", e)
                            break
        except:
            while scrape_page(driver) is not None:
                while True:
                    scrape_page(driver)
                    try:
                        next_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[4]/div/div[5]/div[3]/div[3]/div/div/button[8]'))
                        )
                        next_button.click()
                        print("Navigated to the next page.")
                    except NoSuchElementException:
                        print("No more pages to navigate.")
                        break
                    except Exception as e:
                        print("Error navigating to the next page:", e)
                        break
        finally:
            # Salvar os links no CSV
            df = pd.DataFrame(links, columns=['Product Links'])
            df.to_csv(real_links, index=False)


    except Exception as e:
        print("Not able to run the code, error:", e)

    # Processar cada link
    process_products(driver)

    # Parar o scraping
    driver.quit()

    # Converter a lista de dicionários em um DataFrame
    df = pd.DataFrame(products_data)
    # Salvar o DataFrame atualizado
    df.to_csv(real_output_path, index=False)

    print(df.info())
with mode:
    run() 