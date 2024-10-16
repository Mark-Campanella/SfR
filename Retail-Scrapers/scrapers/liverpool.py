import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import pandas as pd
import re
import os
import json
from wakepy import keep
import random
def run(keywords:str)->None:
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

    scraper = "Liverpool"
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
    #chrome_options.add_argument("--incognito")
    # disable extensions
    chrome_options.add_argument("--disable-extensions")
    #run in headless mode
    # chrome_options.add_argument("--headless") #hide GUI (+eff/-trust)
    # disable sandbox mode
    chrome_options.add_argument('--no-sandbox')
    # disable shared memory usage
    chrome_options.add_argument('--disable-dev-shm-usage')
    # rotate user agents 
    chrome_options.add_argument(f'user-agent={user_agent}')
    #-----------------------------------------------------Do Not Modify unless changes are required (modifications on the website)-----------------------------------------------#

    search_for = keywords
    url = 'https://www.liverpool.com.mx/tienda/home'
    scroll_down_script = "window.scrollTo(0, document.body.scrollHeight);"



    #VARIABLES

    class_search_bar = 'form-control.search-bar.plp-no__results'
    class_items = 'm-product__card.card-masonry.a'
    xpath_next_button = '//*[@id="__next"]/main/div[2]/div[1]/div/div[4]/main/div[3]/div/nav/ul/li[6]/a'

    class_five_star = "TTavgRate"
    class_review_amount = "TTreviewCount"
    class_price = 'a-product__paragraphRegularPrice.m-0.d-inline'
    class_img = 'm-img-pdp.added-event'
    class_more_img = 'pswp__img'

    class_spec_titles = 'productSpecsGrouped_bold'
    class_spec_texts = 'productSpecsGrouped_regular'     

    class_claim_title = 'flix-p3-subtitle.flix-d-h5.feature_modular_map_title'
    class_claim_title2= 'flix-p3-subtitle.feature_modular_map_title'
    class_claim_text = 'flix-p3-desc.flix-d-p.feature_modular_map_desc'


    # Global Variables
    next_page = None
    links = []
    products_data = []
    filtered = False

    driver = webdriver.Chrome(options=chrome_options)

    # Change the property value of the navigator for webdriver to undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    #enable stealth mode
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    #------------------------------------------------------------------------------------------------------------------------------------------Functions
    def scrape_page(driver):
        '''
        Get the items's links and store it in the list of links
        \nReturn the next page webelement
        '''
        global links
        global next_page
        
        #Scroll Down
        driver.execute_script(scroll_down_script)
        print("Scrolled to bottom of the page.")
        
        #Start to get the elements
        try:
            elems = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, class_items)))
            print(f"Found {len(elems)} elements with class {class_items}.")
            
            #get the links
            tags = [elem.find_element(By.TAG_NAME, "a") for elem in elems]
            links.extend([tag.get_attribute("href") for tag in tags])
            
            #try to find the next page, if found, return it, else return None
            try:
                next_page = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, xpath_next_button)))
                print(f"Found next page button")
            except:
                next_page = None
                print("No next page found.")
        except Exception as e:
            print("Error!! ", e)
        finally:
            return next_page

    def process_products(driver):
        '''
        Foreach link caught, scrape item's attributes and go to the next
        \nClear variable after usage
        '''
        global links
        for link in links: 
            process_product(driver, link)
            print(f'{links.index(link)+1}/{len(links)}')
        links.clear()

    def process_product(driver, link:str):
        '''
        Process each product
        '''
        global products_data, all_headers
        driver.get(link)
        driver.implicitly_wait(20)    
        
        product_info = {'Link': link}
        #--------------------------------------------------------------------------------------------------------------------NAME & SKU
        #SKU is not clearly given, so my logic was to take the capitalized code in header
        try:
            name = WebDriverWait(driver,30).until(
                EC.presence_of_element_located((By.TAG_NAME,'h1'))
            ).text
            sku = [token for token in name.split() if token.isupper() and token != "LG"]
            sku = ' '.join(sku)
        except Exception as e:
            print("Not able to get name, nor SKU → error: ",e)
            name = ""
            sku = ""
        finally:
            product_info["Name"] = name
            product_info["SKU"] = sku.lower()  
        
        #-----------------------------------------------------------------------------------------------------------------------Reviews    
        five_star = ""
        try:
            five_star = WebDriverWait(driver,30).until(
                EC.presence_of_element_located((By.CLASS_NAME,class_five_star))
            ).text
            five_star = five_star.replace(" / 5,0",'').replace(',','.')
        except Exception as e:
            print("Error getting 5 Star Data:", e)
        finally:
            product_info["Five Star"] = five_star
            
        review_amount = ""   
        try:
            review_amount = driver.find_element(By.CLASS_NAME,class_review_amount).text
            print(review_amount)
            review_amount = re.search(r'/d+',review_amount).group()
        except Exception as e:
            print("Error getting the Review Amount:", e)
        finally:
            product_info["Review Amount"] = review_amount
        #-------------------------------------------------------------------------------------------------------------------------PRICE    
        price = None   
        try:
            price = driver.find_element(By.CLASS_NAME,class_price).text
            price = price.replace('$', '').replace(',','').replace("\n","")
            price = float(price)/100
            print(price)
        except Exception as e:
            print("Error getting price:", e)
            pass
        finally:
            product_info["Price"] = price
            
        #------------------------------------------------------------------------------------------------------------------------IMAGES
        img = ""
        try:
            img = WebDriverWait(driver,30).until(
                EC.presence_of_element_located((By.CLASS_NAME,class_img))).get_attribute('src')
        except Exception as e:
            print("Error getting Image:", e)
            pass
        finally:
            product_info["Image"] = img    
        more_img = []
        try:
            more_img = driver.find_elements(By.CLASS_NAME,class_more_img)
            more_img = [img.get_attribute('src') for img in more_img]
            "\n".join(more_img)
        except Exception as e:
            print("Error getting More Images:", e)
            pass
        finally:
            product_info["More Images"] = more_img
            
        #-------------------------------------------------------------------------------------------------------------------------SPECS  
            try:
                headers = driver.find_elements(By.CLASS_NAME,class_spec_titles)
                texts = driver.find_elements(By.CLASS_NAME,class_spec_texts)
                headers = [header.text for header in headers]
                texts = [text.text for text in texts]
                for header, text in zip(headers, texts):
                    product_info[header] = text
            except Exception as e:
                print("Error getting the specs:",e)
        #-------------------------------------------------------------------------------------------------------------------------Claims

        
        try:
            claim_titles = driver.find_elements(By.CLASS_NAME,class_claim_title)
            claim_titles2= driver.find_elements(By.CLASS_NAME,class_claim_title2)
            claim_titles_combined = []
            
            for claim_item in claim_titles:
                claim_titles_combined.append(claim_item.text)
            for claim_item in claim_titles2:
                claim_titles_combined.append(claim_item.text)
            try:    
                claim_texts = driver.find_elements(By.CLASS_NAME,)
                claim_texts = [claim_text.text for claim_text in claim_texts]
                
                for claim_title,claim_text in zip(claim_titles_combined,claim_texts):
                    product_info[claim_title] = claim_text
                    
            except Exception as e : print("Error getting claims's texts: ",e)
        except Exception as e :print("Error getting claims's titles: ",e)
        

        products_data.append(product_info)



    #---------------------------------------------------------------------------Begining---------------------------------------------------------------------#    
    #Links - test and speed process
    real_links = "statics/product_link_lvp.csv"
    #Outputs
    test_output_path = f'outputs/{scraper}/test_product_data.csv'
    real_output_path= f'outputs/{scraper}/product_data.csv'
    #Force run
    no_file = "statics/no_file.csv"

    def execution():
        driver.implicitly_wait(20)    
        driver.get(url)
        print("Page loaded.")
        search = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_search_bar)))
        search.send_keys(search_for)
        
        time.sleep(1)
        
        actions = ActionChains(driver)
        actions.send_keys(Keys.ENTER).perform()
        
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
            if links is None:
                btn_next_page = scrape_page(driver)
                while btn_next_page is not None:
                    try:
                        print(f"Navigating to next page")
                        btn_next_page.click()
                        time.sleep(5)
                        btn_next_page = scrape_page(driver)
                    except:
                        print("No next page...")
                        btn_next_page = None
                    
        #If file doesn't exist, run routine to get it and save it later
        except:
            btn_next_page = scrape_page(driver)
            while btn_next_page is not None:
                try:
                    print(f"Navigating to next page")
                    btn_next_page.click()
                    time.sleep(5)
                    btn_next_page = scrape_page(driver)
                except:
                    print("No next page...")
                    btn_next_page = None
                
        if not os.path.exists(real_links):
            df = pd.DataFrame(links, columns=['Product Links'])
            df.to_csv(real_links, index=False)
            
        process_products(driver) #Get information from each link   
        driver.quit()

        # Convert the list of dictionaries into a dataframe
        df = pd.DataFrame(products_data)
        df.to_csv(real_output_path, index=False)
        
        #reset
        zero=[]
        zero = pd.DataFrame(zero)
        df = zero
        df_translated = zero
        added_skus = zero
        removed_skus = zero
    try:        
        execution()
    except Exception as e:
        print(f"Not able to run the code, error: {e}\nTrying again")
        try:
            execution()
        except:
            print(f"Not able to run the code, error: {e}\n\n\tQuitin...\nEND")