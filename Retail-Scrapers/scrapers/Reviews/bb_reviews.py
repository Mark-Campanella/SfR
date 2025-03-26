import time
import logging
from typing import List, Dict, Any
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium_stealth import stealth

import pandas as pd

# ------------------------------
# Selectors configuration
# ------------------------------
# Product details selectors
SELECTOR_PRODUCT_ID = "model-and-sku.body-copy-lg.flex.gap-50" # > get the first <dd> element's text
SELECTOR_PRODUCT_NAME = "v-fw-regular" # get txt
SELECTOR_PRODUCT_LINK = "v-fw-regular" # get href
SELECTOR_PRODUCT_FIVE_STAR = "ugc-c-review-average.font-weight-medium.order-1" # get txt
SELECTOR_PRODUCT_REVIEWS_AMOUNT = "c-reviews.order-2" # get txt, remove (reviews) from text > convert to integer
SELECTOR_REVIEW_SUMMARY = "mb-200.mt-none" # get txt
SELECTOR_PRODUCT_PRO_CONS = "filters-wrap.mb-none" #pro is [0] and cons is [1]

# Review selectors
SELECTOR_REVIEWS = "reviews-list" # this is an ul > get all <li> elements, for each li get the following:
SELECTOR_REVIEW_ID = "ugc-author.v-fw-medium.body-copy-lg" # get txt and hash it
SELECTOR_REVIEW_DATE = "posted-date-ownership.disclaimer.v-m-right-xxs" # get txt
SELECTOR_REVIEW_RATING = "c-ratings-reviews.flex.c-ratings-reviews-small.align-items-center.gap-50" # get p, it is hidden
SELECTOR_REVIEW_TITLE = "h4"
SELECTOR_REVIEW_TEXT = "pre-white-space" # get txt
SELECTOR_REVIEWER_RECOMMENDS = "ugc-recommendation" # get txt

# Next page button selector for reviews pagination
SELECTOR_NEXT_PAGE = "page.next" # > get a > get href

# ------------------------------
# Scraping functions
# ------------------------------

def dismiss_survey(driver: webdriver.Chrome, logger: logging.Logger) -> None:
    """
    Dismiss the survey popup if it is displayed.
    """
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
        logger.info("No survey popup")
        
def scrape_product_details(driver: webdriver.Chrome, logger: logging.Logger) -> Dict[str, str]:
    """
    Scrape the product details from the current product page.
    
    Returns:
        A dictionary containing product details.
    """
    details: Dict[str, str] = {}
    time.sleep(5)
    try:
        details["product_id"] = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, SELECTOR_PRODUCT_ID))).find_element(By.TAG_NAME, "dd").text or ""
        details["product_name"] = driver.find_element(By.CLASS_NAME, SELECTOR_PRODUCT_NAME).text or ""
        details["product_link"] = driver.find_element(By.CLASS_NAME, SELECTOR_PRODUCT_LINK).get_dom_attribute("href") or ""
        details["product_five_star"] = driver.find_element(By.CLASS_NAME, SELECTOR_PRODUCT_FIVE_STAR).text or ""
        details["product_reviews_amount"] = int(driver.find_element(By.CLASS_NAME, SELECTOR_PRODUCT_REVIEWS_AMOUNT).text.replace("Reviews", "").replace("(", "").replace(")", "").replace(".","").strip()) or ""
        details["review_summary"] = driver.find_element(By.CLASS_NAME, SELECTOR_REVIEW_SUMMARY).text or ""

    except NoSuchElementException as e:
        logger.error(f"Error scraping product details: {e}")
    except ValueError as e:
        logger.error(f"Error converting reviews amount to integer: {e}")
    except AttributeError as e:
        logger.error(f"Error extracting pros and cons: {e}")
    except KeyError as e:    
        logger.error(f"Error extracting pros and cons: {e}")
    except TypeError as e:  
        logger.error(f"Error extracting pros and cons: {e}")
    except IndexError as e: 
        logger.error(f"Error extracting pros and cons: {e}")
    except Exception as e:
        logger.error(f"Error scraping product details: {e}")
    return details

