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
from urllib.parse import urljoin
import wakepy

mode = wakepy.keep.presenting()


#-----------------------------------------------------Personalization Variables---------------------------------------------------------------------#
url = "https://www.samsung.com/sec/washing-machines/all-washing-machines/?bespoke-grande-ai-onebody"


#-----------------------------------------------------Do Not Modify if no changes are required------------------------------------------------------#

# Global Variables
next_page = None
links = []
products_data = []
main_headers = ["Link", "Name", "SKU", "Price", "Five Star", "Review Amount", "Image Link", 'Description', 'More Images Links', 'Videos Links'] 
#Links - test and speed process
test_links = "statics/test_product_link_samsung_ko.csv"
real_links = "statics/product_link_samsung_ko.csv"
#Outputs
test_output_path = 'outputs/samsung_ko/test_product_data.csv'
real_output_path= 'outputs/samsung_ko/product_data.csv'
#other paths
old_file = 'statics/old_file.csv'
#Force run
no_file = "statics/no_file.csv"

class_list_items = "list list-type"

class_product_sku = 'itm-sku b2c-itm-sku compare-box-align'
class_product_img = 'view-image-box slick-slide slick-current slick-active'
class_product_5_star = 'itm-rating b2c-itm-rating'
class_product_price = 'itm-price itm-type'
class_more_images_div = 'prod-image-navi-wrap' # > find img > src

class_claim_div = 'heightWrap'
class_claims_placeholder_1 = 'wrap-component feature-benefit new-component pt-none pb-none w1440px img-bottom'
class_claims_placeholder_2 = 'wrap-component textbox-simple new-component pt-none pb-none w1440px'

