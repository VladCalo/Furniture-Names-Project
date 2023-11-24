import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
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
            self.chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        
    @staticmethod
    def get_links():
        csv_path = '/Users/vladcalomfirescu/Desktop/MyFiles/DEV/ML/Veridion-Project/data/links.csv'
        df = pd.read_csv(csv_path, header=None, names=['urls'])
        return df
    
    def get_url_content(self, url):
        try:
            self.driver.get(url)
            
            time.sleep(5)
            
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except:
                pass
            
            WebDriverWait(self.driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            body_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            page_text = body_element.text
            return page_text
        
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
        df = Extraction.get_links()
        for idx, row in df.head(iterations).iterrows():
            url = row.get('urls', '')
            if url:
                page_text = self.get_url_content(url)
                    
                if page_text and '404 Page Not Found' not in str(page_text):
                    raw_data.append((url, page_text))
        return raw_data
    
    def heuristic_matching(self):
        nlp = spacy.load("en_core_web_sm")
        raw_data = self.get_data()
                
        
    def open_url(self, url):
        self.driver.get(url)
        
    def close(self):
        self.driver.quit()
        
        
extraction = Extraction()
p = extraction.get_data(iterations=5)
print("this is p")
for item in p:
    print(item)
    print("\n###################\n")
extraction.close()

    