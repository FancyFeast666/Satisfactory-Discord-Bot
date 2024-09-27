from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

#this file is used to handle the web-scraping functionality of the Discord Bot

def web_scrape():
    service = Service(
        r'XXX\chromedriver.exe')  # Replace with your ChromeDriver path

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless") #this will make it so you do not see the visuals of the website as the page is being scraped, useful for helping with system resources
    chrome_options.add_argument("--disable-features=NetworkService")
    chrome_options.binary_location = (r'XXX\chrome.exe')  #replace this with your Chrome developer path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get('https://satisfactory-calculator.com/en/interactive-map') #website to be scraping from

    dismiss_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#patreonModal button.close')) #selenium will look for the dismiss button on the website and click it
    )

    dismiss_button.click()

    file_input = driver.find_element(By.ID, 'saveGameFileInput') #finds the element to upload the save file

    file_input.send_keys(r'XXX\FactoryGame\Saved\SaveGames\server\scrape.sav') #replace this with where you save your server saves, by default it is under appdata. This uses its own file called scrape.sav

    time.sleep(8) #delay to process the upload on the website

    with open('page_source.txt', 'w', encoding='utf-8') as file: #this scrapes the entire page source onto a txt file to be used later. Will be optimized further later on.
        file.write(driver.page_source)
    driver.quit() #ends the driver process

def get_hard(): #this function is used to obtain the amount of hard drives collected thus far in the save
    search_term = "\"hardDrives\" data-collected=\""
    with open("page_source.txt", 'r', encoding='utf-8') as file:
        for line in file:
            if search_term in line:
                temp = line
                file.close()
                break
    match = re.search(r'data-collected="(\d+)"', line)
    num = -1
    if match:
        num = int(match.group(1))
    return num

def get_yellow_slug(): #this function is used to obtain the amount of yellow slugs collected thus far in the save
    search_term = "\"yellowSlugs\" data-type=\"Desc_Crystal_C\" data-collected=\""
    with open("page_source.txt", 'r', encoding='utf-8') as file:
        for line in file:
            if search_term in line:
                temp = line
                file.close()
                break
    match = re.search(r'data-collected="(\d+)"', line)
    num = -1
    if match:
        num = int(match.group(1))
    return num
def get_blue_slug(): #this function is used to obtain the amount of blue slugs collected thus far in the save
    search_term = "\"greenSlugs\" data-type=\"Desc_Crystal_C\" data-collected=\""
    with open("page_source.txt", 'r', encoding='utf-8') as file:
        for line in file:
            if search_term in line:
                temp = line
                file.close()
                break
    match = re.search(r'data-collected="(\d+)"', line)
    num = -1
    if match:
        num = int(match.group(1))
    return num
def get_purple_slug(): #this function is used to obtain the amount of purple slugs collected thus far in the save
    search_term = "\"purpleSlugs\" data-type=\"Desc_Crystal_C\" data-collected=\""
    with open("page_source.txt", 'r', encoding='utf-8') as file:
        for line in file:
            if search_term in line:
                temp = line
                file.close()
                break
    match = re.search(r'data-collected="(\d+)"', line)
    num = -1
    if match:
        num = int(match.group(1))
    return num
def get_mercer(): #this function is used to obtain the amount of mercer spheres collected thus far in the save
    search_term = "\"mercerSpheres\" data-collected=\""
    with open("page_source.txt", 'r', encoding='utf-8') as file:
        for line in file:
            if search_term in line:
                temp = line
                file.close()
                break
    match = re.search(r'data-collected="(\d+)"', line)
    num = -1
    if match:
        num = int(match.group(1))
    return num

def get_somersloop(): #this function is used to obtain the amount of somersloops collected thus far in the save
    search_term = "\"somersloops\" data-collected=\""
    with open("page_source.txt", 'r', encoding='utf-8') as file:
        for line in file:
            if search_term in line:
                temp = line
                file.close()
                break
    match = re.search(r'data-collected="(\d+)"', line)
    num = -1
    if match:
        num = int(match.group(1))
    return num