class_spec_container = 'component-con spec-all drop-component component03'
class_show_full_specs='dropButton' 
class_div_prod_spec_table="spec-table" # select <ol> > select <li>s > select texts> for li in lis {title: li.texts[0], content: li.texts[1]}



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
    BASE_URL = "https://www.samsung.com/"

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
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("Scrolled to bottom of the page.")
            
            # Encontrar todos os elementos da página
            div_products = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust(class_list_items)))
            )
            products = div_products.find_elements(By.CLASS_NAME,'item-inner')             

            # Obter os links dos elementos encontrados
            tags = [product.find_element(By.CLASS_NAME, item_adjust("card-img cardImgSwiper")) for product in products]
            links = [tag.get_dom_attribute("href") for tag in tags if tag.get_dom_attribute("href")]
            print(f"Captured {len(links)} new links from the current page.")
                
            # Salvar os links no CSV
            df = pd.DataFrame(links, columns=['Product Links'])
            df.to_csv(real_links, index=False)
        except Exception as e:
            print("Unable to run the code, error: ",e)

    def process_product(driver, link):
        global products_data, main_headers
        driver.get(link)
        #----------------------------------------------------------------------------------------------------------------------------------------------------------------------GET LINK
        product_info = {'Link': link}
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT NAME
        try:
            product_name_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "goodsDetailNm"))
            )
            product_info['Name'] = product_name_element.text
            print("hi")
        except Exception as e:
            product_info['Name'] = ""
            print("Error getting product name:", e)
            
        unwanted = "+"
        if product_info['Name'] and unwanted in product_info["Name"]:
            print(f"Unwanted character found in product name: {product_info['Name']}")
            return   
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT SKU
        try:
            product_sku_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust(class_product_sku)))
            )
            product_info['SKU'] = product_sku_element.text
        except Exception as e:
            product_info['SKU'] = ""
            print("Error getting product SKU:", e)
            
            
            #--------------------------------------------------GET COLOR VARIANTS SKUs
        try:
            color_variants_skus_list = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,item_adjust("dropList itm-color-list")))
            ).find_elements(By.TAG_NAME,"li")
            color_variants_skus = []
            for li in color_variants_skus_list:
                color_variants_skus.append((li.find_element(By.TAG_NAME,'input').get_dom_attribute('data-mdl-code')))
            product_info["Color Variant SKUs"] = "\n".join(color_variants_skus)

        except Exception as e:
            print("Error getting color variants skus, error: ",e)
            product_info["Color Variant SKUs"] = ""

        #-------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT FLAGS
        try:
            product_flags = driver.find_elements(By.CLASS_NAME,'itm-flag')
            product_flags_text = [flag_text.text for flag_text in product_flags]
            product_info['Flags'] = "\n".join(product_flags_text)
        except Exception as e:
            product_info['Flags'] = ""
            print("Error fetching flags: ", e)            
            
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT IMAGE    
        try:
            product_image_link = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust(class_product_img))))
            product_info['Image Link'] = f"https{product_image_link.get_dom_attribute('src')}"
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
            price_section = (driver.find_element(By.CLASS_NAME, item_adjust(class_product_price)))
            price = price_section.find_element(By.TAG_NAME,"span").text
            product_info['Price'] = price
        except Exception as e:
            product_info['Price'] = ""
        #--------------------------------------------------------------------------------------------------------------------------------------------------------GET MORE PRODUCT IMAGE
        images = []
        try:
            div_more_images = driver.find_element(By.CLASS_NAME, item_adjust(class_more_images_div))
            try:
                # Capturar links das imagens dentro do <div>
                images = [
                    img.get_dom_attribute("src") 
                    for img in div_more_images.find_elements(By.TAG_NAME, 'img') 
                    if img.get_dom_attribute("src")
                ]
                
                # Ajustar os links e preparar para salvar
                images_adjusted = list(map(lambda x: "https" + x if not x.startswith("http") else x, images))
                product_info['More Images Links'] = "\n".join(images_adjusted)
            except Exception as e: 
                product_info['More Images Links'] = "N/A"
                print("Error getting More Images could not get the images:", e)
        except Exception as e:       
            product_info['More Images Links'] = "N/A"
            print("Error getting More Images could not get <div>:", e)
        
           
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------GET SPECS
        try:
            # Aguarda o botão estar presente e clicável
            spec_container = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, item_adjust(class_spec_container)))
                            )
            show_full_specs_btn = spec_container.find_element(By.CLASS_NAME,item_adjust(class_show_full_specs))
            
            # Rola até o botão para garantir visibilidade
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_full_specs_btn)
            print("Scrolled into view.")
            
            # Tenta clicar no botão usando JavaScript ou Selenium
            try:
                # Primeiro, tenta clicar diretamente
                show_full_specs_btn.click()
                print("Clicked using Selenium.")
            except Exception as e:
                # Se o clique direto falhar, tenta com JavaScript
                driver.execute_script("arguments[0].click();", show_full_specs_btn)
                print("Clicked using JavaScript fallback.")
        except Exception as e:
            print("Couldn't click 'show full specs' button:", e)

