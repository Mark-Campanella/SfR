from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import pandas as pd
import random
import wakepy
from urllib.parse import urljoin
import hashlib
import logging
import time

mode = wakepy.keep.presenting()

logging.basicConfig(filename='logs/product_scraper.log', level=logging.INFO, 
                format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
#-----------------------------------------------------Personalization Variables---------------------------------------------------------------------#
url = "https://www.appliancecanada.com/collections/jennair"


#-----------------------------------------------------Do Not Modify if no changes are required------------------------------------------------------#

# Global Variables
next_page = None
links = []
products_data = []
main_headers = ["Link", "Name", "SKU", "Price", "Five Star", "Review Amount", "Image Link", 'Description', 'More Images Links', 'Videos Links'] 
#Links - test and speed process
real_links = "statics/product_link.csv"
#Outputs
real_output_path= 'outputs/JennAir/CN_output.csv'
#other paths
old_file = 'statics/old_file.csv'
#Force run
no_file = "statics/no_file.csv"
BASE_URL = "https://www.appliancecanada.com"
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
    #chrome_options.add_argument("--headless") #improve efficiency, decrease trustability
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


    def get_product_meta_data(driver, product_info):
        """Helper function to extract product name and SKU"""
        try:
            outer = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, item_adjust("desc_blk"))))
            outer = outer.find_element(By.CLASS_NAME, item_adjust("row")).find_element(By.CLASS_NAME, item_adjust("col-xs-12"))
        except Exception as e:
            logger.error("Error getting product meta data: %s", e)
            return
        try:
            product_info_metas = WebDriverWait(outer, 2).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1")))
            product_info['Name'] = product_info_metas.text
            product_info['SKU'] = product_info_metas.text.split()[-1]
        except Exception as e:
            product_info['Name'] = ""
            product_info['SKU'] = ""
            logger.error("Error getting product name and SKU: %s", e)


    def get_product_image_link(driver, product_info):
        """Helper function to get product image link"""
        try:
            product_image_link = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust('abc'))))
            product_info['Image Link'] = product_image_link.get_dom_attribute('src')
        except Exception as e:
            product_info['Image Link'] = ""
            logger.error("Error getting product image link: %s", e)

    def get_product_price(driver, product_info):
        """Helper function to get product price"""
        try:
            price = driver.find_element(By.CLASS_NAME, item_adjust("money regPrice no-print")).text
            product_info['Price'] = price
        except Exception as e:
            product_info['Price'] = ""
            logger.error("Error getting price: %s", e)

    def get_product_reviews(driver, product_info):
        """Helper function to extract product reviews"""
        try:
            five_star = driver.find_element(By.CLASS_NAME, item_adjust("pr-snippet-stars pr-snippet-stars-png")).get_dom_attribute('aria-label')
            five_star = five_star.split()[1]
            product_info['Five Star'] = five_star
        except Exception as e:
            product_info['Five Star'] = ""
            logger.error("Error getting five star rating: %s", e)

        try:
            reviews = driver.find_element(By.CLASS_NAME, item_adjust("pr-snippet-review-count"))
            reviews_text = reviews.text
            product_info['Review Amount'] = reviews_text.split()[0]
        except Exception as e:
            product_info['Review Amount'] = ""
            logger.error("Error getting review amount: %s", e)
        
        try:
            reviews.click()
        except:
            logger.error("Error clicking on reviews")

    def extract_comment_data(comment, link, product_info):
        """Extracts and returns the necessary information from a single comment"""
        try:
            comment_id_text = comment.find_element(By.CLASS_NAME, item_adjust("pr-rd-details pr-rd-author-nickname")).text
            comment_id_hash = hashlib.sha256(comment_id_text.split()[-1].encode()).hexdigest()
        except NoSuchElementException:
            comment_id_hash = ""
            logger.error("Error getting comment id")

        try:
            comment_5_star = comment.find_element(
                    By.CLASS_NAME, item_adjust("pr-rd-star-rating")
                ).find_element(
                        By.CLASS_NAME,item_adjust("pr-snippet-stars pr-snippet-stars-png")
                    ).get_dom_attribute('aria-label').split()[1]
        except NoSuchElementException:
            comment_5_star = ""
            logger.error("Error getting comment 5 star rating")

        try:
            comment_date = comment.find_element(By.CLASS_NAME, item_adjust("pr-rd-details pr-rd-author-submission-date")).text
        except NoSuchElementException:
            comment_date = ""
            logger.error("Error getting comment date")

        try:
            comment_title = comment.find_element(By.CLASS_NAME, item_adjust("pr-rd-review-headline")).text
        except NoSuchElementException:
            comment_title = ""
            logger.error("Error getting comment title")

        try:
            comment_text = comment.find_element(By.CLASS_NAME, item_adjust("pr-rd-description-text")).text
        except NoSuchElementException:
            comment_text = ""
            logger.error("Error getting comment text")

        try:
            comment_sum = comment.find_element(By.CLASS_NAME, item_adjust('pr-rd-bottomline pr-rd-inner-content-block')).text
        except NoSuchElementException:
            comment_sum = ""
            logger.error("Error getting comment sum")

        return {
            "Link": link,
            "Product Name": product_info['Name'],
            "SKU": product_info['SKU'],
            "Image Link": product_info['Image Link'],
            "Five Star": product_info['Five Star'],
            "Review Amount": product_info['Review Amount'],
            "Price": product_info['Price'],
            "comment_id": comment_id_hash,
            "comment_5_star": comment_5_star,
            "comment_date": comment_date,
            "comment_title": comment_title,
            "comment_text": comment_text,
            "comment_sum": comment_sum,
        }
    def process_product(driver, link):
        
        global products_data
        driver.get(link)
        
        product_info = {'Link': link}
        
        # Get product meta data
        get_product_meta_data(driver, product_info)

        # Get product image link
        get_product_image_link(driver, product_info)

        # Get product price
        get_product_price(driver, product_info)

        get_product_reviews(driver, product_info)
        
        # Extract comments
        try:
            next_button_comment = driver.find_element(By.CLASS_NAME, item_adjust("pr-rd-pagination-btn pr-rd-pagination-btn--next"))
        except NoSuchElementException:
            next_button_comment = None
            logger.info("No more comments")

        try:
            outer_identifier_to_list = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.ID, item_adjust("pr-review-display"))))

            comments = outer_identifier_to_list.find_elements(By.CLASS_NAME, "pr-review")
            comment_obj = []
            for comment in comments:
                review = extract_comment_data(comment, link, product_info)
                comment_obj.append(review)
                products_data.append(review)

            # Pagination for comments
            while next_button_comment:
                logger.info(f"Getting comments - {len(comment_obj)}")
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button_comment)
                    driver.execute_script("arguments[0].click();", next_button_comment)
                    #next_button_comment.click()
                    WebDriverWait(driver, 4).until(
                        EC.presence_of_element_located((By.CLASS_NAME, item_adjust("pr-review-display"))))
                    
                    comments = outer_identifier_to_list.find_elements(By.CLASS_NAME, "pr-review")
                    for comment in comments:
                        review = extract_comment_data(comment, link, product_info)
                        comment_obj.append(review)
                        products_data.append(review)
                        print(review)

                    next_button_comment = driver.find_element(By.CLASS_NAME, item_adjust("pr-rd-pagination-btn pr-rd-pagination-btn--next"))
                except NoSuchElementException:
                    next_button_comment = None
                    logger.info("No more comments")
                    break
                except StaleElementReferenceException:
                    time.sleep(2)
                    next_button_comment = driver.find_element(By.CLASS_NAME, item_adjust("pr-rd-pagination-btn pr-rd-pagination-btn--next"))
                    continue
                except Exception as e:
                    logger.error("Error during comment pagination: %s", e)
                    break
        except Exception as e:
            logger.error("Error getting comments: %s", e)

    def process_products(driver):
        global links
        links = pd.Series(links).drop_duplicates().tolist()
        links = [link for link in links if link]  # Remover valores inválidos

        for idx, link in enumerate(links, start=1):
            if not link:  # Ignora valores inválidos
                logger.warning(f"Skipping invalid link at index {idx}, link: {link}")
                continue
            try:
                process_product(driver, link)
                logger.info(f"Processing {idx}/{len(links)}: {link}")
            except Exception as e:
                logger.error(f"Error getting into link:{link}\nReason: {e}")
                continue

        links.clear()

    def scrape_page(driver: webdriver.Chrome):
        """
        Scrapes the current page for product links, checks if new content is loaded,
        clicks the 'next page' button if available, and repeats until no more buttons are found.

        Returns:
            bool: True if scraping is successful, False otherwise.
        """
        global links

        def find_next_page_button():
            """Find the 'next page' button if available."""
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, item_adjust("findify-components--button findify-components-search--lazy-results__next-button")))
                )
                return driver.find_element(By.CLASS_NAME, item_adjust("findify-components--button findify-components-search--lazy-results__next-button"))
            except Exception as e:
                logger.info("No 'Next' page button found or timed out: %s", e)
                return None

        def capture_links():
            """Capture all product links from the current page."""
            try:
                products_outer = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, item_adjust("findify-components-common--grid")))
                )
                tags = []
                tags_web = products_outer.find_elements(
                    By.CLASS_NAME,
                    item_adjust("findify-components--cards--product product-banner-appcan current-banner-undefined status-available custom-findify-link")
                )
                for tag_web in tags_web:
                    tag_link = tag_web.get_dom_attribute("href")
                    if tag_link:
                        tags.append(urljoin(BASE_URL, tag_link))
                links.extend(tags)
                logger.info(f"Captured {len(tags)} new links from the current page.")
            except Exception as e:
                logger.error(f"Error capturing product links: {e}")

        def scroll_to_bottom():
            """Scroll to the bottom of the page until no new content is loaded."""
            previous_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                logger.info("Scrolled to the bottom of the page.")
                time.sleep(3)  # Wait for content to load
                current_height = driver.execute_script("return document.body.scrollHeight")
                if current_height == previous_height:
                    logger.info("No new content loaded. Breaking scroll loop.")
                    break
                previous_height = current_height

        try:
            while True:
                # Capture product links on the current page
                capture_links()

                # Scroll to load all content on the current page
                scroll_to_bottom()

                # Find and click the 'Next Page' button if it exists
                next_page_button = find_next_page_button()
                if next_page_button:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_page_button)
                        driver.execute_script("arguments[0].click();", next_page_button)
                        logger.info("Clicked the 'Next' page button.")
                        time.sleep(3)  # Wait for the next page to load
                    except Exception as e:
                        logger.error(f"Error clicking 'Next' page button: {e}")
                        break  # Exit the loop if the button click fails
                else:
                    logger.info("No more 'Next' page button. Stopping scraping.")
                    break  # Exit the loop if no button is found

            return True  # Successfully scraped all pages

        except Exception as e:
            logger.error(f"Unable to run scrape_page, error: {e}")
            print(f"Unable to run the code, error: {e}")
            return False

    global products_data
    try:
        driver.get(url)
        driver.implicitly_wait(20)  # Esperar o carregamento da página
        print("Page loaded.")

        try:
            # Carregar links existentes, se houver
            links = pd.read_csv(real_links).drop_duplicates()
            links = links["Product Links"].to_list()

            if links == None:
                scrape_page(driver)
                df = pd.DataFrame(links, columns=['Product Links']).drop_duplicates()
                df.to_csv(real_links, index=False)

        except FileNotFoundError:
            scrape_page(driver)
            df = pd.DataFrame(links, columns=['Product Links'])
            df.to_csv(real_links, index=False)

        
    except Exception as e:
        logger.error("Not able to run the code, error:", e)

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