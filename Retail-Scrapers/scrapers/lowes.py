import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium_stealth import stealth
import undetected_chromedriver as uc
import seleniumwire.undetected_chromedriver as uc


import pandas as pd
# from scrapers.routines.Laundry.bb_file_cleaner import cleanup
from scrapers.routines.Laundry.bb_merger import merge
from scrapers.routines.Laundry.bb_file_cleaner import cleanup

import random
import logging
from datetime import datetime





#-----------------------------------------------------Personalization Variables---------------------------------------------------------------------#
url = "https://www.lowes.com/"

#-----------------------------------------------------Do Not Modify if no changes are required------------------------------------------------------#

class_search_bar = "sb-input.js-predictive-input.js-predictive-current"
class_search_button = "sb-search-icon"

class_items_list = "items"
class_items = "tile_group"
aria_label_next_button = "arrow right"


class_product_5_star = "avgrating"
class_product_review_amount = "sc-dhKdcB.fpxwai"
class_product_sku = "styles__ParagraphRegular-sc-1ljw3tp-0.doewXW.typography.variant--body_small.align--left.body_2" #second element in the array
class_product_img_container="ImageContainerstyles__ImageTileWrapper-sc-1l8vild-0.cfyBCn.tile"
class_product_img="tile-img"


class_product_price = "PriceUIstyles__SPAN-sc-14j12uk-1.guaLly.was-price.false "
class_product_price2 = "item-price-dollar"
# class_product_price_btn_modal = "priceView-tap-to-view-price.priceView-tap-to-view-price-bold"
# class_product_price_div_modal = 'restricted-pricing__regular-price-section'
# class_product_price_innerdiv_modal = 'pricing-price'
# class_product_price_btn_close_modal = "c-close-icon.c-modal-close-icon"

#class_product_features_btn = "c-button-unstyled.features-drawer-btn.w-full.flex.justify-content-between.align-items-center.py-200"
#class_product_features_seemore_btn = "c-button-unstyled.see-more-button.btn-link.bg-none.p-none.border-none.text-style-body-lg-500"
class_product_features_div = "sc-fjvvzt.jcPQoi.overviewWrapper"
class_product_features_description_text = "romance"
class_product_features_div_of_ul_li = "specs"


class_product_guides_div = "guides"
class_product_guides = "guide-item" #get a href for guide in guide-items


class_btn_more_images = 'MobileGallery__ViewportItemWrapper-sc-nv7kpt-2.dQeOUC.thumbnail-wrapper'
class_div_images =  "react-transform-component.transform-component-module_content__uCDPE "
class_div_btn_images = "ButtonBase-sc-1ngvxvr-0 jEYXMi backyard button size--medium variant--ghost color--interactive shape--rounded IconButtonBase-sc-y8g6tj-0 kvnCWR icon-button button-right navigation-wrapper-button".replace(" ", ".")

class_specs_div = "SpecificationComponentstyles__NewSpecificationWrapper-sc-s1hhpd-0.dEOazC" #get tables elements for each table get tbodys for each tbody get trs for each tr get tds for each td get td.text tds_texts[even] = headers | tds_texts[odd]= content
data_testid_show_full_specs = "specification-accordion" #if class_specs_div not found, try to click in the data_testid_show_full_specs and execute logic again


# Global Variables
next_page = None
links = []
products_data = []
main_headers = ["Link", "Name", "SKU", "Price", "Five Star", "Review Amount", "Image Link", 'Description', 'More Images Links', 'Videos Links'] 
#Links - test and speed process
test_links = "statics/test_product_link_LWs.csv"
real_links = "statics/product_link_LWs.csv"
#Outputs
test_output_path = "outputs/Lowe's/test_product_data.csv"
real_output_path= "outputs/Lowe's/product_data.csv"
#other paths
old_file = 'statics/old_file.csv'
#Force run
no_file = "statics/no_file.csv"



