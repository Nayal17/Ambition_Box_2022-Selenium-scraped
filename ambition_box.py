import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime
import time
from tqdm import tqdm


def get_driver():
    chrome_options = Options()
    ## The sandbox environment provides a testing and staging platform without allowing the code being tested to
    ## make changes to existing code and databases
    chrome_options.add_argument('--no-sandbox')
    ## A headless browser is a web browser without a graphical user interface. Headless browsers provide automated 
    ## control of a web page in an environment similar to popular web browsers, but they are executed via a 
    ## command-line interface or using network communication.
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

    return driver


def company(driver):
    names = []
    ratings = []
    reviews = []
    domains = []
    locations = []
    years = []
    employees = []
    for i in range(len(driver.find_elements(By.CLASS_NAME,'company-content-wrapper'))):
        div = driver.find_elements(By.CLASS_NAME,'company-content-wrapper')[i]
        
        ### name
        try:
            name = div.find_elements(By.CLASS_NAME,'company-name')[0].get_attribute('textContent').strip()
            names.append(name)
        except:
            names.append('NA')
        
        ### rating
        try:
            rating = div.find_elements(By.CLASS_NAME,'rating')[0].get_attribute('textContent').strip()
            ratings.append(rating)
        except:
            ratings.append('NA')
        
        ## review
        try:
            review = div.find_elements(By.CLASS_NAME,'review-count')[0].get_attribute('textContent').strip()[1:-1]
            if review.split(' ')[0][-1]=='k':
                review = int(float(review.split(' ')[0][:-1])*1000)
            else:
                review = int(review.split(' ')[0])

            reviews.append(review)
        except:
            reviews.append('NA')

        ### domain, location, employee_count, years old
        a = 0
        b = 0
        c = 0
        d = 0 
        for k in range(len(div.find_elements(By.CLASS_NAME,"infoEntity"))):
            p = div.find_elements(By.CLASS_NAME,"infoEntity")[k]  
            try:
                i = p.find_elements(By.CLASS_NAME,'icon-domain')[0].get_attribute('textContent').strip()
                dom = p.get_attribute('textContent').strip()
                domains.append(dom)
                a = a + 1
            
            except:
                try:
                    i = p.find_elements(By.CLASS_NAME,'icon-pin-drop')[0].get_attribute('textContent').strip()
                    loc = p.get_attribute('textContent').strip()
                    locations.append(loc)
                    b = b + 1


                except:
                    try:
                        i = p.find_elements(By.CLASS_NAME,'icon-supervisor-account')[0].get_attribute('textContent').strip()
                        employee = p.get_attribute('textContent').strip()
                        employees.append(employee)
                        c = c + 1

                    except:
                        try:
                            i = p.find_elements(By.CLASS_NAME,'icon-access-time')[0].get_attribute('textContent').strip()
                            year = p.get_attribute('textContent').strip().split(' ')[0]
                            years.append(year)
                            d = d + 1

                        except:
                            print('no_info')
        
        val = 'unknown'
        if a==0:
            domains.append(val)
        
        if b==0:
            locations.append(val)

        if c==0:
            employees.append(val)

        if d==0:
            years.append(val)

    return {"names": names,
            "ratings": ratings,
            "reviews": reviews,
            "domains": domains,
            "locations": locations,
            "years": years,
            "employees": employees,
            }



if __name__== '__main__':
    driver = get_driver()
    cp_name = []
    rats_ = []
    revs_ = []
    doms_ = []
    locs_ = []
    emps_ = []
    yrs_ = []
    desc_ = []

    for u in tqdm(range(1,334)):
        url = f'https://www.ambitionbox.com/list-of-companies?campaign=desktop_nav&page={u}'
        driver.get(url)
        comp = company(driver) 

        doms_.extend(comp['domains'])
        locs_.extend(comp['locations'])
        emps_.extend(comp['employees'])
        yrs_.extend(comp['years'])
        cp_name.extend(comp['names'])
        rats_.extend(comp['ratings'])
        revs_.extend(comp['reviews'])
        print(yrs_)

        
    df = pd.DataFrame({"Company":cp_name,
                        "Rating(5)":rats_,
                        "Review_count":revs_,
                        "Domain":doms_,
                        "Location":locs_,
                        "No. of Employees":emps_,
                        "Years old":yrs_})

    df.to_csv('Ambition_Box.csv')

