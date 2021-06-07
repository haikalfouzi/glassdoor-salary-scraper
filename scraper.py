import time
import json
import pickle
import Salary
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys


def obj_dict(obj):
    return obj.__dict__
#enddef

def json_export(data, cityName):
    jsonFile = open("Data/" + cityName + ".json", "w")
    jsonFile.write(json.dumps(data, indent=4, separators=(',', ': '), default=obj_dict))
    jsonFile.close()
#enddef

def init_driver():
    driver = webdriver.Chrome(executable_path = "./chromedriver")
    driver.wait = WebDriverWait(driver, 10)
    return driver
#enddef

def login(driver, username, password):
    driver.get("http://www.glassdoor.com/profile/login_input.htm")
    try:
        user_field = driver.wait.until(EC.presence_of_element_located(
            (By.ID, "userEmail")))
        pw_field = driver.find_element_by_id("userPassword")
        login_button = driver.find_element_by_name("submit")
        user_field.send_keys(username)
        user_field.send_keys(Keys.TAB)
        pw_field.send_keys(password)
        login_button.click()
    except TimeoutException:
        print("TimeoutException! Username/password field or login button not found on glassdoor.com")
#enddef

def search(driver, city, title):
    driver.get("https://www.glassdoor.com/Salaries/index.htm")
    try:
        search_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.ID, "HeroSearchButton")))
        time.sleep(2)
        title_field = driver.find_element_by_id("KeywordSearch")
        city_field = driver.find_element_by_id("LocationSearch")
        title_field.send_keys(title)
        title_field.send_keys(Keys.TAB)
        time.sleep(1)
        city_field.send_keys(city)
        city_field.send_keys(Keys.RETURN)
        time.sleep(1)
    except TimeoutException:
        print("TimeoutException! city/title field or search button not found on glassdoor.com")
#enddef

def parse_salaries_HTML(salaries, data, city):
    for salary in salaries:
        jobTitle = "-"
        company = "-"
        meanPay = "-"
        jobTitle = salary.find('p',{'class':'m-0'}).text
        company = salary.find('p',{'class':'m-0'}).next_sibling.text
        try:
            meanPay = salary.find('p',{'class':'d-block d-md-none m-0'}).text +\
            " " + salary.find('p',{'class':'d-block d-md-none m-0 css-1kuy7z7'}).text
        except:
            meanPay = 'xxx'
        r = Salary.Salary(jobTitle, company, meanPay, city)
        data.append(r)
    #endfor
    return data
#enddef

def get_data(driver, URL, city, data, refresh, startPage=1):
    print("\nPage " + str(startPage))
    if (refresh):
        driver.get(URL)
        print( "Getting " + URL)
        time.sleep(2)
    try:
        next_btn = driver.find_element_by_class_name("pagination__ArrowStyle__nextArrow ")
        next_link = next_btn.find_element_by_css_selector("a").get_attribute('href')
    except:
        next_btn = False
        next_link = False
    #endif
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SalarySearchResults")))
    HTML = driver.page_source
    soup = BeautifulSoup(HTML, "html.parser")
    try:
        salaries = soup.find_all('div', {'data-test' : 'job-info'})
    except:
        salaries = False
    if (salaries):
        data = parse_salaries_HTML(salaries, data, city)
        print( "Page " + str(startPage) + " scraped.")
        if (next_link):
            get_data(driver, next_link, city, data, True, startPage + 1)
    else:
        print( "No data available for", city)
    #endif
    return data


if __name__ == "__main__":

    username = "gldoor01@maildrop.cc" # your email here
    password = "bugmenot" # your password here
    driver = init_driver()
    time.sleep(3)
    print( "Logging into Glassdoor account ...")
    login(driver, username, password)
    # search(driver, city, title)
    print( "\nStarting data scraping ...")
    time.sleep(10)
    city_list = open("cities.txt").read().splitlines()
    data_out = []
    for city in city_list:
        search(driver, city, 'Mechanical Engineer')
        appendable = get_data(driver, driver.current_url, city, [], False, 1)
        print( "\nExporting data to " + city + ".json")
        if appendable:
            data_out.append(appendable)
            json_export(appendable, city)
    if data_out:
        json_export(data_out, 'allcities')
    driver.quit()
#endif
