import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import spacy
from spacy.matcher import Matcher
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException


class Extraction:
    def __init__(self, headless=True) -> None:
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.chrome_options)

    @staticmethod
    def get_links():
        csv_path = "/Users/vladcalomfirescu/Desktop/MyFiles/DEV/ML/Veridion-Project/data/links.csv"
        df = pd.read_csv(csv_path, header=None, names=["urls"])
        return df

    def get_url_content(self, url):
        """
        Returns:
        page_text: all the text content from the url
        h_text: a list of texts from the all header elements
        """
        try:
            self.driver.get(url)
            a_elements = h_elements = []
            time.sleep(10)

            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except:
                pass

            WebDriverWait(self.driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )

            try:
                body_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                print (f"body Error: {e}")
            
            try: 
                h_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(( By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6"))
                )
            except Exception as e:
                print (f"h_elements Error: {e}")
                
            # try: 
            #     a_elements = WebDriverWait(self.driver, 10).until(
            #         EC.presence_of_all_elements_located(( By.XPATH, "//a"))
            #     )
            # except (NoSuchElementException, StaleElementReferenceException) as e:
            #     print (f"a_elements Error: {e}")
            
            # if a_elements:
            #     h_elements += a_elements
            h_texts = []
            for header in h_elements:
                h_texts.append(header.text)

            page_text = body_element.text
            return page_text, h_texts

        except TimeoutException:
            print(f"Timed out waiting for body element on {url}")
            return None
        except WebDriverException as e:
            if "404" in str(e):
                print(f"Error 404: {url} not found")
            else:
                print(f"Error accessing {url}: {e}")
            return None

    def get_data(self, iterations=100):  
        raw_data = []
        h_elements = []
        df = Extraction.get_links()
        for _, row in df.head(iterations).iterrows():
            url = row.get("urls", "")
            if url:
                page_text, h_texts = self.get_url_content(url)

                if page_text and "404 Page Not Found" not in str(page_text):
                    raw_data.append((url, page_text))

                if h_texts:
                    h_texts = [header for header in h_texts if header != "" and "404" not in header]
                    h_elements.append((url, h_texts))
                    
        h_elements = [(url, h_texts) for url, h_texts in h_elements if h_texts]
        return raw_data, h_elements



    def close(self):
        self.driver.quit()



