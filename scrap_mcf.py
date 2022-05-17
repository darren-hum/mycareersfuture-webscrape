
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

#from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
from datetime import date

##########################################################################

service = Service(executable_path=ChromeDriverManager().install())

##########################################################################

##########################################################################
# sets options
def set_chrome_options() -> None:
    
    """
    Sets chrome options for selenium
    Enable headless
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options

##########################################################################
# find total pages to loop
def total_pages(page_zero):
    """
    This function calculates the total number of pages when browsing job postings.
    The returned number is 1 less than the actual number as the web address starts at 0.
    """
    driver = webdriver.Chrome(service=service)
    driver.get(page_zero)
    no_of_jobs_found = driver.find_element(By.XPATH, "//div[@data-cy='search-result-headers']").text
    driver.close()

    no_of_jobs_found = no_of_jobs_found.replace(",", "")

    #there are 20 results per page, starts at 0
    total_job_pages = int(re.search(r'\d+', no_of_jobs_found).group(0))/20
            
    return total_job_pages

##########################################################################
# list of pages to scrape
def links_of_pages(total_pages, keyword = ""):
    k = keyword.replace(" ", "%20").lower() + '&'
    links = [f'https://www.mycareersfuture.gov.sg/search?search={k}sortBy=new_posting_date&page={i}' for i in range(total_pages)]
    print('returning', links)
    return links

browse_pages = 'https://www.mycareersfuture.gov.sg/search?sortBy=new_posting_date&page=0'
job_func = 'https://www.mycareersfuture.gov.sg/job/education-training?sortBy=relevancy&page=0'
full_time = 'https://www.mycareersfuture.gov.sg/search?employmentType=Full%20Time&sortBy=relevancy&page=0'
min_salary = 'https://www.mycareersfuture.gov.sg/search?salary=2000&sortBy=relevancy&page=0' # $2000 example
keyword = 'https://www.mycareersfuture.gov.sg/search?search=data%20engineer&sortBy=relevancy&page=0' #data engineer example
keyword_company = 'https://www.mycareersfuture.gov.sg/search?search=data%20engineer&postingCompany=Direct&sortBy=relevancy&page=0' #data engineer / direct company post

##########################################################################

def posting_links(pages_links):
    """
    Input a list of browse pages links.
    Gets individual job posting links on the page.
    """
    postinglinks = []

    for link in pages_links:
        driver = webdriver.Chrome(service=service)
        driver.get(link)
        time.sleep(2)
        for i in range(3): #testing with 3 - should be 20
            try:
                url = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="job-card-{i}"]/div/a'))).get_attribute('href')
                postinglinks.append(url)
            except:
                #print('error')
                continue

        driver.quit()
    
    return postinglinks

##########################################################################

def scrape_pages(pages_links):
    """
    Function loops through list of url. For each url, it scrapes data of the 20 job postings on the page.
    Returns a list of dictionaries containing the data of the job postings extracted from the browse page
    """
    xpaths = {
    'company' : '//*[@data-cy="company-hire-info__company"]',
    'job_title' : '//*[@data-cy="job-card__job-title"]',
    'location' : '//*[@data-cy="job-card__location"]',
    'employment_type' : '//*[@data-cy="job-card__employment-type"]',
    'seniority' : '//*[@data-cy="job-card__seniority"]',
    'category' : '//*[@data-cy="job-card__category"]',
    'salaryrange_min' : '/div/a/div[2]/div/span[2]/div/span[1]',
    'salaryrange_max' : '/div/a/div[2]/div/span[2]/div/span[2]',
    'date_info' : '//*[@data-cy="job-card-date-info"]',
    'applications' : '//*[@data-cy="job-card__num-of-applications"]'
            }
    df_listdict = []
    for url in pages_links:

        driver = webdriver.Chrome(service=service)
        driver.get(url)

        for i in range(20):
            card = f'//*[@id="job-card-{i}"]'
            dict = {}
            for var in xpaths:
                path = card + xpaths[var]
                try:
                    logging.info('trying path %s', path)
                    result = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH, path))).text
                except:
                    logging.info('   >> element not found, assigning empty string')
                    result = ""

                dict[var] = result
            df_listdict.append(dict)
            driver.quit()
    return df_listdict

##########################################################################

def scrape_posting(posting_links):
    """
    Function takes a list of postings of the job post itself and scrapes it.
    Returns a list of dictionaries.
    """
    xpaths = {
        'company' : '//*[@id="job-details"]//*[@data-cy="company-hire-info__company"]',
        'job_title' : '//*[@id="job-details"]//*[@data-cy="job-card__job-title"]',
        'address' : '//p[@id="address"]',
        'employment_type' : '//p[@id="employment_type"]',
        'seniority' : '//p[@id="seniority"]',
        'min_exp' : '//p[@id="min_experience"]',
        'category' : '//p[@id="job-categories"]',
        'salaryrange_min' : '//*[@id="job-details"]/div[1]/div[3]/div/div/section[2]/div/span[2]/div/span[1]',
        'salaryrange_max' : '//*[@id="job-details"]/div[1]/div[3]/div/div/section[2]/div/span[2]/div/span[2]',
        'applications' : '//*[@id="num_of_applications"]',
        'post_date' : '//*[@id="last_posted_date"]',
        'post_expiry' : '//*[@id="expiry_date"]',
        'jd' : '//*[@id="job-details"]/div[1]/div[4]/div[2]'
    }
    
    df_listdict = []
    for url in posting_links:

        driver = webdriver.Chrome(service=service)
        driver.get(url)
        
        dict = {}
        for var in xpaths:
            path = xpaths[var]
            try:
                #logging.info('trying path %s', path)
                result = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH, path))).text
            except:
                #logging.info('   >> element not found, assigning empty string')
                result = ""

            dict[var] = result
        df_listdict.append(dict)
        driver.quit()

    df = pd.DataFrame(df_listdict)
    return df

##########################################################################

def lambda_handler(event, context):
    total_pgs = 1 #total_pages('https://www.mycareersfuture.gov.sg/search?sortBy=new_posting_date&page=0')
    page_links = links_of_pages(total_pgs)
    post_links = posting_links(page_links)
    df = scrape_posting(post_links)
    df.to_csv('mcf_data.csv')