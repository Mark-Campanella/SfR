import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException
from selenium_stealth import stealth
import pandas as pd
from scrapers.routines.Laundry.bb_file_cleaner import cleanup
from scrapers.routines.Laundry.bb_merger import merge
import random
import logging
from datetime import datetime
import undetected_chromedriver as uc




#-----------------------------------------------------Personalization Variables---------------------------------------------------------------------#
url = "https://www.bestbuy.com/?intl=nosplash"


#-----------------------------------------------------Do Not Modify if no changes are required------------------------------------------------------#


class_search_bar = "search-input"
class_search_button = "header-search-button"

class_items = "product-list-item"
class_pagination_btns = "pagination-arrow"


class_product_5_star = "font-weight-medium.font-weight-bold.order-1"
class_product_review_amount = "c-reviews.order-2"
class_product_sku = "pr-150.inline-block"
class_product_img="flex jfGDjp1H5YP6xBJc align-items-center m-auto object-contain px-50".replace(" ",".")

class_product_price = "customer-price.large_Pdp.text-8.font-500.leading-8.text-default-fixed.large-price.text-6.leading-6"
id_product_price_btn_modal = "restricted-price"
class_product_price_div_modal = 'restricted-pricing__regular-price-section'
class_product_price_innerdiv_modal = 'pricing-price'
class_product_price_btn_close_modal = "c-close-icon.c-modal-close-icon"
class_comments_summary = "mt-200.body-copy-lg.mb-none"

class_product_features_btn = "c-button-unstyled font-weight-medium w-full flex justify-content-between align-items-center ZjQDoW6pq08UwL3A".replace(" ",".")
class_product_features_seemore_btn = "c-button-link text-3 mt-25 font-500".replace(" ",".")
class_product_features_description_text = "text-style-body-lg-400 m-none whitespace-pre-wrap leading-5".replace(" ",".")
class_product_features_div_of_ul_li = "pl-300".replace(" ",".")
class_close_features_btn = "relative border-xs justify-center items-center flex flex-row bg-comp-surface-transparent border-transparent p-0 w-300 h-300 border-none rounded-md cursor-pointer z-50 self-start grow-0".replace(" ",".")

class_btn_more_images = 'c-button-unstyled flex m-auto h-800 w-800 rounded'.replace(" ",".")
class_ul_more_imgs = 'c-carousel-list.scrollable'
class_videos_btn = 'relative border-xs border-solid items-center box-border inline-flex cursor-pointer shrink-0 py-50 min-h-400 border-comp-outline-default-muted bg-transparent rounded-full px-200'.replace(" ",".")
class_videos_list = 'item.c-carousel-item '
class_each_video_btn = 'video-image-button.align-items-center.bg-cover.bg-transparent.flex.flex-row.border-none.justify-center.p-none.relative'

class_show_full_specs = "c-button c-button-outline c-button-md show-full-specs-btn col-xs-6".replace(" ",".")
class_list_item_specs = "grow p-200 pt-100 md__p-300 md__pt-200".replace(" ",".")
class_div_each_spec = "dB7j8sHUbncyf79K inline-flex w-full body-copy-lg".replace(" ",".")
class_div_spec_header = "grow basis-none font-weight-medium".replace(" ",".")
class_div_spec_text = "grow basis-none pl-300".replace(" ",".")

class_btn_see_all_reviews = "relative border-xs border-solid rounded-lg justify-center items-center self-start flex flex-row cursor-pointer px-300 py-100 border-comp-outline-primary-emphasis bg-comp-surface-primary-emphasis mr-200 Op9coqeII1kYHR9Q".replace(" ",".")


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



