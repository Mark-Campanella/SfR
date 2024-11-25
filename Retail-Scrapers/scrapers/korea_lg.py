from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import pandas as pd
import random
from urllib.parse import urljoin

#-----------------------------------------------------Personalization Variables---------------------------------------------------------------------#
url = "https://www.lge.co.kr/wash-tower?subCateId=CT50210002"


#-----------------------------------------------------Do Not Modify if no changes are required------------------------------------------------------#

# Global Variables
next_page = None
links = []
products_data = []
main_headers = ["Link", "Name", "SKU", "Price", "Five Star", "Review Amount", "Image Link", 'Description', 'More Images Links', 'Videos Links'] 
#Links - test and speed process
test_links = "statics/test_product_link_LG_ko.csv"
real_links = "statics/product_link_LG_ko.csv"
#Outputs
test_output_path = 'outputs/LG_ko/test_product_data.csv'
real_output_path= 'outputs/LG_ko/product_data.csv'
#other paths
old_file = 'statics/old_file.csv'
#Force run
no_file = "statics/no_file.csv"


class_items = "top-title-main"
xpath_second_page = '//*[@id="_plpComponent"]/section/section[3]/section[2]/div/div[4]/span/a'
class_product_sku = 'sku copy'
class_product_img = 'pdp-visual-image is-active'
class_product_5_star = 'star-rating-wrap'
class_product_price = 'price-detail-item type-small-dept'
class_btn_more_images = 'thumbnail more'
class_claims_placeholder = 'iw_placeholder'
class_claim = 'iw_component'
class_spec_container = 'prod-spec-detail'
class_show_full_specs='btn_collapse_more' 
class_div_prod_spec_detail="prod-spec-detail"