#class_div_prod_spec_table="spec-table" # select <ol> > select <li>s > tah> for li in lis {title: li.texts[0], content: li.texts[1]}

        try:
            product_specs = WebDriverWait(spec_container, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, item_adjust(class_div_prod_spec_table)))
            ).find_elements(By.TAG_NAME,'ol')

            for ol in product_specs:
                for spec_item in ol.find_elements(By.TAG_NAME, 'li'):
                    try:
                        try:
                            header = spec_item.find_element(By.TAG_NAME, 'button').text
                        except:
                            header = spec_item.find_element(By.TAG_NAME,"strong").text
                        spec = spec_item.find_element(By.TAG_NAME, "p").text
                        product_info[header] = spec

                        if header not in main_headers:
                            main_headers.append(header)
                    except Exception as e:
                        print(f"Error extracting specification: {e}")

        except Exception as e:
            print(f"Error occurred while getting specifications: {e}")

            
        print(f'COMPLETE SPEC ADDED:{product_info}\n')
        products_data.append(product_info)   

        #------------------------------------------------------------------------------------------------------------------------------------------------------------GET PRODUCT CLAIMS        
        try:
            claims_div = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME,item_adjust(class_claim_div)))
            )
            
            claim_list = (
                WebDriverWait(claims_div, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, item_adjust(class_claims_placeholder_1)
                         ))
                ) 
                +
                WebDriverWait(claims_div, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME,item_adjust(class_claims_placeholder_2)
                    ))
                )
            )
            
            for i, claim in enumerate(claim_list, start=1):  # Enumerate os claims
                list_of_content = []

                # Capturar texto
                texts = claim.text.strip()
                if texts:
                    list_of_content.append(texts)
                else:
                    print(f"No text found in claim {i}")

                # Capturar imagens (espera explícita)
                try:
                    images_list = WebDriverWait(claim, 10).until(
                        EC.visibility_of_all_elements_located((By.TAG_NAME, 'img'))
                    )
                    for image in images_list:
                        src = image.get_dom_attribute('src') or image.get_dom_attribute('data-src')
                        if src:
                            list_of_content.append(src)
                        else:
                            print(f"Image with no valid 'src' or 'data-src' in claim {i}")
                except Exception as e:
                    print(f"Error loading images in claim {i}: {e}")

                # Capturar vídeos (espera explícita)
                try:
                    videos_list = WebDriverWait(claim, 10).until(
                        EC.visibility_of_all_elements_located((By.TAG_NAME, 'video'))
                    )
                    # Para cada vídeo em videos_list, tente encontrar o primeiro elemento <source>.
                    source_list = []
                    for video in videos_list:
                        try:
                            source = video.find_element(By.TAG_NAME, 'source').get_dom_attribute("src")  # Busca apenas o primeiro <source>
                            source_list.append(source)
                        except NoSuchElementException:
                            print("Elemento <source> não encontrado para um vídeo.")                        
                    if source_list:
                        list_of_content.append("\n".join(source_list))
                    else:
                            print(f"Video with no 'src' in claim {i}")
                except Exception as e:
                    print(f"Error loading videos in claim {i}: {e}")

                # Capturar links (sem espera explícita, mas verificando conteúdo)
                claim_links = claim.find_elements(By.TAG_NAME, 'a')
                if claim_links:
                    list_of_content.extend([
                        link.get_dom_attribute('href') or "" for link in claim_links
                    ])
                else:
                    print(f"No links found in claim {i}")

                # Remover valores vazios ou `None`
                list_of_content = [content for content in list_of_content if content]

                # Salvar dados no dicionário
                if list_of_content:
                    product_info[f'Claim item {i}'] = '\n'.join(list_of_content)
                    print(f'Claim item {i}: {product_info[f"Claim item {i}"]}\n')
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
                

    def process_products(driver):
        '''
        Process each link and clean the variable right after.
        \nDROP DUPLICATES → There are quite a lot of sponsored data
        '''
        
        global links
        links = pd.Series(links).drop_duplicates().tolist()
        links = [link for link in links if link]  # Remove valores inválidos

        for idx, link in enumerate(links, start=1): 
            if not link:  # Ignora valores inválidos como segurança extra
                print(f"Skipping invalid link at index {idx}, link: {link}")
                continue
            try:
                print(f'Before : {link} || After : {urljoin(BASE_URL,link)}')
                process_product(driver, urljoin(BASE_URL, link))
                print(f"Processing {idx}/{len(links)}: {urljoin(BASE_URL, link)}")
            except Exception as e:
                print(f"Error getting into link:{link}\nReason: {e}")
                continue

        links.clear()


    #---------------------------------------------------------------------------Begining---------------------------------------------------------------------#
    global products_data
    try:        
        driver.get(url)
        driver.implicitly_wait(20)  # Wait for it to load
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
                scrape_page(driver)
        #If file doesn't exist, run routine to get it and save it later
        except:
            scrape_page(driver)
        
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
with mode:
    run() 