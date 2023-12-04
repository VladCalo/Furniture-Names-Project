from typing import Any
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import re
import subprocess
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import spacy
from spacy.matcher import Matcher
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException


class Exploration:
    def __init__(self, filename, headless=True, recursive=False) -> None:
        # self.chrome_options = Options()
        # self.chrome_options.add_argument('--disable-extensions')
        # self.chrome_options.add_argument("--disable-notifications")
        if headless:
            pass
            # self.chrome_options.add_argument("--headless")
        # self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver = webdriver.Firefox()
        self.driver.set_script_timeout(30)

        # Set the page load timeout to a lower value (e.g., 30 seconds)
        self.driver.set_page_load_timeout(30)

        # Set the implicit wait timeout to a lower value (e.g., 30 seconds)
        self.driver.implicitly_wait(30)
        
        self.initial_links= Exploration.get_links(filename)
        self.recursive = recursive 
        
    @staticmethod
    def get_links(filename):
        print("################################## GETTING LINKS #################################")
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        repo_dir = result.stdout.strip()
        training_csv_path = repo_dir + f"/data/{filename}"
        
        df = pd.read_csv(training_csv_path, header=None, names=["urls"])
        return df['urls'].tolist()
    
    @staticmethod
    def is_valid_https_link(link):
        pattern = re.compile(r'^https://', re.IGNORECASE)
        return bool(pattern.match(link))
    
    def extract_after_https(self, link):
        pattern = re.compile(r'^https?://(?:www\.)?([^\.]+)')
        try:
            match = pattern.match(link)
            if match:
                domain = match.group(1)
                for l in self.initial_links:
                    if domain in l:
                        return True
        except Exception as e:
            print(f"Error in extract_after_https: {e}")
        return False
               
    def get_all_links(self, initial_links, depth=2, visited=set()):
        if depth <= 0:
            return set()
        unique_links = set()
        for link in initial_links:
            if link is not None:
                if link not in list(visited) and self.is_valid_https_link(link):
                    try:
                        self.driver.get(link)
                        print(link)
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, 'body')))
                            
                        visited.add(link)
                                
                        curr_page_links = {a.get_attribute('href') for a in self.driver.find_elements(By.TAG_NAME, 'a')}
                        unique_links.update(curr_page_links)
                                
                        child_links = curr_page_links - visited
                        child_links = [cl for cl in child_links if self.extract_after_https(cl) == True]
                        unique_links.update(self.get_all_links(child_links, depth - 1, visited))
                    except WebDriverException as e:
                        print(f"Error accesing link: {link} with error: {e}")
                        continue
        # with open("/Users/vladcalomfirescu/Desktop/MyFiles/DEV/ML/Veridion-Project/data/test_data/all_links.csv", 'w') as f:
        #     for link in unique_links:
        #         f.write(link + "\n")
        
        return list(unique_links)