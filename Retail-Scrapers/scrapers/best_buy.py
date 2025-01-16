import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import pandas as pd
from scrapers.routines.Laundry.bb_file_cleaner import cleanup
from scrapers.routines.Laundry.bb_merger import merge
import random
import logging
from datetime import datetime




#-----------------------------------------------------Personalization Variables---------------------------------------------------------------------#
url = "https://www.bestbuy.com/?intl=nosplash"


#-----------------------------------------------------Do Not Modify if no changes are required------------------------------------------------------#

class_search_bar = "search-input"
class_search_button = "header-search-button"

class_items = "sku-item"
class_next_button = "sku-list-page-next"


class_product_5_star = "ugc-c-review-average.font-weight-medium.order-1"
class_product_review_amount = "c-reviews.order-2"
class_product_sku = "product-data-value.body-copy"
class_product_img="primary-image.max-w-full.max-h-full"

class_product_price = "priceView-hero-price.priceView-customer-price"
class_product_price_btn_modal = "priceView-tap-to-view-price.priceView-tap-to-view-price-bold"
class_product_price_div_modal = 'restricted-pricing__regular-price-section'
class_product_price_innerdiv_modal = 'pricing-price'
class_product_price_btn_close_modal = "c-close-icon.c-modal-close-icon"

class_product_features_btn = "c-button-unstyled.features-drawer-btn.w-full.flex.justify-content-between.align-items-center.py-200"
class_product_features_seemore_btn = "c-button-unstyled.see-more-button.btn-link.bg-none.p-none.border-none.text-style-body-lg-500"
class_product_features_description_text = "description-text.lv.text-style-body-lg-400"
class_product_features_div_of_ul_li = "pdp-utils-product-info"

class_btn_more_images = 'image-button.align-items-center.bg-cover.bg-transparent.flex.flex-column.border-none.justify-center.p-none.relative.rounded-corners.align-items-center.bg-cover.bg-transparent.flex.flex-column.border-none.justify-center.p-none.relative.rounded-100.z-1'
class_div_images =  "c-tile.border.rounded.v-base.thumbnail-container"
class_div_btn_images = "image-button.align-items-center.bg-cover.bg-transparent.flex.flex-column.border-none.justify-center.p-none.relative"
class_videos_btn = 'tab-title.v-bg-pure-white.border-none.text-primary.heading-6.p-0.relative.t-1px.heading-6.v-fw-regular'
class_videos_list = 'thumbnail-content.inline-block.mr-150.inline-align-top.mb-300.w-full'
class_each_video_btn = 'video-image-button.align-items-center.bg-cover.bg-transparent.flex.flex-row.border-none.justify-center.p-none.relative'

class_show_full_specs = "c-button.c-button-outline.c-button-md.show-full-specs-btn.col-xs-6"
class_ul_item_specs = "zebra-stripe-list.inline.m-none.p-none"
class_li_item_specs = "zebra-list-item.mt-500"
class_div_each_spec = "zebra-row.flex.p-200.justify-content-between.body-copy-lg"
class_div_spec_type = "mr-100.inline"
class_div_spec_text = "w-full"

# Global Variables
next_page = None
links = []
products_data = []
main_headers = ["Link", "Name", "SKU", "Price", "Five Star", "Review Amount", "Image Link", 'Description', 'More Images Links', 'Videos Links'] 
#Links - test and speed process
test_links = "statics/test_product_link_BB.csv"
real_links = "statics/product_link_BB.csv"
#Outputs
test_output_path = 'outputs/Best_Buy/test_product_data.csv'
real_output_path= 'outputs/Best_Buy/product_data.csv'
#other paths
old_file = 'statics/old_file.csv'
#Force run
no_file = "statics/no_file.csv"

# Configure logging
current_date = datetime.now().strftime("%Y-%m-%d")
log_filename = f"logs/{current_date}_bb_scraping.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Logging is configured.")


