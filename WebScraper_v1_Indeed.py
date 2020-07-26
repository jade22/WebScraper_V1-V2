#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 20:38:23 2020

@author: JadeZHOU
"""

# install two packages of python for retrieving website data (type belowing code in terminal)

##########################
#  pip install requests  #
#  pip install bs4       #
##########################



import requests
from bs4 import BeautifulSoup
import time
import traceback
import csv


####################################################################

def retrieve_page(url):
    '''
    Retrieve the info of a web page and parse them into a structual html text
    @param url: a given url which navigates to the page to be retrieved
    @return a BeautifulSoup object
    '''
    
    
### change the header informationa and simulate a browser to send a request to the given website (refer to: https://blog.csdn.net/weixin_42515907/article/details/88083440?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-14.compare&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-14.compare):
    headers = {'User-Agent': 'Mozilla/5.0'} 
   
    try:
        response = requests.get(url)
#         response = requests.get(url, headers = headers) # use it when the given website does not allow python codes to extract info
        response.raise_for_status() # return 200 meaning it is requested properly 
#         assert response.encoding == 'UTF-8', 'response.encoding is not UTF-8' # check if get the proper encoding
    except:
        try:
            response = requests.get(url, headers = headers) 
            response.raise_for_status()
        except:
            print('Get wrong when requesting an url')
            traceback.print_exc()
    
    page = BeautifulSoup(response.text, 'html.parser')
    # print(page)
    
    return page


####################################################################
    
def get_data(page, data):
    '''
    Retrieve all wanted urls on a web page first and then get the wanted info on all pages given by each retrieved url
    @param page: a given web page (parsed)
    @return a list of tuple
    '''


### get the main body of the given page (i.e., the job lists of Indeed):

    try:
        tags = page.find_all('div', class_ = 'jobsearch-SerpJobCard unifiedRow row result')
    except:
        traceback.print_exc()

        
### get info of each job on one page:

    for tag in tags:
        time.sleep(2) # wait for 2 seconds in order not to be treated as maliciously obtainning info
        print(f'\nRetrieving the info of job {tags.index(tag)}...')
        try:
            job_link = 'https://www.indeed.com' + tag.find('h2', attrs = {'class': 'title'}).find('a').get('href')
            details = retrieve_page(job_link)
            if job_link:
                print('Got job link...')
            try:
                description = details.find('div', class_ = 'jobsearch-jobDescriptionText').text.strip()
                if description:
                    print('Got job description...')
            except:
                description = None            
        except:
            job_link = None
            description = None
        try:
            title = tag.find('h2', attrs = {'class': 'title'}).find('a').get('title')
            if title:
                print('Got job title...')
        except:
            title = None
        try:
            company = tag.find('span', attrs = {'class': 'company'}).text.strip()
            if company:
                print('Got job company...')
        except:
            company = None
        try:
            location = tag.find('span', class_ = 'location accessible-contrast-color-location').text.strip()
            if location:
                print('Got job location...')
        except:
            location = None
        data.append((title, company, location, description, job_link))
    
        
### get the url of next page:

    # try:
    #     next_page = 'https://www.indeed.com' + page.find('ul', class_ = 'pagination-list').find('a', attrs = {'aria-label': "Next"}).get('href')
    # except:
    #     traceback.print_exc()
    #     next_page = None
        
        
    # return data, next_page  

    return data

################################## ExportData ##################################


def save_data(data):
    
    filename = input('Enter a csv file name:\n')
    assert filename[-4:] == '.csv', "Please input a right file name!"
    with open(filename, 'w', newline = '') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(['title', 'company', 'location', 'description', 'job_link'])
        for item in data:
            writer.writerow(item)

def update_data(data):
    
    # filename = input('Enter an existing csv file name which you want to update:\n')
    # assert filename[-4:] == '.csv', "Please input a right file name!"
    filename = 'indeed.csv'
    with open(filename, 'a+', newline = '') as csv_f:
        writer = csv.writer(csv_f)
        for item in data:
            writer.writerow(item)




################################## MainBody ##################################

# url_indeed = input('Enter a url:\n')
# data = []
# while url_indeed:
#     page = retrieve_page(url_indeed)
#     data, url_indeed = get_data(page, data)
#     print('Go to next page!\n')
#     if len(data) > 10000:
#         break

if __name__ == '__main__':   
    data = []
    print ("\nStarting data scraping ...")
    for p in range(0,1010,10):
        print(f'\nStarting page {int(p/10)+1}...')
        url_indeed = f'https://www.indeed.com/jobs?q=business+analyst&l=us&start={p}'
        page = retrieve_page(url_indeed)
        data = get_data(page, data)    
        if len(data) > 10000:
            print('Data is enough (>10000).')
            break
            
    print ("\nEnding data scraping ...")
    print(f'Got {len(data)} records in total.')
    print ("\nExporting data to indeed.csv")
    update_data(data)