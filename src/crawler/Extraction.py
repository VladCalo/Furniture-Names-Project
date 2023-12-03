import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import re
import subprocess
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import spacy
from urllib.parse import urlparse, urljoin
from spacy.matcher import Matcher
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from Exploration import Exploration


class Extraction(Exploration):
    def __init__(self, filename, headless=True, recursive=False) -> None:
        super().__init__(filename=filename, headless=headless, recursive=recursive)
   
    def get_url_content(self, url):
        """
        Returns:
        page_text: all the text content from the url
        h_text: a list of texts from the all header elements
        """
        try:
            self.driver.get(url)
            h_elements = []
            time.sleep(3)

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
                body_element = None
            
            try: 
                h_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(( By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6"))
                )
            except Exception as e:
                print (f"h_elements Error: {e}")
                h_elements = None
                
            if h_elements:
                h_texts = []
                for header in h_elements:
                    h_texts.append(header.text)
            else:
                h_texts = None
            
            if body_element:
                page_text = body_element.text
            else:
                page_text = None
                
            print(f"{url} OK\n")
            return page_text, h_texts

        except WebDriverException as e:
            if "404" in str(e):
                print(f"Error 404: {url} not found")
            else:
                print(f"Error accessing {url}: {e}")
            return None, None

    def get_data(self):  
        raw_data = []
        h_elements = []
        
        if self.recursive:
            urls = super().get_all_links(self.initial_links)
        else:
            urls = self.initial_links
        print("################################## GET DATA FROM PAGES #################################")
        for url in urls:
            # if self.extract_after_https(url):
                print(f"Getting data from {url}")
                if url:
                    page_text, h_texts = self.get_url_content(url)

                    if page_text and "404" not in str(page_text):
                        raw_data.append((url, page_text))

                    if h_texts:
                        h_texts = [header for header in h_texts if header != "" and "404" not in header]
                        h_elements.append((url, h_texts))
                    
        h_elements = [(url, h_texts) for url, h_texts in h_elements if h_texts]
        return raw_data, h_elements

    def close(self):
        self.driver.quit()



