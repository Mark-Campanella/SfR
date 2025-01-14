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
import hashlib
import logging

mode = wakepy.keep.presenting()

logging.basicConfig(filename='logs/product_scraper.log', level=logging.INFO, 
                format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
#-----------------------------------------------------Personalization Variables---------------------------------------------------------------------#
url = "https://www.canadianappliance.ca/s.php?&q=jennair&brand_id%5B%5D=21&range_start=201&per_page=&"


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
BASE_URL = "https://www.canadianappliance.ca"
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


    def get_product_meta_data(driver, product_info, link):
        """Helper function to extract product name and SKU"""
        try:
            product_info_metas = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust("product-info row"))))
            metas_elements = product_info_metas.find_elements(By.TAG_NAME, "meta")
            for meta in metas_elements:
                if meta.get_dom_attribute("itemprop") == "name":
                    product_info['Name'] = meta.get_dom_attribute("content")
                elif meta.get_dom_attribute("itemprop") == "sku":
                    product_info['SKU'] = meta.get_dom_attribute("content")
        except Exception as e:
            product_info['Name'] = ""
            product_info['SKU'] = ""
            logger.error("Error getting product name and SKU: %s", e)


    def get_product_image_link(driver, product_info):
        """Helper function to get product image link"""
        try:
            product_image_link = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust('enlarge img-box'))))
            product_info['Image Link'] = urljoin(BASE_URL, product_image_link.get_dom_attribute('href'))
        except Exception as e:
            product_info['Image Link'] = ""
            logger.error("Error getting product image link: %s", e)


    def get_product_reviews(driver, link, product_info):
        """Helper function to extract product reviews"""
        try:
            five_star = driver.find_element(By.CLASS_NAME, item_adjust("avg-rating"))
            product_info['Five Star'] = five_star.text
        except Exception as e:
            product_info['Five Star'] = ""
            logger.error("Error getting five star rating: %s", e)

        try:
            reviews = driver.find_element(By.CLASS_NAME, item_adjust("pd-reviews-recommend"))
            review_amount = reviews.find_elements(By.TAG_NAME, 'div')[-1].text.replace("(", "").replace(")", "").replace(" reviews", "")
            product_info['Review Amount'] = review_amount
        except Exception as e:
            product_info['Review Amount'] = ""
            logger.error("Error getting review amount: %s", e)


    def get_product_price(driver, product_info):
        """Helper function to get product price"""
        try:
            price = driver.find_element(By.CLASS_NAME, "strikeout").text
            product_info['Price'] = price
        except Exception as e:
            product_info['Price'] = ""
            logger.error("Error getting price: %s", e)


    def get_general_recommendation(driver, reviews, product_info):
        """Helper function to get general recommendation"""
        try:
            general_recommendation = WebDriverWait(reviews, 20).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div[2]/div[2]/div[2]/div/div/div[5]/div[3]/div[2]")))
            product_info['Recommendation'] = general_recommendation.text
        except Exception as e:
            product_info['Recommendation'] = ""
            logger.error("Error getting general recommendation: %s", e)


    def extract_comment_data(comment, link, product_info):
        """Extracts and returns the necessary information from a single comment"""
        try:
            comment_id_text = comment.find_element(By.CLASS_NAME, "pr-rd-bold").text
            comment_id_hash = hashlib.sha256(comment_id_text.encode()).hexdigest()
        except NoSuchElementException:
            comment_id_hash = ""
            logger.error("Error getting comment id")

        try:
            comment_5_star = comment.find_element(By.CLASS_NAME, item_adjust("pr-rd-star-rating")).text
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
        get_product_meta_data(driver, product_info, link)

        # Get product image link
        get_product_image_link(driver, product_info)

        # Get product reviews and price
        get_product_reviews(driver, link, product_info)
        get_product_price(driver, product_info)

        try:
            reviews = driver.find_element(By.CLASS_NAME, item_adjust("pd-reviews-recommend"))
            get_general_recommendation(driver, reviews, product_info)
        except Exception as e:
            logger.error("Error getting general recommendation: %s", e)

        # Extract comments
        try:
            next_button_comment = driver.find_element(By.CLASS_NAME, item_adjust("pr-rd-pagination-btn pr-rd-pagination-btn--next"))
        except NoSuchElementException:
            next_button_comment = None
            logger.info("No more comments")

        try:
            comments_btn = driver.find_element(By.CLASS_NAME, 'pr-button')
            driver.execute_script("arguments[0].scrollIntoView(true);", comments_btn)
            driver.execute_script("arguments[0].click();", comments_btn)


            outer_identifier_to_list = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust("pr-review-display"))))

            comments = outer_identifier_to_list.find_elements(By.CLASS_NAME, "pr-review")
            comment_obj = []
            for comment in comments:
                review = extract_comment_data(comment, link, product_info)
                comment_obj.append(review)
                products_data.append(review)

            # Pagination for comments
            while next_button_comment:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button_comment)
                    driver.execute_script("arguments[0].click();", next_button_comment)
                    next_button_comment.click()
                    WebDriverWait(driver, 4).until(
                        EC.presence_of_element_located((By.CLASS_NAME, item_adjust("pr-review-display"))))
                    
                    comments = outer_identifier_to_list.find_elements(By.CLASS_NAME, "pr-review")
                    for comment in comments:
                        review = extract_comment_data(comment, link, product_info)
                        comment_obj.append(review)
                        products_data.append(review)

                    next_button_comment = driver.find_element(By.CLASS_NAME, item_adjust("pr-rd-pagination-btn pr-rd-pagination-btn--next"))
                except NoSuchElementException:
                    next_button_comment = None
                    logger.info("No more comments")
                    break
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

    # Start
    def scrape_page(driver: webdriver.Chrome):
        """
        Scrapes the current page for product links and returns the next page button if available.

        Returns:
            WebElement: The next page button element if found, otherwise None.
        """
        global links
        global next_page
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("Scrolled to bottom of the page.")

            tags = []
            try:
                products_outer = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME,item_adjust("pi-products")))
                )
                try:
                    tags_web = products_outer.find_elements(By.CLASS_NAME, item_adjust("product-tile tile-container"))
                    for tag_web in tags_web:
                        tags.append(tag_web.get_dom_attribute("data-href") if tag_web.get_dom_attribute("data-href") else None)
                    logger.debug("Found tag in product.")
                except NoSuchElementException as e:
                    logger.error(f"Error finding tag in product: {e}")
                
                links.extend(tags)
            except Exception as e:
                logger.error(f"Error finding products: {e}")

            logger.info(f"Captured {len(links)} new links from the current page.")
            try:
                next_page_button = driver.find_element(By.CLASS_NAME, item_adjust("pagination")).find_element(By.XPATH, '//a[@title="next page" and @rel="next"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", next_page_button)
                driver.execute_script("arguments[0].click();", next_page_button)
                next_page = True
            except NoSuchElementException:
                next_page = False
            except NoSuchElementException:
                next_page = False
            return next_page
        except Exception as e:
            logger.error(f"Unable to run the code at scrape_page, error: {e}")
            print("Unable to run the code, error:", e)
            return False

    global products_data
    try:
        driver.get(url)
        driver.implicitly_wait(20)  # Esperar o carregamento da página
        print("Page loaded.")

        # try:
        #     # Carregar links existentes, se houver
        #     links = pd.read_csv(no_file)
        #     links = links["Product Links"].to_list()

        #     if links == None:
        next_page = True
        while next_page:
            next_page = scrape_page(driver)
        # except:
        #         while next_page:
        #             next_page = scrape_page(driver)
        # finally:
            # Salvar os links no CSV
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