def run(keywords:str)-> None:
    global next_page
    global products_data
    global links
    global main_headers
    global test_links
    global real_links
    global test_output_path
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
    chrome_options.add_argument("--headless") #improve efficiency, decrease trustability
    # disable sandbox mode
    chrome_options.add_argument('--no-sandbox')
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


    search_for = keywords
    #----------------------------------------------------------------Functions-------------------------------------------------------------------------#

    def handle_survey():
        try:
            # If survey is noticed then click the no button, else, continue
            no_thanks_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, "survey_invite_no"))
            )
            no_thanks_button.click()
            print("Survey dismissed")
            logger.info("Survey appeared and was dismissed")
        except:
            print("No survey popup")
            
    def scrape_page(driver):
        global links
        global next_page
        handle_survey()    
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Scrolled to bottom of the page.")
        try:
            elems = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, class_items)))
            print(f"Found {len(elems)} elements with class {class_items}.")
            logger.info(f"Found {len(elems)} elements with class {class_items}.")

            tags = [elem.find_element(By.TAG_NAME, "a") for elem in elems]
            links.extend([tag.get_attribute("href") for tag in tags])
            
            try:
                next_page = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_next_button))).get_attribute("href")
                print(f"Found next page: {next_page}")
                logger.info(f"Found next page: {next_page}")
            except:
                next_page = None
                print("No next page found.")
                logger.info("No next page found.")
                #save list of last scraped items, for threads usage later 
                df = pd.DataFrame(links, columns=['Product Links'])
                df = df.drop_duplicates()
                df.to_csv(real_links, index=False)
        except Exception as e:
            print("Error!! ", e)
            logger.error(f"Error: {e}")

    def process_product(driver, link):
        global products_data, main_headers
        driver.get(link)
        driver.implicitly_wait(20)
        handle_survey()

        product_info = {'Link': link}
        unwanteds = ["Package", "Stacking Kit", "sorry"]

        def log_error(section, error):
            print(f"Error in {section}: {error}")
            logger.error(f"Error in {section}: {error}")

        def get_element_text(by, identifier, section_name, timeout=20):
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, identifier))
                )
                return element.text
            except Exception as e:
                log_error(section_name, e)
                return "N/A"

        def get_element_attribute(by, identifier, attribute, section_name, timeout=20):
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, identifier))
                )
                return element.get_dom_attribute(attribute)
            except Exception as e:
                log_error(section_name, e)
                return "N/A"

        # Product Name
        product_info['Name'] = get_element_text(By.TAG_NAME, "h1", "Product Name")
        if any(unwanted in product_info['Name'] for unwanted in unwanteds):
            return

        # Product SKU
        product_info['SKU'] = get_element_text(By.CLASS_NAME, class_product_sku, "Product SKU")

        # Product Image
        product_info['Image Link'] = get_element_attribute(By.CLASS_NAME, class_product_img, 'src', "Product Image")

        # Product Reviews
        product_info['Five Star'] = get_element_text(By.CLASS_NAME, class_product_5_star, "Five Star Reviews", timeout=30)
        product_info['Review Amount'] = get_element_text(By.CLASS_NAME, class_product_review_amount, "Review Amount", timeout=30)
        
        # Product Comments Summary
        product_info['Comments Summary'] = get_element_text(By.CLASS_NAME, 'mb-200.mt-none', "Comments Summary", timeout=10)

        # Product Price
        try:
            price_div = driver.find_element(By.CLASS_NAME, class_product_price)
            product_info['Price'] = price_div.find_element(By.TAG_NAME, 'span').text
        except Exception as e:
            try:
                driver.find_element(By.CLASS_NAME,class_product_price_btn_modal).click()
                try:
                    price_div = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, class_product_price_div_modal))
                    )
                    price_div = price_div.find_element(By.CLASS_NAME, class_product_price_innerdiv_modal)
                    price_div = price_div.find_element(By.CLASS_NAME, class_product_price)
                    price = price_div.find_element(By.TAG_NAME, 'span').text
                    product_info['Price'] = price
                except Exception as e_text:
                    logger.error("Couldn't get the price because ", e_text)
                    product_info['Price'] = ""
                        #I was having problem to click in the button, this is an atomic bomb, I know
                try:
                    #Uses Selenium to click
                    close_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, class_product_price_btn_close_modal))
                    )
                    close_btn.click()
                except Exception as e:
                    print(f"Error clicking close button: {e}")
                    try:
                        # Uses JS to click
                        driver.execute_script("arguments[0].click();", close_btn)
                    except Exception as js_e:
                        print(f"Error clicking close button with JS: {js_e}")
                        try:
                            #Just refresh if everything fails
                            driver.refresh()
                        except Exception as all_e:
                            print("Error in all atempts to click in the close button: ", all_e)
            except: logger.error("Couldn't close the modal nand/nor get the price properly")

        # More Product Images
        inner_div_more_images = []
        btn_images = []
        images = []
        try:
            btn_more_images = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, class_btn_more_images)))
            btn_more_images.click()
            try:
                div_ol_more_images = driver.find_element(By.CLASS_NAME,'carousel-indicate.flex.flex-row.flex-wrap')
                try:
                    div_li_more_images = div_ol_more_images.find_elements(By.CLASS_NAME,'thumbnail-content.inline-block.mr-150.mb-150.inline-align-top')
                    try:
                        for each_li in div_li_more_images:
                            inner_div_more_images.append(each_li.find_element(By.CLASS_NAME,class_div_images))
                        for each_div_more_images in inner_div_more_images:
                            btn_images.append(each_div_more_images.find_element(By.TAG_NAME, 'button'))
                        for each_btn in btn_images:
                            try:
                                images.append(each_btn.find_element(By.TAG_NAME,'img').get_attribute('src'))
                            except: pass
                        product_info['More Images Links'] = images  
                    except Exception as e: 
                        product_info['More Images Links'] = "N/A"
                        print("Error getting More Images could not get the div, or buttons, or image of each image", e)
                except Exception as e:
                    product_info['More Images Links'] = "N/A"
                    print("Error getting More Images could not get the <li>s", e)    
            except Exception as e:       
                product_info['More Images Links'] = "N/A"
                print("Error getting More Images could not get the <ol>", e) 
        except Exception as e: 
            product_info['More Images Links'] = "N/A"
            logger.error("Error getting More Images, could not click in the more images button", e)

        # Product Videos
        try:
            videos=[]
            button_list = []
            btn_videos = driver.find_element(By.CLASS_NAME, class_videos_btn)
            btn_videos.click()
            try:    
                list_of_videos = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME,class_videos_list)))      
                try:
                    for item in list_of_videos:
                        button_list.append(item.find_element(By.CLASS_NAME,class_each_video_btn))
                    try:
                        for button in button_list:
                            try:
                                button.click()
                                video = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.TAG_NAME,'source'))).get_attribute('src')
                                videos.append(video)
                            except:
                                pass
                        product_info['Videos Links'] = videos
                    except Exception as e: print("Could not get the buttons or the videos", e)
                except Exception as e: print("Could not get the list of videos", e)
            except Exception as e: print("Could not find the video button, error: ", e)              
        except Exception as e:
            product_info['Videos Links'] = "N/A"
            print("Error getting Videos Links:", e)    
        try: 
            driver.find_element(By.CLASS_NAME,"c-close-icon.c-modal-close-icon").click()
        except Exception as e:
            print("Couldn't click quit button, refreashing...")
            driver.refresh()

        # Description and Features
        try:
            description_features = []
            try:
                features_btn = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_product_features_btn))
                )
                try:
                    features_btn.click()
                except:
                    driver.execute_script("arguments[0].click();", features_btn)
            except Exception as e:
                log_error("Features Button", e)

            features_description = get_element_text(By.CLASS_NAME, class_product_features_description_text, "Features Description")
            if features_description:
                description_features.append(features_description)

            div = driver.find_element(By.CLASS_NAME, class_product_features_div_of_ul_li)
            ul = div.find_element(By.TAG_NAME, 'ul')
            features = ul.find_elements(By.TAG_NAME, 'li')
            for feature in features:
                try:
                    h4 = feature.find_element(By.TAG_NAME, 'h4').text or f"Unnamed Feature"
                    p = feature.find_element(By.TAG_NAME, 'p').text
                    description_features.append(f"{h4}: {p}")
                except Exception as e:
                    log_error("Feature Extraction", e)

            product_info['Description'] = "\n".join(description_features) or "N/A"
        except Exception as e:
            log_error("Description and Features", e)
            product_info['Description'] = "N/A"

        # Energy Guide
        product_info['Energy Guide'] = get_element_attribute(By.CLASS_NAME, 'c-button-link.energy-guide-link.ml-150', 'href', "Energy Guide")

        # User Manual and Spec Sheet
        try:
            documents = driver.find_elements(By.CLASS_NAME, 'manual-link.body-copy-lg')
            product_info['User Manual'] = documents[0].get_attribute('href') if len(documents) > 0 else "N/A"
            product_info['Spec Sheet'] = documents[1].get_attribute('href') if len(documents) > 1 else "N/A"
        except Exception as e:
            log_error("Manual and Spec Sheet", e)
            product_info['User Manual'], product_info['Spec Sheet'] = "N/A", "N/A"

        # Add to global data
        products_data.append(product_info)
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------GET SPECS
        try:
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, class_show_full_specs))).click()
        except Exception as e:
            print("Couldn't click show full specs button:", e)
        
        try:
            list_of_specs_ul = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, class_ul_item_specs))
            )

            for each_item in list_of_specs_ul:
                try:
                    spec_items = each_item.find_elements(By.CLASS_NAME, class_div_each_spec)
                    for spec_item in spec_items:
                        header = spec_item.find_element(By.CLASS_NAME, class_div_spec_type).text
                        #I could not find a way of getting the spec text with CSS Classes
                        #Then I could fetch by XPATH on a generic mode
                        spec = spec_item.find_element(By.XPATH, ".//div[contains(@class, 'w-full') and not(contains(@class, 'mr-200'))]").text
                        product_info[header] = spec
                        if header not in main_headers:
                            main_headers.append(header)
                            
                except Exception as e:
                    print(f"Error extracting specification: {e}")
                    continue
                
        except Exception as e:
            print(f"Error occurred while getting specifications: {e}")
            
        print(f'COMPLETE SPEC ADDED:{product_info}\n')
        products_data.append(product_info)

    def process_products(driver):
        '''
        Process each link and clean the variable right after.
        \nDROP DUPLICATES → There are quite a lot of sponsored data
        '''
        
        global links
        links = pd.Series(links).drop_duplicates().tolist()
        for link in links: 
            process_product(driver, link)
            print(f'Processing: {links.index(link)+1}/{len(links)}')
        links.clear()

    #---------------------------------------------------------------------------Begining---------------------------------------------------------------------#
    global products_data
    try:        
        driver.get(url)
        handle_survey()
        driver.implicitly_wait(20)  # Wait for it to load
        print("Page loaded.")
        logger.info("Page loaded.")
        search = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_search_bar)))
        search.send_keys(search_for)
        
        time.sleep(2)
        
        button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, class_search_button)))
        button.click()
        
        driver.implicitly_wait(20)  # Wait for it to load

        '''
        This section is useful for test purposes
            You need to uncomment and fix indentation, also look at the code below, might be useful
        '''
        try:
            #If exists, run based on the links given
            links = pd.read_csv(no_file)
            links = links["Product Links"].to_list()
            
            #If no links in the file, execute the routine
            if links == None:
                i=1
                while True:
                    print("Scraping page: ",i)
                    handle_survey()
                    scrape_page(driver)
                    if next_page: 
                        i+=1
                        driver.get(next_page)
                        print(f"Navigating to next page: {next_page}: {i}")
                        logger.info(f"Navigating to next page: {next_page}: {i}")
                    else: 
                        break
        #If file doesn't exist, run routine to get it and save it later
        except:
            i=1
            while True:
                print("Scraping page: ",i)
                handle_survey()
                scrape_page(driver)
                if next_page: 
                    i+=1
                    driver.get(next_page)
                    print(f"Navigating to next page: {next_page}: {i}")
                    logger.info(f"Navigating to next page: {next_page}: {i}")
                else: 
                    break
        
    except Exception as e:
        print("Not able to run the code, error: ", e)
        logger.error(f"Not able to run the code, error: {e}")
    df_links = pd.DataFrame(links, columns=['Product Links'])
    df_links = df_links.drop_duplicates()
    df_links.to_csv(real_links, index=False)
    #for each link get product info
    process_products(driver)

    #stop scraping
    driver.quit()


    try:
        print(products_data)
    except Exception as e:
        print(e)
        
    # Convert the list of dictionaries into a dataframe
    df = pd.DataFrame(products_data)
            
    # Cleanup and Merge/Reorder Routines are going to be called. 
    # Keeping a copy of df to be safe
    df_save = df.copy()
    #Now we have the df with updated info
    try:
        df = cleanup(df)
    except Exception as e:
        print("Not able to cleanup, ", e)
        logger.error(f"Not able to cleanup, {e}")
        df = df_save
    try:
        df = merge(df)
    except Exception as e:
        print("Not able to merge with the SAS VA and Traqline's SKU data")
        logger.error(f"Not able to merge with the SAS VA and Traqline's SKU data, {e}")
        
    #Get last scraped information
    try:
        df_old = pd.read_csv(old_file)
    except FileNotFoundError as e:
        print ("Not able to locate file: ",e)
        logger.error(f"Not able to locate file: {e}")
    except Exception as e:
        print("Error: ", e)
        logger.error(f"Error: {e}")
        
    #compare the SKU to see if there were models coming in and out 
    try:

        # See SKUs removed → if in old but not in new then the item was removed
        removed_skus = df_old[~df_old['SKU'].isin(df['SKU'])].copy()
        
        # See SKUs added → if in new but not in old then the item was added
        added_skus = df[~df['SKU'].isin(df_old['SKU'])].copy()
        
        # Exports
        added_skus.to_csv('outputs/Best_Buy/added_models.csv', index=False)
        removed_skus.to_csv('outputs/Best_Buy/removed_models.csv', index=False)
        
    except Exception as e:
        print("Not able to detect changes! Something went wrong: ",e)
        logger.error(f"Not able to detect changes! Something went wrong: {e}")
        
    finally:
        # Save the updated DataFrame
        df.to_csv(real_output_path, index=False)
        
    print(df.info())


    # Cleaning up all variables that might get "polluted" in next iteration
    # Lists
    products_data = []
    links = []
    # DataFrames
    df = pd.DataFrame()
    df_save = pd.DataFrame()
    df_old = pd.DataFrame()
    added_skus = pd.DataFrame()
    removed_skus = pd.DataFrame()