def mimic(driver):
    actions = ActionChains(driver)
    
    # Lista de ações possíveis
    behaviors = [
        "scroll",         # Rolagem aleatória da página
        "move_mouse",     # Movimento aleatório do mouse
        "key_press",      # Pressionar teclas aleatórias (Tab, Enter, etc.)
        "click",          # Clique aleatório em links ou botões
        "pause"           # Pausa aleatória
    ]
    
    # Seleciona uma ou duas ações aleatórias da lista de comportamentos
    selected_behaviors = random.sample(behaviors, random.choice([1, 2]))  # Escolhe 1 ou 2 ações aleatórias
    
    # Executa as ações escolhidas
    if "scroll" in selected_behaviors:
        # Rolagem aleatória da página
        scroll_height = random.randint(300, 1500)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(1, 3))  # Pausa aleatória após rolar

    if "move_mouse" in selected_behaviors:
        # Movimento aleatório do mouse
        screen_width = driver.execute_script("return window.innerWidth")
        screen_height = driver.execute_script("return window.innerHeight")
        mouse_x = random.randint(0, screen_width)
        mouse_y = random.randint(0, screen_height)
        actions.move_by_offset(mouse_x, mouse_y).perform()
        time.sleep(random.uniform(1, 3))  # Pausa aleatória após o movimento

    if "key_press" in selected_behaviors:
        # Pressionar teclas aleatórias (como 'Tab', 'Enter', 'Arrow Down', 'Arrow Up')
        random_key = random.choice([Keys.TAB, Keys.ENTER, Keys.ARROW_DOWN, Keys.ARROW_UP])
        
        # Captura o URL atual antes de pressionar a tecla
        current_url = driver.current_url
        
        # Executa a ação de pressionar a tecla
        actions.send_keys(random_key).perform()
        
        # Pausa após pressionar a tecla
        time.sleep(random.uniform(1, 2))
        
        # Verifica se o URL mudou após a pressão da tecla
        if driver.current_url != current_url:
            print("Página mudou. Retornando...")
            driver.back()  # Retorna para a página anterior
            time.sleep(random.uniform(1, 3))  # Pausa após voltar

    if "click" in selected_behaviors:
        # Clique aleatório em links ou elementos visíveis
        clickable_elements = driver.find_elements(By.CSS_SELECTOR, 'a, button, [role="button"]')
        if clickable_elements:
            element = random.choice(clickable_elements)
            
            # Captura o URL atual antes do clique
            current_url = driver.current_url
            
            # Executa o clique
            element.click()
            
            # Pausa para permitir a navegação
            time.sleep(random.uniform(1, 3))
            
            # Verifica se o URL mudou após o clique
            if driver.current_url != current_url:
                print("Página mudou. Retornando...")
                driver.back()  # Retorna para a página anterior
                time.sleep(random.uniform(1, 3))  # Pausa após voltar

    if "pause" in selected_behaviors:
        # Espera aleatória entre 2 e 5 segundos
        time.sleep(random.uniform(2, 5))  # Pausa para simular o tempo de leitura


