import pandas as pd
from selenium import webdriver
from selenium import common as common
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


class LocatorItem:
    def __init__(self,locator: str):
        self.locator = locator
        if locator[0] == "#":
            self.by = By.CSS_SELECTOR
            self.find = "find_element_by_css_selector"
        else:
            self.by = By.XPATH
            self.find = "find_element_by_xpath"
    def find_self(self, browser):
        return getattr(browser,self.find)(self.locator)


def read_paginated_table(
        link: str, 
        table_chooser:str=None, 
        next_button_chooser:str=None, 
        next_button_chooser_2:str=None, 
        show_more_option:str=None, 
        delay:float=0) -> pd.DataFrame:
    """
    Read HTML tables that show a limited number of rows at a time.
    :param link: The link to the page where the table is located.
    :param table_chooser: The xpath or css selector to the table.
    :param next_button_chooser: The xpath or CSS selector for the next button
    :param next_button_chooser2: The xpath or CSS selector the next button on the second page of the table
    :param show_more_option: The xpath or css selector for a "show more rows" button for the table.
    :param delay: Delay between clicking the next buttons.
    :return A dataframe consisting of all of the data from the HTML table.
    """

    try:
        browser = webdriver.Chrome()
        browser.get(link)
    except common.exceptions.WebDriverException as e:
        print(f"Either invalid link or webdriver not configured correctly.\n{e}")
        return pd.DataFrame()
    
    # this mode allows the following: launch a browser, figure out the selectors, and then continue with the scraping process.
    # this is useful for databases that have dynamic paths upon initialization.
    if not (table_chooser or next_button_chooser):
        table_chooser = input("Table chooser xpath/css: ")
        next_button_chooser = input("Next button chooser xpath/css: ")
        next_button_chooser_2 = input("Page 2 Next button chooser xpath/css, or press enter to continue: ")
        if next_button_chooser_2:
            print("Don't forget to go back to page 1 before providing (or not providing) next optional argument!")
        show_more_option = input("Show more chooser xpath/css, or press enter to continue: ")

    table_locator = LocatorItem(table_chooser)
    next_locator = LocatorItem(next_button_chooser)

    try:
        print("Searching the page for specified webelements...")
        if show_more_option:
            try:
                show_more_by = By.CSS_SELECTOR if show_more_option[0] == "#" else By.XPATH
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((show_more_by, show_more_option))).click()  # Waits a maximum of
                # 10 seconds for the show more rows selector to show up.
                print("Show more button selected.")
            except TimeoutException:
                print("Show more selector not found.")

        # The last two lines check if the crucial elements (Next button and the table) are found on the page.
        next_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((next_locator.by, next_locator.locator)))
        table_locator.find_self(browser).get_attribute('outerHTML')


    except common.exceptions.NoSuchElementException as e:
        print(f"I think I was unable to find either the table, next button, or the show more option if it was provided .\n{e}")
    except Exception as e:
        print(f"Something went wrong that I wasn't expecting.  Here you go:\n{e}")

    page_number = 1  # used for keeping track of how many table pages have been read.
    df_list = [pd.DataFrame()]  # will contain all of the tables for each page.
    consecutive_errors = 0  # will keep track of how many errors are made without a successful table download.
    # If enough errors are made consecutively, the program returns everything up to the failure point and shuts off.
    # will be used to detect if the page has successfully changed.
    done = False  # monitor if the scraping job is done.
    print("Scraping page 1...")
    max_errors = 40 if delay == 0 else min(1 / delay + 5, 40)
    while max_errors and not done:
        try:
            while True:
                if consecutive_errors >= max_errors:
                    raise common.exceptions.NoSuchElementException  # stop scraping if there have been too many
                # consecutive errors.

                html = table_locator.find_self(browser).get_attribute('outerHTML')  # get the outer table html
                temp_df = pd.read_html(html)[0]  # create a dataframe from the html table
                if not temp_df.equals(df_list[-1]):  # if this table is new...
                    consecutive_errors = 0  # the operation was a success, so reset the consecutive errors counter.
                    df_list.append(temp_df)  # add the new df the list of all dataframes.
                    if page_number == 2 and next_button_chooser_2:
                        next_locator = LocatorItem(next_button_chooser_2)
                    next_button = next_locator.find_self(browser)  # find the next button
                    browser.execute_script("arguments[0].click();", next_button)  # click the button
                    page_number += 1  # we are now on the next page
                    if (page_number % 10) == 0:
                        print("Scraping Page: {}...".format(page_number))

                else:
                    consecutive_errors += 1
                time.sleep(delay)
        except common.exceptions.NoSuchElementException:
            print("Finished after {} clicks, or the next button couldn't be found.".format(page_number))
            done = True
        except ValueError:
            print("No table found")
            done = True
        except Exception as e:
            print(e)
            consecutive_errors += 1
    if df_list:
        return pd.concat(df_list, ignore_index=True)  # concatenate all of the dataframes into one big dataframe.
    else:
        return pd.DataFrame()  # return an empty dataframe if the operation was a failure.