def run(keywords:str)-> None:
    # Configure logging
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"logs/{current_date}_bb_scraping.log"
    logging.basicConfig(filename=log_filename, level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    logger.info("Logging is configured.")

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

    chrome_options = Options()
    # start the browser window in maximized mode
    chrome_options.add_argument("--start-maximized")
    # disable the AutomationControlled feature of Blink rendering engine
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-geolocation")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-media_stream")

    # disable pop-up blocking
    chrome_options.add_argument("--disable-popup-blocking")
    #run in incognito mode
    chrome_options.add_argument("--incognito")
    # disable extensions
    chrome_options.add_argument("--disable-extensions")
    #run in headless mode
    # chrome_options.add_argument("--headless") #improve efficiency, decrease trustability
    # chrome_options.add_argument("--window-size=1920,1080")
    # disable sandbox mode
    chrome_options.add_argument('--no-sandbox')
    # disable shared memory usage
    chrome_options.add_argument('--disable-dev-shm-usage')
    # rotate user agents
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--lang=pt-BR")

    driver = uc.Chrome(options=chrome_options)
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
            
    def scrape_page(driver: webdriver.Chrome):
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
                pagination_elements = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, class_pagination_btns)))
                for element in pagination_elements:
                    if element.get_dom_attribute('arial-label') =="Next page":
                        next_page = element.get_dom_attribute('href')
                        break
                if next_page is None: raise NoSuchElementException("Next page element not found.")
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

    def process_product(driver: webdriver.Chrome, link):
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
        element = driver.find_elements(By.CLASS_NAME,class_product_sku)[0]
        product_info['SKU'] = element.text.replace('Model: ', "").strip()
        # product_info['SKU'] = get_element_text(By.CLASS_NAME, class_product_sku, "Product SKU")

        # Product Image
        product_info['Image Link'] = get_element_attribute(By.CLASS_NAME, class_product_img, 'src', "Product Image")

        # Product Reviews
        product_info['Five Star'] = get_element_text(By.CLASS_NAME, class_product_5_star, "Five Star Reviews", timeout=30)
        product_info['Review Amount'] = get_element_text(By.CLASS_NAME, class_product_review_amount, "Review Amount", timeout=30)
        
        # Product Comments Summary
        product_info['Comments Summary'] = get_element_text(By.CLASS_NAME, class_comments_summary, "Comments Summary", timeout=10)

        # Product Price
        try:
            price_div = driver.find_element(By.CLASS_NAME, class_product_price)
            product_info['Price'] = price_div.text
            # product_info['Price'] = price_div.find_element(By.TAG_NAME, 'span').text
        except Exception as e:
            product_info['Price'] = "N/A"
            # try:
            #     driver.find_element(By.ID,id_product_price_btn_modal).click()
            #     try:
            #         price_div = WebDriverWait(driver, 5).until(
            #             EC.presence_of_element_located((By.CLASS_NAME, class_product_price_div_modal))
            #         )
            #         price_div = price_div.find_element(By.CLASS_NAME, class_product_price_innerdiv_modal)
            #         price_div = price_div.find_element(By.CLASS_NAME, class_product_price)
            #         price = price_div.find_element(By.TAG_NAME, 'span').text
            #         product_info['Price'] = price
            #     except Exception as e_text:
            #         logger.error("Couldn't get the price because ", e_text)
            #         product_info['Price'] = ""
            #             #I was having problem to click in the button, this is an atomic bomb, I know
            #     try:
            #         #Uses Selenium to click
            #         close_btn = WebDriverWait(driver, 3).until(
            #             EC.element_to_be_clickable((By.CLASS_NAME, class_product_price_btn_close_modal))
            #         )
            #         close_btn.click()
            #     except Exception as e:
            #         print(f"Error clicking close button: {e}")
            #         try:
            #             # Uses JS to click
            #             driver.execute_script("arguments[0].click();", close_btn)
            #         except Exception as js_e:
            #             print(f"Error clicking close button with JS: {js_e}")
            #             try:
            #                 #Just refresh if everything fails
            #                 driver.refresh()
            #             except Exception as all_e:
            #                 print("Error in all atempts to click in the close button: ", all_e)
            # except: logger.error("Couldn't close the modal nand/nor get the price properly")

        # More Product Images
        images = [str]
        try:
            btn_more_images = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, class_btn_more_images)))
            btn_more_images.click()
            try:
                ul_more_images = driver.find_element(By.CLASS_NAME,class_ul_more_imgs)
                try:
                    img_more_images = ul_more_images.find_elements(By.TAG_NAME,'img')
                    try:
                        for img in  img_more_images:
                            images.append(img.get_dom_attribute("srcset"))
                        product_info['More Images Links'] = images  
                    except Exception as e: 
                        product_info['More Images Links'] = "N/A"
                        print("Error getting More Images could not get the div, or buttons, or image of each image", e)
                except Exception as e:
                    product_info['More Images Links'] = "N/A"
                    print("Error getting More Images could not get the <img>s", e)    
            except Exception as e:       
                product_info['More Images Links'] = "N/A"
                print("Error getting More Images could not get the <ul>", e) 
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
                        button_list.append(item.find_element(By.TAG_NAME,'button'))
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
        time.sleep(5)
        try:
            description_features = []
            try:
                # Wait for and click the product features button
                features_btn = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_product_features_btn))
                )
                features_btn.click()
            except Exception as e: print("There was a problem finding the Features Button: ", e)
            
            try:
                # Wait for and click the 'See More' button if it exists
                see_more_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, class_product_features_seemore_btn))
                ) 
                see_more_btn.click()
            except Exception as e:
                print("No 'See More' button found:", e)
            try:
                # Wait for and extract the main features description
                features_description = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_product_features_description_text))
                ).text

                description_features.append(features_description)
            except:
                try:
                    # Wait for and extract the main features description
                    features_description = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CLASS_NAME, (class_product_features_description_text+".clamp")))
                    ).text

                    description_features.append(features_description)
                except: print('No text description found')
                
            # Wait for the div containing the list of features
            div_of_features = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_features_div_of_ul_li))
            )

            # Extract the features list
            list_of_features = div_of_features.find_elements(By.TAG_NAME, "li")
            i=1
            feature = 1
            for each_element in list_of_features:
                try:
                    try:
                        h4 = each_element.find_element(By.TAG_NAME, 'h4').text
                    except:
                        h4=f'Unamed {i}'
                        i+=1
                    p = each_element.find_element(By.TAG_NAME, 'p').text  
                    feature_line = f"{h4}: {p}"
                    description_features.append(feature_line)
                    feature += 1
                except Exception as e:
                    print("Error extracting feature:", e)
                    continue

            product_info['Description'] = '\n'.join(description_features)
            
        except Exception as e:
            product_info['Description'] = "N/A"
            print("Error getting Features:", e)


        # Energy Guide
        product_info['Energy Guide'] = get_element_attribute(By.CLASS_NAME, 'c-button-link.px-150.body-copy-lg', 'href', "Energy Guide")

        # User Manual and Spec Sheet
        try:
            documents = driver.find_elements(By.CLASS_NAME, 'list-pipe')
            product_info['User Manual'] = documents[0].get_attribute('href') if len(documents) > 0 else "N/A"
            product_info['Spec Sheet'] = documents[1].get_attribute('href') if len(documents) > 1 else "N/A"
        except Exception as e:
            log_error("Manual and Spec Sheet Error", e)
            product_info['User Manual'], product_info['Spec Sheet'] = "N/A", "N/A"

        # Add to global data
        products_data.append(product_info)
        try:
            driver.find_element(By.CLASS_NAME,class_close_features_btn).click()
        except Exception as e:
            print("Couldn't click quit button on FEATURES, refreashing...")
            driver.refresh()
            
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------GET SPECS
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, class_show_full_specs))).click()
        except Exception as e:
            try:
                show_full_specs_btn = driver.find_element(By.CLASS_NAME, class_show_full_specs)
                driver.execute_script("arguments[0].click();", show_full_specs_btn)
            except Exception as e:
                logger.error(f'Error clicking in the Spec btn - {e}')
        
        try:
            list_of_specs = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_list_item_specs))
            )
            list_of_specs = list_of_specs.find_elements(By.TAG_NAME, "li")

            for each_item in list_of_specs:
                try:
                    spec_items = each_item.find_elements(By.CLASS_NAME, class_div_each_spec)
                    for spec_item in spec_items:
                        header = spec_item.find_element(By.CLASS_NAME, class_div_spec_header).text
                        spec = spec_item.find_element(By.CLASS_NAME, class_div_spec_text).text
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
    def process_products(driver: webdriver.Chrome):
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
        # driver.get("https://bot.sannysoft.com/")
        # time.sleep(2)
        # driver.save_screenshot("webdriver_test.png")       
        # driver.quit() 
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
            links = pd.read_csv(real_links)
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
    df_old = pd.DataFrame()
    try:
        df_old = pd.read_csv(old_file)
        if df_old.empty:
            print("No old file found, creating one...")
            logger.info("No old file found, creating one...")
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