def scrape_reviews(driver: webdriver.Chrome, logger: logging.Logger) -> List[Dict[str, str]]:
    """
    Scrape all reviews from the current page of a product.
    
    Returns:
        A list of dictionaries where each dictionary represents a review.
    """
    reviews_list: List[Dict[str, str]] = []
    try:
        reviews = driver.find_element(By.CLASS_NAME, SELECTOR_REVIEWS)
        review_elements = WebDriverWait(reviews,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "review-item")))
        for review in review_elements:
            try:
                random_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
                review_data: Dict[str, str] = {
                    "review_id": hash(WebDriverWait(reviews,10).until(EC.presence_of_element_located((By.CLASS_NAME, "review-item-content.col-xs-12.col-md-9"))).
                                             find_element(By.CLASS_NAME, SELECTOR_REVIEW_ID).text or random_id) or "",
                    "review_date": review.find_element(By.CLASS_NAME, SELECTOR_REVIEW_DATE).text or "",
                    "review_rating": int(review.find_element(By.CLASS_NAME, SELECTOR_REVIEW_RATING).
                                                find_element(By.TAG_NAME, "p").get_attribute("innerHTML").
                                                replace("Rated", "").replace("out of 5 stars", "").strip()) or "",
                    "review_title": review.find_element(By.TAG_NAME, SELECTOR_REVIEW_TITLE).text or "",
                    "review_text": review.find_element(By.CLASS_NAME, SELECTOR_REVIEW_TEXT).text or "",
                    "reviewer_recommends": review.find_element(By.CLASS_NAME, SELECTOR_REVIEWER_RECOMMENDS).text or "",
                }
                reviews_list.append(review_data)
            except NoSuchElementException as e:
                logger.error(f"Error scraping a review: {e}")
            except Exception as e:
                logger.error(f"Error processing a review: {e}")

    except Exception as e:
        logger.error(f"Error scraping reviews: {e}")
    return reviews_list

def click_next_page(driver: webdriver.Chrome, logger: logging.Logger, retries: int = 3) -> bool:
    """
    Click the next page button for reviews if available.
    
    Returns:
        True if the next page button was clicked, else False.
    """
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, SELECTOR_NEXT_PAGE))
        ).find_element(By.TAG_NAME, "a")
                
        if next_button.is_displayed() and next_button.is_enabled():
            current_url = driver.current_url  # Save the URL before clicking
            
            next_button.click()
            logger.info("Clicked 'Next Page' button, waiting for new content...")
            WebDriverWait(driver, 10).until(
                EC.url_changes(current_url)
            )
            return True

        logger.info("Next page button is not enabled or not visible.")
        return False

    except TimeoutException:
        logger.info("No next page available or timed out waiting for navigation.")
        return False

    except NoSuchElementException:
        logger.info("Next page button not found.")
        return False
    
    except ElementClickInterceptedException:
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, "survey_invite_no"))
            )
            dismiss_survey(driver, logger)
        except TimeoutException:
            logger.info("No survey popup detected.")
            dismiss_survey(driver, logger)
            return click_next_page(driver, logger, retries - 1)
        else:
            logger.error("Max retries reached for clicking next page.")
            return False
    
    except Exception as e:
        logger.error(f"Error clicking next page button: {e}")
        return False

def scrape_product_page(driver: webdriver.Chrome, logger: logging.Logger, product_url: str) -> Dict[str, Any]:
    """
    Scrape all product details and all reviews (with pagination) from a product page.
    
    Args:
        product_url: URL of the product page.
    
    Returns:
        A dictionary containing the product information and a list of its reviews.
    """
    product_data: Dict[str, Any] = {}
    if not product_url.startswith('http'):
        product_url = 'https://www.bestbuy.com' + product_url
    try:
        driver.get(product_url)
        # Wait for the product details to load (using product name as reference)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, SELECTOR_PRODUCT_NAME))
            )
        except:
            dismiss_survey(driver, logger)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, SELECTOR_PRODUCT_NAME)))
        product_data = scrape_product_details(driver, logger)
        all_reviews: List[Dict[str, str]] = []
        # Scrape reviews from the first page
        reviews = scrape_reviews(driver, logger)
        all_reviews.extend(reviews)
        # Paginate through additional review pages if available
        while True:
            if click_next_page(driver, logger):
                time.sleep(5)
                reviews = scrape_reviews(driver, logger)
                all_reviews.extend(reviews)
            else:
                break
        product_data["reviews"] = all_reviews
    except Exception as e:
        logger.error(f"Error processing product page {product_url}: {e}")
    return product_data



def save_data_to_csv(data: List[Dict[str, Any]], logger: logging.Logger) -> None:
    """
    Save product data and reviews separately as CSVs and also create a merged version.
    
    Args:
        data: List of product dictionaries.
        product_filename: CSV filename for products.
        review_filename: CSV filename for reviews.
        logger: Logger instance.
    """
    product_df = pd.DataFrame()
    try:
        # Criar DataFrame dos produtos
        product_df = pd.DataFrame([
            {key: product.get(key, "") for key in ["product_id", "product_link", "product_name",
                                                   "product_five_star", "product_reviews_amount",
                                                   "review_summary", "pros", "cons"]}
            for product in data
        ])

        # Criar DataFrame das reviews
        review_df = pd.DataFrame([
            {**review, "product_id": product["product_id"]} 
            for product in data 
            for review in product.get("reviews", [])
        ])

        product_df['product_id']=product_df['product_id'].str.lower()
        review_df['product_id']=review_df['product_id'].str.lower()
       
        merged_df = review_df.merge(product_df, on="product_id", how="left")

        # Salvar CSV mesclado
        # merged_df.to_csv("reviews.csv", index=False, encoding="utf-8")
        logger.info(f"✅ Dados salvos com sucesso: 'reviews.csv'")
        return merged_df
    except Exception as e:
        logger.error(f"❌ Erro ao salvar CSVs: {e}")
        return product_df