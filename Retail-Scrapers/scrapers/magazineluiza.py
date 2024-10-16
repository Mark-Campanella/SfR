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
import os
import json
from wakepy import keep
from scrapers.routines.Laundry.magazineluiza_file_cleaner import clean
import random

# Global Variables
next_page = None
links = []
products_data = []
filtered = False

def run(keywords:str)->None:
        
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
    # chrome_options.add_argument("--headless") #hide GUI (+eff/-trust)
    # disable sandbox mode
    chrome_options.add_argument('--no-sandbox')
    # disable shared memory usage
    chrome_options.add_argument('--disable-dev-shm-usage')
    # rotate user agents 
    chrome_options.add_argument(f'user-agent={user_agent}')

    #-----------------------------------------------------Do Not Modify unless changes are required (modifications on the website)-----------------------------------------------#
    #Those are mostly CSS Classes, notwithstanding, I had to go to a XPATH 2x those are more critical and might require more maintaince!!
    search_for = keywords
    url = 'https://www.magazineluiza.com.br/'
    scroll_down_script = "window.scrollTo(0, document.body.scrollHeight);"

    xpath_price_filter_min = '//*[@id="__next"]/div/main/section[3]/div[2]/div[3]/div[2]/div/div[1]/div[1]/input'
    xpath_next_button = '//*[@id="__next"]/div/main/section[4]/div[5]/nav/ul/li[9]/button'

    class_search_bar= 'sc-iapWAC.dliMlI'
    class_search_button = 'sc-eqUAAy.IubVJ.sc-ePDLzJ.cObXPU' #Not using

    price_min = 40000 # R$400,00
    class_btn_apply_filter = 'sc-fUnMCh.ioWxHY.sc-kUdmhA.fQIIXy'
    class_filter = 'sc-fqkvVR.kOsgy'
    class_filter_min = "sc-dSCufp.kEkNGz"
    class_items = 'sc-fHjqPf.eXlKzg.sc-dcjTxL.gwmFli.sc-dcjTxL.gwmFli'
    main = 'sc-f0cf7f7-0.hiMCYa'

    class_price = 'sc-kpDqfm.gBEKKZ.sc-fFlnrN.iNGPEW'
    class_main_image = "sc-eBMEME.ivurhG"
    class_five_star_div = 'sc-dhKdcB.jnmzra.sc-iRfNzj.gXjpmo'
    class_five_star = 'sc-kUdmhA.dWhxDa'
    class_description = 'sc-fqkvVR.hlqElk.sc-fdVlUD.brfvue'
    class_more_img_btn = 'sc-fqkvVR.hhMVXv'
    class_more_img_div = 'sc-dkmUuB.LQICX'
    class_more_img_carousel = "sc-hHOBiw.jCwvDE"
    class_more_img_if_fails = 'sc-fqkvVR.aPzLt.sc-lmJFLr.genPaT'
    class_product_description_header = 'sc-dcJsrY.jZKEso'
    class_product_description_text = 'sc-iGgWBj.eWtIHQ.sc-kodNMj.dCOsrq'

    class_table_specs = 'sc-iGgWBj.iCEidV.sc-eBwKMn.kTdlzO'
    class_table_headers = "sc-bHnlcS.dUJHzp"
    class_table_td = 'sc-cKXybt.eHjdkg'
    class_table_table_texts = 'sc-fatcLD.dnJluC'

    driver = webdriver.Chrome(options=chrome_options)
    # Change the property value of the navigator for webdriver to undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    stealth(driver,
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
        global filtered
        
        try:
            #Filter function: needs to be done only once, that's why I am using a flag here    
            if filtered is False:
                #You will find some sleep method here, they are for the page to load properly
                try:
                    #Find where the filter is
                    filter_min = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,class_filter)))
                    filter_min = filter_min.find_element(By.TAG_NAME,'input')
                    print("Found the filter!")
                    time.sleep(2)
                    #Clear what was already set there
                    filter_min.clear()
                    #Enter value: I am using R$400,00 as bottom filter
                    filter_min.send_keys(price_min)
                    time.sleep(10)
                except Exception as e:
                    try:
                        print(f"Not able to get the filter right, error:\n {e}")
                        filter_min = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,class_filter_min)))
                        filter_min.clear()
                        time.sleep(3)
                        filter_min.send_keys(price_min)
                        time.sleep(5)
                    except:
                        try:
                            print(f"Not able to get the filter right")
                            filter_min = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,xpath_price_filter_min)))
                            filter_min.clear()
                            time.sleep(3)
                            filter_min.send_keys(price_min)
                            time.sleep(5)
                        except Exception as e:
                            print("Sorry, tried everything to set the filter...:\n\n",e)
                #Click in the Apply button
                try:
                    btn_apply_filter = WebDriverWait(driver,2).until(EC.element_to_be_clickable((By.CLASS_NAME,class_btn_apply_filter)))
                    btn_apply_filter.click()
                    time.sleep(15)
                except: print("Not able to click on the apply button")
                filtered = True #Set flag as True for it to only run once
        except Exception as e: print(f"Not able to filter, error: \n{e}\nGetting all products...")
        
        #Scroll Down
        driver.execute_script(scroll_down_script)
        print("Scrolled to bottom of the page.")
        
        #After filtered, start to get the elements
        try:
            tags = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, class_items)))
            print(f"Found {len(tags)} elements with class {class_items}.")
            links.extend([tag.get_attribute("href") for tag in tags])

            #If items scraped, GET NEXT PAGE
            try:
                next_page = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, xpath_next_button)))
                print(f"Found next page button")
            except:
                next_page = None
                print("No next page found.")
        except Exception as e:
            print("Error!! ", e)
        return next_page


    def process_product(driver, link:str):
        '''
        Process each product
        '''
        global products_data, all_headers
        driver.get(link)
        driver.implicitly_wait(20)    
        
        product_info = {'Link': link}
        #-------------------------------------------------------------------------------------------------------------------------------GET JSON WITH INFO

        #There is a JSON in each product, with some information innit. I have found it quicker to get and populate the dict of product!
        try:
            #the json is always the first script available in the main page!
            main_page = driver.find_element(By.CLASS_NAME,main)
            content = main_page.find_element(By.TAG_NAME,'script').get_attribute("innerHTML")
            content_text = json.loads(content)

            #Name
            try:
                product_info['Name'] = content_text['name']
            except Exception as e:
                print("Error getting Name on JSON → Getting normal way.\n\tError: ",e)
                try:
                    product_name_element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                    product_info['Name'] = product_name_element.text
                except Exception as e:
                    product_info['Name'] = ""
                    print("Error getting product name:", e)
            finally:        
                #If item not of our interest, ignore it
                unwanteds = ["pacote", "peça", "capa", "mini"]
                if any(unwanted in product_info['Name'].lower() for unwanted in unwanteds):
                    return
                
            #Price 
            try:        
                product_info['Price'] = content_text['offers']['price']
            except Exception as e:
                print("Error getting PRICE on JSON → Getting normal way.\n\tError: ",e)   
                try:
                    product_price = driver.find_element(By.CLASS_NAME,class_price)
                    product_info['Price'] = product_price.text.replace("R$","").replace("&nbsp;","").replace('.','').replace(",", ".").strip()
                except Exception as e:
                    product_info['Price'] = ""
                    print(f"Error occurred while getting price:\n{e}")


            #Image
            try:
                product_info['Image'] = content_text['image'].replace("186x140","1000x1000")
            except Exception as e:
                print("Error getting IMAGE on JSON → Getting normal way.\n\tError: ",e)
                try:
                    image = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,class_main_image)))
                    product_info["Image"] = image.get_attribute('src').replace("/800x560/","/1000x1000/")
                except:
                    product_info["Image"] = ""
                    print("Not able to get Image")

            #Description                
            try:
                product_info['Description'] = content_text['description']
            except Exception as e:
                print("Error getting DESCRIPTION on JSON → Getting normal way.\n\tError: ",e)
                try:
                    text = driver.find_element(By.CLASS_NAME,class_description).text
                    product_info['Description'] = text
                except:
                    product_info['Description'] = ''
                    print("Not able to get the Description")

            #5-Star    
            try:
                product_info['Five Star'] = content_text['aggregateRating']['ratingValue']
                product_info['Review Amount'] = content_text['aggregateRating']['reviewCount']
            except Exception as e:
                print("Error getting FIVE STAR AND REVIEW on JSON → Getting normal way.\n\tError: ",e)
                try:
                    five_star_div = driver.find_element(By.CLASS_NAME,class_five_star_div)
                    review_list = five_star_div.find_element(By.CLASS_NAME, ).text().split()
                    five_star = review_list[0]
                    review_amount = review_list[1].replace('(', '').replace(')', '').strip()
                    product_info['Five Star'] = five_star
                    product_info['Review Amount'] = review_amount
                except:
                    product_info['Five Star'] = ""
                    product_info['Review Amount'] = ""
                    print("Not able to get 5-star data")
            
                    #other info        
            try:
                product_info['Brand'] = content_text['brand']
                product_info['Color'] = content_text['color']
            except Exception as e:
                print("Error getting OTHER INFO on JSON,\n\tERROR: ",e)


                #-------------------------------------------------------------------------------------------------------------------------------------------SKU
            try:
                #For SKU, we will find the word in the Name that isupper()
                words = product_info['Name'].split(" ")
                for word in words:
                    if word.isupper() and word != "LG":
                        sku = word.lower()
                        break
                    else:
                        sku = None
                product_info['SKU'] = sku
            except:
                product_info['SKU'] = None
                print("Not able to get SKU")         
                
            #-----------------------------------------------------------------------------------------------------------------------------------------MORE IMAGES
            try:
                try:
                    driver.find_element(By.CLASS_NAME,class_more_img_btn).click()
                    div_images = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME,class_more_img_div)))
                    carousels = div_images.find_elements(By.CLASS_NAME,class_more_img_carousel)
                    for carousel in carousels:
                        images_webelement = [image_webelement for image_webelement in carousel.find_elements(By.TAG_NAME,'img')]
                    images = [image.get_attribute('src') for image in images_webelement]
                    try:
                        for image in images:
                            if "90x90" in image: image.replace("/90x90/",'/1000x1000/')
                            elif "96x74" in image: image.replace('/96x74/','/1000x1000/')
                            
                        product_info['More Images'] = images
                    except Exception as e: print('Error making images bigger: ',e)
                    driver.refresh()
                except:
                    div_images = driver.find_element(By.CLASS_NAME,class_more_img_if_fails)
                    images_webelement = div_images.find_elements(By.TAG_NAME,'img')
                    images = [image.get_attribute('src') for image in images_webelement]
                    try:
                        for image in images:
                            if "90x90" in image: image.replace("90x90",'1000x1000')
                            elif "96x74" in image: image.replace('96x74','1000x1000')
                            elif "96x72" in image: image.replace('96x72','1000x1000')
                        product_info['More Images'] = images
                    except Exception as e: print('Error making images bigger: ', e)            
                print(product_info['More Images'])
            except Exception as e: print("Error getting More Images: ", e)    
            
            #Scroll to load table properly
            driver.execute_script(scroll_down_script)
            
            #--------------------------------------------------------------------------------------------------------------------------------------------SPECS TABLE
            try:
                print("\nLet's get the SPECIFICATIONS:\n")
                try:
                    #GET OUTER TABLE
                    table = WebDriverWait(driver,10).until(
                        EC.presence_of_element_located((By.CLASS_NAME,class_table_specs))
                    )
                    try:
                    #GET HEADER    
                        headers_elements = table.find_elements(By.CLASS_NAME,class_table_headers)
                        headers = [header.get_attribute('textContent') for header in headers_elements]
                        print("\n\nHEADERS:",headers)
                        
                        try:
                        #GET TEXT 
                            tds = table.find_elements(By.CLASS_NAME,class_table_td)
                            tables = [td.find_element(By.CLASS_NAME,class_table_table_texts) for td in tds]
                            texts = [table.find_element(By.TAG_NAME,'td').get_attribute('textContent') for table in tables]
                            print('\n\nTEXTS',texts)
                            
                            #Now we want to envelop that in a structure like: "header":"text"    
                            for header, text in zip(headers, texts): 
                                product_info[header] = text
                                #print(f"\tMatched Header:Text, like:{header}:{product_info[header]}")
                                
                        except Exception as e: print("Not able to get the text: ", e)            
                    except Exception as e: print("Not able to get the header: ", e)        
                except Exception as e: print("Not able to find the outer table: ", e)
            except Exception as e: print('Something happened gettign the SPECS, error:',e) 
            print(product_info)
            products_data.append(product_info)

        except Exception as e:
            print("Failed to get info from product :(, ERROR:\n\n",e)

    def process_products(driver):
        global links
        for link in links: 
            process_product(driver, link)
            print(f'{links.index(link)+1}/{len(links)}')
        links.clear()

    #---------------------------------------------------------------------------Begining---------------------------------------------------------------------#  
    #Links - test and speed process
    real_links = "statics/product_link_Mzl.csv"
    #Outputs
    test_output_path = 'outputs/Magazineluiza/test_product_data.csv'
    real_output_path= 'outputs/Magazineluiza/product_data.csv'
    #Force run
    no_file = "statics/no_file.csv"  

    try:        
        driver.get(url)
        driver.implicitly_wait(20)
        time.sleep(2)
        print("Page loaded.")
        search = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_search_bar)))
        search.send_keys(search_for)
        
        time.sleep(0.6)
        
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
                i = 0
                btn_next_page = scrape_page(driver)
                while btn_next_page is not None:
                    i+=1
                    print(f"Navigating to next page",i+1)
                    btn_next_page.click()
                    time.sleep(5)
                    btn_next_page = scrape_page(driver)
                        
        #If file doesn't exist, run routine to get it and save it later
        except:
            i = 0
            btn_next_page = scrape_page(driver)
            while btn_next_page is not None:
                i+=1
                print(f"Navigating to next page:", i+1)
                btn_next_page.click()
                time.sleep(5)
                btn_next_page = scrape_page(driver)
    except Exception as e:
        print("Not able to run the code, error: ", e)

    if not os.path.exists(real_links):
        df = pd.DataFrame(links, columns=['Product Links'])
        df.to_csv(real_links, index=False)
        
    process_products(driver)
    driver.quit()

    # Convert the list of dictionaries into a dataframe
    df = pd.DataFrame(products_data)
    df_list = clean(df)

    #store
    df = df_list[0]
    df_translated = df_list[1]
        
    df.to_csv(real_output_path, index=False)
    df_translated.to_csv('outputs/Magazineluiza/translated_product_data.csv', index=False, encoding='utf-8')


    #reset
    zero=[]
    zero = pd.DataFrame(zero)
    df = zero
    df_translated = zero
    added_skus = zero
    removed_skus = zero