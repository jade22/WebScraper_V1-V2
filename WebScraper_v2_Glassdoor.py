#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 16:02:59 2020

@author: JadeZHOU
"""


'''
Note:

V2 adds a automatic login module compared with V1. I used Glassdoor as an example to test the code.
'''



##########################
#  pip install selenium  #
#  pip install bs4       #
##########################


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import csv



################################## AutomaticLogin ##################################

'''
An automatic login module, refer to: https://github.com/ZhaoyiHuangUCSD/gd_interview_webscrap_tutorial/blob/master/scraper_v1.2.py
Need download ChromeDriver first and use selenium with it together.
Selenium is an open-source web-based automation tool. We can initiate a driver and then send the standard Python commands to the browser automatically through it.
'''




username = '' # your Glassdoor Username
password = '' # your Glassdoor Password

#initiate a driver, here needing to download and install ChromeDriver first
def init_driver():
    driver = webdriver.Chrome(executable_path = "./chromedriver") # chromedriver and the python script are in the same directory
    driver.wait = WebDriverWait(driver, 10)
    return driver
#enddef

#log in the account automatically
def login(driver, username, password):
    driver.get('http://www.glassdoor.com/profile/login_input.htm')
    try:
        user_field = driver.wait.until(EC.presence_of_element_located((By.ID, "userEmail")))
        pw_field = driver.find_element_by_id("userPassword")
        user_field.clear()
        user_field.send_keys(username)
        user_field.send_keys(Keys.TAB) # act as ".clear()", locate to the next field of user_field (here is pw_field) and clear its default values
        time.sleep(1)
        pw_field.send_keys(password)
        time.sleep(1)
        pw_field.send_keys(Keys.ENTER) # act as clicking the login button

    except TimeoutException:
        print("TimeoutException! Username/password field or login button not found on glassdoor.com")
#enddef


################################## ScrapData ##################################


#get the URLs describing each job details of the job lists
def parse_html(driver, url, soup = []):

    try:
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
    except:
        return soup
    return soup
#enddef

def retrieve_urls_job_details(driver, url, startpage, endpage, urls_detail = []):

    if startpage > endpage:
        return urls_detail
    #endif
    currentURL = f'{url[:-5]}{startpage}.htm'
    print(f'\nPage {startpage} of {endpage}...')
    print(f'\nGetting {currentURL}')
    soup = parse_html(driver, currentURL)
    if soup:
        infos = soup.find_all('div', class_ = 'jobContainer')
    else:
        print ("\nWaiting ... page still loading or CAPTCHA input required")
        time.sleep(3)
        soup = parse_html(driver, currentURL)
    #endif
    if infos == False:
        error = f'\nFailed to parse {currentURL}'
        return urls_detail, error
    #endif
    for info in infos:
        url_detail = info.a.get('href')
        urls_detail.append(url_detail)
    print(f'\nPage {startpage} scraped. ')
    time.sleep(2)
    if startpage % 10 == 0:
        print('\nTaking a breather for a few seconds...')
        time.sleep(10)
    #endif
    retrieve_urls_job_details(driver, url, startpage + 1, endpage, urls_detail)

    return urls_detail, ''
#enddef

def get_data(driver, url, data = []):


    print(f'\nGetting {url}')
    try:
        soup = parse_html(driver, url)
        time.sleep(5)
    except:
        error = f'Failed to parse {url}'
        return data, error
    try:
        c = soup.find('div', class_ = 'css-16nw49e e11nt52q1')
    except:
        error = f'Failed to parse {url}'
        return data, error
    try:
        company = c.text.strip()[:-4]
        rating = c.text.strip()[-4:-1]
        print('\nGot job company and rating...')
    except:
        rating = None
        company = None
    try:
        title = soup.find('div', class_ = 'css-17x2pwl e11nt52q6').text.strip()
        print('\nGot job title...')
    except:
        title = None
    try:
        location = soup.find('div', class_ = 'css-1v5elnn e11nt52q2').text.strip()
        print('\nGot job location...')
    except:
        location = None
    try:
        salary = soup.find('span', class_ = 'small css-10zcshf e1v3ed7e1').text.strip().split(' ')[0]
        print('\nGot job salary...')
    except:
        salary = None
    try:
        description = soup.find('div', 'desc css-58vpdc ecgq1xb3').text.strip()
        print('\nGot job description...')
    except:
        description = None

    data.append((title, company, rating, location, salary, description, url))
    return data, ''
#enddef



################################## ExportData ##################################

def save_data(data):

    filename = './data/glassdoor.csv'
    with open(filename, 'w', newline = '') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(['title', 'company', 'rating', 'location', 'salary', 'description', 'job_link'])
        for item in data:
            writer.writerow(item)
#enddef

def update_data(data):

    # filename = input('Enter an existing csv file name which you want to update:\n')
    # assert filename[-4:] == '.csv', "Please input a right file name!"
    filename = './data/glassdoor.csv'
    with open(filename, 'a+', newline = '') as csv_f:
        writer = csv.writer(csv_f)
        for item in data:
            writer.writerow(item)
#enddef

################################## MainBody ##################################
if __name__ == '__main__':
    driver = init_driver()
    time.sleep(3)
    print ("\nLogging into Glassdoor account...")
    login(driver, username, password)
    time.sleep(5)
    print ("\nStarting to scrap urls of job details...")
    url = 'https://www.glassdoor.com/Job/us-data-analyst-jobs-SRCH_IL.0,2_IN1_KO3,15_IP2.htm'
    startpage = 1
    endpage = 10
    urls_detail, error = retrieve_urls_job_details(driver, url, startpage, endpage)
    if error:
        print ("\nWaiting ... page still loading or CAPTCHA input required")
        time.sleep(3)
        urls_detail, error = retrieve_urls_job_details(driver, url, startpage, endpage, urls_detail)
    print(f'\nGot {len(urls_detail)} job urls in total.')
    print('\nStarting to scrap job details...')
    for url in urls_detail:
        print(f'\nJob {urls_detail.index(url)+1} of {len(urls_detail)}...')
        if (urls_detail.index(url) + 1) % 10 == 0:
            print('\nTaking a breather for a few seconds...')
            time.sleep(10)
        #endif
        data, error = get_data(driver, url)
        if error:
            print ("\nWaiting ... page still loading or CAPTCHA input required")
            time.sleep(5)
            data, error = get_data(driver, url, data)
        #endif
        print(f'\nJob {urls_detail.index(url)+1} scrapped.')
        time.sleep(2)
    #endfor

    print(f'\nGot the infomation of {len(data)} jobs in total.')
    print('\nExporting data to file: glassdoor.csv...')
    save_data(data)
