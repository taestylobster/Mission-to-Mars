# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemi_data":mars_hemis(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemis(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.item', wait_time=1)

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # 2. Create a list to hold the images and titles.
    count = 0
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    hemi_box = img_soup.find('div', class_='collapsible results')
    cerberus_title = hemi_box.find_all('h3')[0].get_text()
    schiaparelli_title = hemi_box.find_all('h3')[1].get_text()
    syrtis_title = hemi_box.find_all('h3')[2].get_text()
    valles_title = hemi_box.find_all('h3')[3].get_text()
    titles = [cerberus_title, schiaparelli_title, syrtis_title, valles_title]

    for item in titles:
        # Find and click the thumbnail
        link1_found = browser.links.find_by_partial_text(titles[count])
        link1_found.click()
        #link2_found = browser.find_by_xpath('//*[@id="wide-image"]/div/ul/li[1]/a')
        #link2_found.click()
        # Parse the resulting html with soup
        html = browser.html
        img_soup = soup(html, 'html.parser')
        # find the relative image url
        hemi = img_soup.find('img', class_='wide-image').get('src')
        hemisphere['img_url'].append(f'{url}/{hemi}')
        hemisphere['title'].append(titles[count])
        hemisphere_image_urls.append({'img_url':f'{url}/{hemi}','title':titles[count]})
        browser.back()
        count = count + 1
    
    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls   

def mars_scrape(html_text):
    # parse html text
    hemi_soup = soup(html_text, "html.parser")
    # adding try/except for error handling
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")
    except AttributeError:
        # Image error will return None, for better front-end handling
        title_elem = None
        sample_elem = None
    hemispheres = {
        "title": title_elem,
        "img_url": sample_elem
    }
    return 

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