def run(keywords:str)-> None:
    # Configure logging
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"logs/{current_date}_lowies.log"
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
    chrome_options = uc.ChromeOptions()
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
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # rotate user agents 
    chrome_options.add_argument(f'user-agent={user_agent}')    
    #chrome_options.add_argument("--headless=new")


    driver = uc.Chrome(options=chrome_options, seleniumwire_options={})
    # Change the property value of the navigator for webdriver to undefined
    stealth(driver,
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    
    
    driver.request_interceptor = lambda request: request.headers.update({
        "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.lowes.com"
    })

    
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
        Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        Object.defineProperty(navigator, 'plugins', {get: () => [{name: 'Chrome PDF Viewer'}, {name: 'Native Client'}]});
    """)
    driver.set_page_load_timeout(30)

    


    search_for = keywords
    #----------------------------------------------------------------Functions-------------------------------------------------------------------------#

    # def handle_survey():
    #     try:
    #         # If survey is noticed then click the no button, else, continue
    #         no_thanks_button = WebDriverWait(driver, 2).until(
    #             EC.presence_of_element_located((By.ID, "survey_invite_no"))
    #         )
    #         no_thanks_button.click()
    #         print("Survey dismissed")
    #         logger.info("Survey appeared and was dismissed")
    #     except:
    #         print("No survey popup")
            
    def scrape_page(driver):
        global links
        global next_page
        # handle_survey()    
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        mimic(driver)
        print("Scrolled to bottom of the page.")
        elements_container = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.CLASS_NAME,class_items_list)
        ))
        try:
            mimic(driver)
            elems = WebDriverWait(elements_container, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, class_items)))
            print(f"Found {len(elems)} elements with class {class_items}.")
            logger.info(f"Found {len(elems)} elements with class {class_items}.")

            tags = [elem.find_element(By.TAG_NAME, "a") for elem in elems]
            links.extend([tag.get_attribute("href") for tag in tags])
            
            try:
                mimic(driver)
                next_page = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, aria_label_next_button))).get_attribute("href")
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
        # handle_survey()

        product_info = {'Link': link}
        unwanteds = ["Package", "Stacking Kit", "sorry"]

        def log_error(section, error):
            print(f"Error in {section}: {error}")
            logger.error(f"Error in {section}: {error}")

        def get_element_text(by, identifier, section_name, timeout=20):
            try:
                mimic(driver)
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, identifier))
                )
                return element.text
            except NoSuchElementException as e:
                log_error(section_name, e)
                return "N/A"
            except TimeoutException as e:
                log_error(section_name, e)
                return "N/A"
            except Exception as e:
                log_error(section_name, e)
                return "N/A"

        def get_element_attribute(by, identifier, attribute, section_name, timeout=20):
            try:
                mimic(driver)
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, identifier))
                )
                return element.get_dom_attribute(attribute)
            except NoSuchElementException as e:
                log_error(section_name, e)
                return "N/A"
            except TimeoutException as e:
                log_error(section_name, e)
                return "N/A"
            except Exception as e:
                log_error(section_name, e)
                return "N/A"

        # Product Name
        mimic(driver)
        product_info['Name'] = get_element_text(By.TAG_NAME, "h1", "Product Name")
        if any(unwanted in product_info['Name'] for unwanted in unwanteds):
            return

        # Product SKU
        product_info['SKU'] = get_element_text(By.CLASS_NAME, class_product_sku, "Product SKU").replace("Item #|Model #","").split()[-1]

        # Product Image
        product_info['Image Link'] = get_element_attribute(By.CLASS_NAME, class_product_img, 'src', "Product Image")

        # Product Reviews
        product_info['Five Star'] = get_element_text(By.CLASS_NAME, class_product_5_star, "Five Star Reviews", timeout=30)
        product_info['Review Amount'] = get_element_text(By.CLASS_NAME, class_product_review_amount, "Review Amount", timeout=30)
        
        # Product Comments Summary

        # Product Price
        try:
            product_info['Price'] = get_element_text(By.CLASS_NAME, class_product_price, "Price", timeout=30)
        except Exception as e:
            try:
                product_info['Price'] = get_element_text(By.CLASS_NAME, class_product_price2, "Price", timeout=30)   
            except Exception as e:
                logger.log(f"Error getting price: {e}")
                product_info['Price'] = ""

        # # More Product Images
        # inner_div_more_images = []
        # btn_images = []
        # images = []
        # try:
        #     btn_more_images = WebDriverWait(driver, 5).until(
        #         EC.element_to_be_clickable((By.CLASS_NAME, class_btn_more_images)))
        #     btn_more_images.click()
        #     try:
        #         div_ol_more_images = driver.find_element(By.CLASS_NAME,'carousel-indicate.flex.flex-row.flex-wrap')
        #         try:
        #             div_li_more_images = div_ol_more_images.find_elements(By.CLASS_NAME,'thumbnail-content.inline-block.mr-150.mb-150.inline-align-top')
        #             try:
        #                 for each_li in div_li_more_images:
        #                     inner_div_more_images.append(each_li.find_element(By.CLASS_NAME,class_div_images))
        #                 for each_div_more_images in inner_div_more_images:
        #                     btn_images.append(each_div_more_images.find_element(By.TAG_NAME, 'button'))
        #                 for each_btn in btn_images:
        #                     try:
        #                         images.append(each_btn.find_element(By.TAG_NAME,'img').get_attribute('src'))
        #                     except: pass
        #                 product_info['More Images Links'] = images  
        #             except Exception as e: 
        #                 product_info['More Images Links'] = "N/A"
        #                 print("Error getting More Images could not get the div, or buttons, or image of each image", e)
        #         except Exception as e:
        #             product_info['More Images Links'] = "N/A"
        #             print("Error getting More Images could not get the <li>s", e)    
        #     except Exception as e:       
        #         product_info['More Images Links'] = "N/A"
        #         print("Error getting More Images could not get the <ol>", e) 
        # except Exception as e: 
        #     product_info['More Images Links'] = "N/A"
        #     logger.error("Error getting More Images, could not click in the more images button", e)

        # # Product Videos
        # try:
        #     videos=[]
        #     button_list = []
        #     btn_videos = driver.find_element(By.CLASS_NAME, class_videos_btn)
        #     btn_videos.click()
        #     try:    
        #         list_of_videos = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME,class_videos_list)))      
        #         try:
        #             for item in list_of_videos:
        #                 button_list.append(item.find_element(By.CLASS_NAME,class_each_video_btn))
        #             try:
        #                 for button in button_list:
        #                     try:
        #                         button.click()
        #                         video = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.TAG_NAME,'source'))).get_attribute('src')
        #                         videos.append(video)
        #                     except:
        #                         pass
        #                 product_info['Videos Links'] = videos
        #             except Exception as e: print("Could not get the buttons or the videos", e)
        #         except Exception as e: print("Could not get the list of videos", e)
        #     except Exception as e: print("Could not find the video button, error: ", e)              
        # except Exception as e:
        #     product_info['Videos Links'] = "N/A"
        #     print("Error getting Videos Links:", e)    
        # try: 
        #     driver.find_element(By.CLASS_NAME,"c-close-icon.c-modal-close-icon").click()
        # except Exception as e:
        #     print("Couldn't click quit button, refreashing...")
        #     driver.refresh()

        try:
            description_features = []

            try:
                mimic(driver)
                # Espera até a div estar visível e acessível
                div = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_product_features_div))
                )
                mimic(driver)
                # Espera e extrai a descrição das características principais
                features_description = WebDriverWait(div, 4).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_product_features_description_text))
                ).text
                description_features.append(features_description)
                
            except NoSuchElementException:
                logger.log('No such element: Could not get product description')  
            except TimeoutException:
                logger.log('TimeoutError: Could not get product description')  
            except Exception as e:
                logger.log(f"Error getting description: {e}") 

            # Espera pela div contendo a lista de características
            div_of_features = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_features_div_of_ul_li))
            )

            # Extrai a lista de características
            mimic(driver)
            list_of_features = div_of_features.find_elements(By.TAG_NAME, "li")
            feature = 1

            for each_element in list_of_features:
                try:
                    p = each_element.find_element(By.TAG_NAME, 'p')
                    if p:  # Verifica se o <p> existe antes de tentar acessar o texto
                        feature_line = f"Feature {feature}: {p.text}"
                        description_features.append(feature_line)
                        feature += 1
                except Exception as e:
                    print(f"Error extracting feature {feature}: {e}")
                    continue

            product_info['Description'] = '\n'.join(description_features)

        except Exception as e:
            product_info['Description'] = "N/A"
            print(f"Error getting Features: {e}")


        try:
            mimic(driver)
            # Wait for the div containing guide items to be present on the page
            guides_div = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_guides_div))
            )
            
            # Find all guide items inside the guides div
            guide_items = guides_div.find_elements(By.CLASS_NAME, class_product_guides)
            
            # Loop through each guide item and extract the 'href' attribute of the <a> tags inside
            for guide_item in guide_items:
                try:
                    mimic()
                    # Find the <a> tag inside the guide item and extract its 'href' attribute
                    link = guide_item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    # Find the <span> tag inside the guide item (adjust if necessary)
                    name = guide_item.find_element(By.TAG_NAME, 'span').text
                    
                    if link:
                        # If name already exists in product_info, append the link to a list
                        if name in product_info:
                            if isinstance(product_info[name], list):
                                product_info[name].append(link)
                            else:
                                product_info[name] = [product_info[name], link]
                        else:
                            product_info[name] = link
                        
                except Exception as e:
                    print(f"Error extracting link from guide item: {e}")
            
        except Exception as e:
            print(f"Error retrieving guide links: {e}")            
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------GET SPECS
        try:
            mimic(driver)
            # Try to find the div with the specifications
            specs_div = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_specs_div))
            )
            
            # Find all tables inside the specs div
            tables = specs_div.find_elements(By.TAG_NAME, 'table')
            
            for table in tables:
                try:
                    # For each table, get the tbody element(s)
                    tbodys = table.find_elements(By.TAG_NAME, 'tbody')
                    
                    for tbody in tbodys:
                        # Get all tr elements from the tbody
                        trs = tbody.find_elements(By.TAG_NAME, 'tr')
                        
                        for tr in trs:
                            # For each tr, get the tds
                            tds = tr.find_elements(By.TAG_NAME, 'td')
                            
                            if len(tds) >= 2:
                                # Assume the first td is the header (even index)
                                # and the second td is the content (odd index)
                                header = tds[0].text.strip()
                                content = tds[1].text.strip()
                                
                                # Store the header and content directly in product_info
                                product_info[header] = content

                except Exception as e:
                    print(f"Error extracting specs from table: {e}")

            # If no specifications were found initially, try to expand the full specifications
            if not product_info:
                print("Specifications not found in the initial div. Trying to expand specs...")

                # Try to click on the button to expand the full specs
                try:
                    mimic(driver)
                    show_full_specs_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, data_testid_show_full_specs))
                    )
                    
                    # Click on the button to expand the full specifications
                    driver.execute_script("arguments[0].click();", show_full_specs_button)

                    # Wait for the specs to expand and then re-run the logic
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, class_specs_div))
                    )
                    mimic(driver)
                    # Re-run the extraction logic after expanding the specs
                    specs_div = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CLASS_NAME, class_specs_div))
                    )
                    mimic(driver)
                    tables = specs_div.find_elements(By.TAG_NAME, 'table')

                    for table in tables:
                        try:
                            mimic(driver)
                            tbodys = table.find_elements(By.TAG_NAME, 'tbody')
                            
                            for tbody in tbodys:
                                trs = tbody.find_elements(By.TAG_NAME, 'tr')
                                
                                for tr in trs:
                                    mimic(driver)
                                    tds = tr.find_elements(By.TAG_NAME, 'td')
                                    
                                    if len(tds) >= 2:
                                        header = tds[0].text.strip()
                                        content = tds[1].text.strip()
                                        
                                        # Store the header and content directly in product_info
                                        product_info[header] = content

                        except Exception as e:
                            print(f"Error extracting specs from table: {e}")

                except Exception as e:
                    print(f"Error expanding the specs: {e}")

        except Exception as e:
            print(f"Error retrieving specifications: {e}")

        
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
        mimic(driver)        # handle_survey()
        time.sleep(180)
        driver.implicitly_wait(20)  # Wait for it to load
        print("Page loaded.")
        logger.info("Page loaded.")

        search = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_search_bar)))
        driver.execute_script("arguments[0].scrollIntoView(true);", search)

        search.send_keys(search_for)
        mimic(driver)
        time.sleep(2)
        
        button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, class_search_button)))
        driver.execute_script("arguments[0].scrollIntoView(true);", search)

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
                    # handle_survey()
                    scrape_page(driver)
                    if next_page: 
                        i+=1
                        print(f"Navigating to next page: {next_page}: {i}")
                        logger.info(f"Navigating to next page: {next_page}: {i}")
                        mimic()
                        driver.get(next_page)
                    else: 
                        break
        #If file doesn't exist, run routine to get it and save it later
        except:
            i=1
            while True:
                print("Scraping page: ",i)
                # handle_survey()
                scrape_page(driver)
                if next_page: 
                    i+=1
                    print(f"Navigating to next page: {next_page}: {i}")
                    logger.info(f"Navigating to next page: {next_page}: {i}")
                    mimic()
                    driver.get(next_page)
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

