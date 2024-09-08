from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
import time
from datetime import datetime
import pandas as pd



#region DF controls and variables
ReviewDF = None
DFStoragePath = "file_path"
#endregion

#scraping section
def GetDataframe():
    #region initialize variable and webdriver
    
    recommendations = []
    review_text = []
    dates = []
    play_time = []

    options = Options()
    options.headless = True
    site = "website"

    # initialize base page
    driver = webdriver.Chrome(options=options)
    driver.get(site)
    #endregion

    #region open main store page from age verification page
    year_select_button_id = 'id'
    age_confirm_button_id = 'id'


    # open age dropdown
    age_button = driver.find_element(By.ID, year_select_button_id)
    age_button.click()

    # click age on dropdown
    age_options = Select(age_button)    
    age_options.select_by_value('age')

    # go to main page
    driver.find_element(By.ID, age_confirm_button_id).click()
    time.sleep(3)
    #endregion

    #region click on summary review button, then open up url with all reviews
    review_filter_button_class = 'button'
    review_filter_buttons = driver.find_elements(By.CLASS_NAME, review_filter_button_class)

    for button in review_filter_buttons:
        if button.text == "option":
            # hover over the correct dropdown
            ActionChains(driver).move_to_element(button).perform()
            
            # click on the recent tab for review order
            review_summary_id = 'is'            
            button.find_element(By.ID, review_summary_id).click()
            break
    time.sleep(1)
    driver.find_element(By.CLASS_NAME, 'button').click()
    time.sleep(1)

    #endregion

    #region click on the recent tab on the third webpage
    filters_bar_class = 'apphub_SectionFilter'

    filters_bar = driver.find_element(By.CLASS_NAME, filters_bar_class)
    
    sorting_dropdown = filters_bar.find_element(By.ID, 'filterselect')
    sorting_dropdown.click()

    popup_class = 'popup_block'
    popup_options = driver.find_element(By.CLASS_NAME, popup_class)

    recent_option_id = 'filterselect_option_7'
    popup_options.find_element(By.ID, recent_option_id).click()
    time.sleep(1)
    # above works

    #endregion



    # region this is going to scroll and scrape

    def scrape(review_page):
        review_card_css = 'css' # contains all information for a single review
        # the following are the search terms once inside the reviews page
        review_header_class = 'class' # this is where playtime and recommendation is stored
        recommendation_class = 'class' # insider review_header_class
        hours_played_class = 'class' # insider review_header_class

        default_year = datetime.now().year


        #below is a test to see how the info gets organized by default
        full_reviews = review_page.find_elements(By.CSS_SELECTOR, review_card_css)

        for review in full_reviews:
            review_header = review.find_element(By.CLASS_NAME, review_header_class)
            # region check if recommended, bool
            recommend = review_header.find_element(By.CLASS_NAME, recommendation_class).text[0]
            if recommend == 'letter1':
                recommend = False
            elif recommend == 'letter2':
                recommend = True
            else:
                continue
            #endregion

            #region get playtime for review
            try:
                hours_played = review_header.find_element(By.CLASS_NAME, hours_played_class).text
                hours_played = float(hours_played.split()[0])
            except:
                continue
            #endregion

            review_text_class = 'class'
            site_review_text = review.find_element(By.CLASS_NAME, review_text_class) # from this I need to separate the first line, if no year it is this year
            full_text = site_review_text.text
            review_sections = full_text.split('\n')


            date_list = review_sections[0].split()[1:]
            full_date = f"{date_list[0]} {date_list[1]} {default_year}"
            date_format = "%B %d %Y"
            date_object = datetime.strptime(full_date, date_format)

            current_review = ' '.join(review_sections[1:])

            recommendations.append(recommend)
            play_time.append(hours_played)
            dates.append(date_object)
            review_text.append(current_review)



    scroll_amount = 1500  # Pixels to scroll each time
    all_reviews_id = 'id' # id home for all revies
    all_reviews_container = driver.find_element(By.ID, all_reviews_id) # get the home of all reviews
    reviews_contains_contents = all_reviews_container.find_elements(By.XPATH, "*") # gets all immediate children of the review class
    previous_driver_position = driver.execute_script("return window.scrollY;") # used to check if driver has moved since last time
    finished = False

    while True:
        # wait for screen to update
        time.sleep(1)

        # scroll      
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        current_driver_position = driver.execute_script("return window.scrollY;")
        
        if len(reviews_contains_contents) > 2: # copy and delete until only 1 page and loading section left
            while len(reviews_contains_contents) > 2:         
                # copy first 2 divs
                scrape(reviews_contains_contents[0])

                # delete first 2 divs
                remove_from_site = reviews_contains_contents[:2]

                for element in remove_from_site:
                    driver.execute_script("arguments[0].remove();", element)

                reviews_contains_contents = all_reviews_container.find_elements(By.XPATH, "*")
            finished = False
        elif current_driver_position == previous_driver_position: # at end 
            # was at the end for two loops, at the true end of the page
            if finished:
                break   

            # attempt to load more reviews by leaving and returning to the bottom of the page         
            driver.execute_script(f"window.scrollBy(0, {-scroll_amount});")
            time.sleep(1)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            finished = True

        
        # get last high of webpage
        previous_driver_position = driver.execute_script("return window.scrollY;")


        # check number of pages loaded
        reviews_contains_contents = all_reviews_container.find_elements(By.XPATH, "*")

    # same as above loop but just cleans out the excess after stopping, probably should turn both in a method to save line space
    while len(reviews_contains_contents) > 0:         
        # copy first 2 divs
        scrape(reviews_contains_contents[0])

        # delete first 2 divs
        remove_from_site = reviews_contains_contents[:2]

        for element in remove_from_site:
            driver.execute_script("arguments[0].remove();", element)

        reviews_contains_contents = all_reviews_container.find_elements(By.XPATH, "*")
    
    #endregion

    
    driver.quit()
    return recommendations, review_text, dates, play_time

recommendation, review, date, play_time = GetDataframe()

ReviewDF = pd.DataFrame(
    {
        'recommendation': recommendation,
        'review_text': review,
        'review_date': date,
        'play_time': play_time,
    }
)
ReviewDF.to_pickle(DFStoragePath)