def run()-> None:
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
    # chrome_options.add_argument("--headless") #improve efficiency, decrease trustability
    # disable sandbox mode
    # chrome_options.add_argument('--no-sandbox')
    # disable shared memory usage
    chrome_options.add_argument('--disable-dev-shm-usage')
    # rotate user agents 
    chrome_options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(options=chrome_options)
    BASE_URL = "https://www.lge.co.kr/"

    # Change the property value of the navigator for webdriver to undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    stealth(driver,
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)


    #----------------------------------------------------------------Functions-------------------------------------------------------------------------#
    def item_adjust(item:str):
        item = item.replace(" ",".")
        return item
    
    def scrape_page(driver):
        global links
        global next_page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Scrolled to bottom of the page.")
        try:
            elems = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, item_adjust(class_items))))
            print(f"Found {len(elems)} elements with class {class_items}.")

            tags = [elem.find_element(By.TAG_NAME, "a") for elem in elems]
            links.extend([tag.get_dom_attribute("href") for tag in tags])
            
            try:
                next_page = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath_second_page)))
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
        try:
            WebDriverWait(driver,30).until(
                EC.element_to_be_clickable((By.ID,'link-button-1454703450485'))
            ).click()
        except:
            pass
        #----------------------------------------------------------------------------------------------------------------------------------------------------------------------GET LINK
        product_info = {'Link': link}
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT NAME
        try:
            product_name_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            product_info['Name'] = product_name_element.text
        except Exception as e:
            product_info['Name'] = ""
            print("Error getting product name:", e)
        unwanteds = ["Package", "Stacking Kit", "sorry"]
        if any(unwanted in product_info['Name'] for unwanted in unwanteds):
            return    
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT SKU
        try:
            product_sku_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust(class_product_sku)))
            )
            #TODO if sku in products_data already in the file, skip it
            product_info['SKU'] = product_sku_element.text
        except Exception as e:
            product_info['SKU'] = ""
            print("Error getting product SKU:", e)
            
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT FLAGS
        try:
            product_flags = driver.find_element(By.CLASS_NAME,'flag-wrap.bar-type').find_elements(By.CLASS_NAME,'flag')
            product_flags_text = [flag_text.text for flag_text in product_flags]
            product_info['Flags'] = product_flags_text
        except Exception as e:
            product_info['Flags'] = ""
            print("Error fetching flags: ", e)            
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT IMAGE    
        try:
            product_image_link = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust(class_product_img))))
            product_info['Image Link'] = product_image_link.get_dom_attribute('src')
        except Exception as e:
            product_info['Image Link'] = ""
            print("Error getting product SKU:", e)

        #----------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT 5-STAR REVIEWS       
        try:
            five_star_and_review_amount = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust(class_product_5_star)))
            ).text
            five_star = five_star_and_review_amount.split()[0]
            product_info['Five Star'] = five_star
        except Exception as e:
            product_info['Five Star'] = ""
            print("Error getting five star rating:", e)
            
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------GET REVIEW AMOUNT
        try:
            review_amount = five_star_and_review_amount.split()[1].replace('(','').replace(')','')
            product_info['Review Amount'] = review_amount
        except Exception as e:
            product_info['Review Amount'] = ""
            print("Error getting review amount:", e)      
                
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT PRICE
        try:
           product_info['Price'] = driver.find_element(By.CLASS_NAME, item_adjust(class_product_price)).text
        except Exception as e:
            #If fails, get promocional price
            try:
                product_info['Price'] = driver.find_element(By.CLASS_NAME,item_adjust("price"))
            except Exception as e_text:
                print("Couldn't get the price because ", e_text)
                product_info['Price'] = ""            
        #--------------------------------------------------------------------------------------------------------------------------------------------------------GET MORE PRODUCT IMAGE
        
        images = []
        try:
            btn_more_images = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, item_adjust(class_btn_more_images))))
            btn_more_images.find_element(By.TAG_NAME,'a').click()
            try:
                div_ul_more_images = driver.find_element(By.CLASS_NAME,'pop-thumbnail-list')
                try:
                    div_li_more_images = (div_ul_more_images.find_elements(By.CLASS_NAME,'pop-thumbnail') + 
                                          div_ul_more_images.find_elements(By.CLASS_NAME,'pop-thumbnail.on') +
                                          div_ul_more_images.find_elements(By.CLASS_NAME,'pop-thumbnail.active')
                                          )
                    try:
                        for each_li in div_li_more_images:
                            try:
                                images.append(each_li.find_element(By.TAG_NAME,'img').get_dom_attribute('src'))
                            except: pass
                        product_info['More Images Links 1'] = images  
                    except Exception as e: 
                        product_info['More Images Links 1'] = "N/A"
                        print("Error getting More Images could not get the images", e)
                except Exception as e:
                    product_info['More Images Links 1'] = "N/A"
                    print("Error getting More Images could not get the items list <li>", e)    
            except Exception as e:       
                product_info['More Images Links 1'] = "N/A"
                print("Error getting More Images could not get the <ul>", e) 
        except Exception as e: 
            product_info['More Images Links 1'] = "N/A"
            print("Error getting More Images, could not click in the more images button", e)
        
        try:
            driver.find_element(By.CLASS_NAME,'btn-close.ui_modal_close').click()
        except Exception as e:
            print("Could not close MODAL IMAGES because of: \n\t", e)
            driver.refresh()        

            
        #------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT CLAIMS
        try:
            claims_placeholder = driver.find_element(By.CLASS_NAME, item_adjust(class_claims_placeholder))
            claim_list = claims_placeholder.find_elements(By.CLASS_NAME, item_adjust(class_claim))
            
            for i, claim in enumerate(claim_list, start=1):  # Enumerate os claims
                list_of_content = []

                # Capture text
                texts = claim.text.strip()
                if texts:
                    list_of_content.append(texts)
                else:
                    print(f"No text found in claim {i}")

                # Capture images
                images_list = claim.find_elements(By.TAG_NAME, 'img')
                if images_list:
                    list_of_content.extend([urljoin(BASE_URL,image.get_dom_attribute('src')) or "" for image in images_list])
                else:
                    print(f"No images found in claim {i}")

                # Capture links
                claim_links = claim.find_elements(By.TAG_NAME, 'a')
                if claim_links:
                    list_of_content.extend([urljoin(BASE_URL,link.get_dom_attribute('href')) or "" for link in claim_links])
                else:
                    print(f"No links found in claim {i}")

                # Capture videos
                videos_list = claim.find_elements(By.TAG_NAME, 'video')
                if videos_list:
                    list_of_content.extend([urljoin(BASE_URL,video.get_dom_attribute('src')) or "" for video in videos_list])
                else:
                    print(f"No videos found in claim {i}")
                
                    # Filter out None values
                    list_of_content = [content for content in list_of_content if content]


                # Save data in dictionary
                if list_of_content:
                    product_info[f'Claim item {i}'] = '\n'.join(list_of_content) 
                    print(f'Claim item {i}:{product_info[f"Claim item {i}"]}\n')
                else:
                    print(f"Claim {i} has no content.")
                    product_info[f'Claim item {i}'] = ""

        except Exception as e:
            print(f"An error occurred while processing claims: {e}")

            
        #--------------------------------------------------------------------------------------------------------------------------------------------------GET DESCRIPTION AND FEATURES        
        # try:
        #     product_specs_container = driver.find_element(By.CLASS_NAME,class_spec_container)
        # except Exception as e:
        #     print("Error trying to get features: ",e)
            
        # #Get Energy guide
        # try:
        #     energy_guide = driver.find_element(By.CLASS_NAME,'c-button-link.energy-guide-link.ml-150').get_dom_attribute("href")
        #     product_info['Energy Guide'] = energy_guide
        # except Exception as e:
        #     product_info['Energy Guide'] = None
        #     print("Error getting the energy guide, sorry, error: ",e)

        # #Get Manual and Specsheet
        # try:
        #     documents = driver.find_elements(By.CLASS_NAME,'manual-link.body-copy-lg')
        #     doc1 = documents[0].get_dom_attribute('href')
        #     doc2 = documents[1].get_dom_attribute('href')
            
        #     if 'user' in doc1.lower() or 'owners' in doc1.lower() or 'specs' in doc2.lower():
        #         product_info['User Manual'] = doc1
        #         product_info['Spec Sheet'] = doc2
        #     else:
        #         product_info['Spec Sheet'] = doc1
        #         product_info['User Manual'] = doc2
        # except: 
        #     print("Error getting the manual, maybe it doesn't exist here? I will try something else...")
        #     try:
        #         doc = driver.find_element(By.CLASS_NAME,'manual-link.body-copy-lg').get_dom_attribute('href')
        #         if 'User' in doc:
        #             product_info['User Manual'] = doc
        #         else:
        #             product_info['Spec Sheet'] = doc
        #     except Exception as e:
        #         product_info['Document 1'] = None
        #         print("Nope, could not find a document, sorry...\n",e)
            
        # finally:
        #     try:
        #         # Attempt to close any modal that might be open
        #         close_icon = WebDriverWait(driver, 10).until(
        #             EC.element_to_be_clickable((By.CLASS_NAME, 'c-close-icon'))
        #         )
        #         close_icon.click()
        #     except Exception as e:
        #         print("No close icon found, refreshing page:", e)
        #         driver.refresh()
                
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------GET SPECS
        try:
            show_full_specs_btn = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, item_adjust(class_show_full_specs))))
            driver.execute_script("arguments[0].scrollIntoView();", show_full_specs_btn)
            show_full_specs_btn.click()
        except Exception as e:
            print("Couldn't click show full specs button:", e)

        
        try:
            product_specs = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust(class_div_prod_spec_detail)))
            ).find_elements(By.CLASS_NAME,'box')

            for box in product_specs:
                # Directly iterate over li elements in each box
                for spec_item in box.find_elements(By.TAG_NAME, 'li'):
                    try:
                        header = spec_item.find_element(By.TAG_NAME, 'dt').text
                        spec = spec_item.find_element(By.TAG_NAME, "dd").text
                        product_info[header] = spec

                        if header not in main_headers:
                            main_headers.append(header)
                    except Exception as e:
                        print(f"Error extracting specification: {e}")

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
        for idx,link in enumerate(links,start=1): 
            try:
                print(link)
                process_product(driver, urljoin(BASE_URL,link))
                print(f"Processing {idx}/{len(links)}: {urljoin(BASE_URL,link)}")
            except Exception as e:
                print(f"Error getting into link:{link}\nReason: {e}")
                continue
        links.clear()

    #---------------------------------------------------------------------------Begining---------------------------------------------------------------------#
    global products_data
    try:        
        driver.get(url)
        driver.implicitly_wait(20)  # Wait for it to load
        try:
            WebDriverWait(driver,30).until(
                EC.element_to_be_clickable((By.ID,'link-button-1454703450485'))
            ).click()
        except:
            pass
        print("Page loaded.")
        # search = WebDriverWait(driver, 30).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, class_search_bar)))
        # search.send_keys(search_for)
        
        # time.sleep(2)
        
        # button = WebDriverWait(driver, 30).until(
        #     EC.element_to_be_clickable((By.CLASS_NAME, class_search_button)))
        # button.click()
        
        # driver.implicitly_wait(20)  # Wait for it to load

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
                    scrape_page(driver)
                    if next_page: 
                        i+=1
                        next_page.click()
                        print(f"Navigating to next page: {next_page}: {i}")
                    else: 
                        break
        #If file doesn't exist, run routine to get it and save it later
        except:
            i=1
            while True:
                print("Scraping page: ",i)
                scrape_page(driver)
                if next_page: 
                    i+=1
                    next_page.click()
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
    # Save the updated DataFrame
    df.to_csv(real_output_path, index=False)
    
    print(df.info())
    
run() 