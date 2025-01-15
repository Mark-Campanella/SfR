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

            tags = [elem.find_element(By.TAG_NAME, "a") for elem in elems]
            links.extend([tag.get_attribute("href") for tag in tags])
            
            try:
                next_page = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_next_button))).get_attribute("href")
                print(f"Found next page: {next_page}")
            except:
                next_page = None
                print("No next page found.")
                #save list of last scraped items, for threads usage later 
                df = pd.DataFrame(links, columns=['Product Links'])
                df = df.drop_duplicates()
                df.to_csv(real_links, index=False)
        except Exception as e:
            print("Error!! ", e)

    def process_product(driver, link):
        global products_data, main_headers
        driver.get(link)
        driver.implicitly_wait(20)
        handle_survey()
        
        #----------------------------------------------------------------------------------------------------------------------------------------------------------------------GET LINK
        product_info = {'Link': link}
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT NAME
        try:
            product_name_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            product_info['Name'] = product_name_element.text
        except Exception as e:
            product_info['Name'] = "N/A"
            print("Error getting product name:", e)
        unwanteds = ["Package", "Stacking Kit", "sorry"]
        if any(unwanted in product_info['Name'] for unwanted in unwanteds):
            return    
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT SKU
        try:
            product_sku_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_sku))
            )
            #TODO if sku in products_data already in the file, skip it
            product_info['SKU'] = product_sku_element.text
        except Exception as e:
            product_info['SKU'] = "N/A"
            print("Error getting product SKU:", e)
            
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT IMAGE    
        try:
            product_image_link = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_img)))
            product_info['Image Link'] = product_image_link.get_attribute('src')
        except Exception as e:
            product_info['Image Link'] = "N/A"
            print("Error getting product SKU:", e)

        #----------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT 5-STAR REVIEWS       
        try:
            five_star = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_5_star))
            ).text
            product_info['Five Star'] = five_star
        except Exception as e:
            product_info['Five Star'] = "N/A"
            print("Error getting five star rating:", e)
            
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------GET REVIEW AMOUNT
        try:
            review_amount = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_review_amount))
            ).text
            product_info['Review Amount'] = review_amount
        except Exception as e:
            product_info['Review Amount'] = "N/A"
            print("Error getting review amount:", e)      
                
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT PRICE
        try:
            price_div = driver.find_element(By.CLASS_NAME, class_product_price)
            product_info['Price'] = price_div.find_element(By.TAG_NAME, 'span').text
        except Exception as e:
            #Some times the product has the price hidden (it needs to be added in your cart to show price, so that is what this is doing)
            try:
                driver.find_element(By.CLASS_NAME,class_product_price_btn_modal).click()
                try:
                    price_div = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, class_product_price_div_modal))
                    )
                    price_div = price_div.find_element(By.CLASS_NAME, class_product_price_innerdiv_modal)
                    price_div = price_div.find_element(By.CLASS_NAME, class_product_price)
                    price = price_div.find_element(By.TAG_NAME, 'span').text
                    product_info['Price'] = price
                except Exception as e_text:
                    print("Couldn't get the price because ", e_text)
                    product_info['Price'] = ""
                        #I was having problem to click in the button, this is an atomic bomb, I know
                try:
                    #Uses Selenium to click
                    close_btn = WebDriverWait(driver, 4).until(
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
            except: print("Couldn't close the modal nand/nor get the price properly")
            
        #--------------------------------------------------------------------------------------------------------------------------------------------------------GET MORE PRODUCT IMAGE
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
            print("Error getting More Images, could not click in the more images button", e)
            
        #------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT VIDEOS    
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
            
        #--------------------------------------------------------------------------------------------------------------------------------------------------GET DESCRIPTION AND FEATURES        
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
            
        #Get Energy guide
        try:
            energy_guide = driver.find_element(By.CLASS_NAME,'c-button-link.energy-guide-link.ml-150').get_attribute("href")
            product_info['Energy Guide'] = energy_guide
        except Exception as e:
            product_info['Energy Guide'] = None
            print("Error getting the energy guide, sorry, error: ",e)

        #Get Manual and Specsheet
        try:
            documents = driver.find_elements(By.CLASS_NAME,'manual-link.body-copy-lg')
            doc1 = documents[0].get_attribute('href')
            doc2 = documents[1].get_attribute('href')
            
            if 'user' in doc1.lower() or 'owners' in doc1.lower() or 'specs' in doc2.lower():
                product_info['User Manual'] = doc1
                product_info['Spec Sheet'] = doc2
            else:
                product_info['Spec Sheet'] = doc1
                product_info['User Manual'] = doc2
        except: 
            print("Error getting the manual, maybe it doesn't exist here? I will try something else...")
            try:
                doc = driver.find_element(By.CLASS_NAME,'manual-link.body-copy-lg').get_attribute('href')
                if 'User' in doc:
                    product_info['User Manual'] = doc
                else:
                    product_info['Spec Sheet'] = doc
            except Exception as e:
                product_info['Document 1'] = None
                print("Nope, could not find a document, sorry...\n",e)
            
        finally:
            try:
                # Attempt to close any modal that might be open
                close_icon = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'c-close-icon'))
                )
                close_icon.click()
            except Exception as e:
                print("No close icon found, refreshing page:", e)
                driver.refresh()
                
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
                else: 
                    break
        
    except Exception as e:
        print("Not able to run the code, error: ", e)

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
        df = df_save
    try:
        df = merge(df)
    except Exception as e:
        print("Not able to merge with the SAS VA and Traqline's SKU data")
        
    #Get last scraped information
    try:
        df_old = pd.read_csv(old_file)
    except FileNotFoundError as e: print ("Not able to locate file: ",e)
    except Exception as e: print("Error: ", e)
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

