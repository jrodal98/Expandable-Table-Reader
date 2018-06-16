import pandas as pd
from selenium import webdriver
from selenium import common as common
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def read_extended_table(link, table_xpath, next_button_selector, delay=.1, show_more_selector=None):
    """
    Read HTML tables that show a limited number of rows at a time.
    :type link: str
    :type table_xpath: str
    :type next_button_selector: str
    :type delay: float
    :type show_more_selector: str
    :param show_more_selector: A css selector for a "show more rows" button for the table.
    :param delay: Delay between clicking the next buttons.
    :param link: The link to the page where the table is located.
    :param table_xpath: The xpath to the table.
    :param next_button_selector: The CSS selector for the next button
    :return A dataframe consisting of all of the data from the HTML table.
    """
    browser = webdriver.Chrome()  # Opens our driver that will be reading the table.  This can obviously be changed with
    # a driver of your choice.
    try:
        browser.get(link)  # Open the page. This command automatically waits for the page to fully load.
        print("Waiting to verify that the page is fully loaded...")
        if show_more_selector is not None:
            try:
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, show_more_selector))).click()  # Waits a maximum of
                # 10 seconds for the show more rows selector to show up.
                print("Show more button selected.")
            except TimeoutException:
                print("Show more selector not found.")

        next_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, next_button_selector)))
        browser.find_element_by_xpath(table_xpath).get_attribute('outerHTML')

        # The last two lines checked if the crucial elements (Next button and the table) are found on the page.

    except common.exceptions.NoSuchElementException:
        print("Unable to locate the xpath or next button.")
    except common.exceptions.WebDriverException:
        print("Cannot navigate to invalid URL.")
    except Exception:
        print("Something went wrong.  Try again later.")

    page_number = 1  # used for keeping track of how many table pages have been read.
    df_list = []  # will contain all of the tables for each page.
    consecutive_errors = 0  # will keep track of how many errors are made without a successful table download.
    # If enough errors are made consecutively, the program returns everything up to the failure point and shuts off.
    old_html = ""  # will be used to track whether or not the html table scraped from the page has changed.  This
    # will be used to detect if the page has successfully changed.
    done = False  # monitor if the scraping job is done.
    print("Scraping page 1...")
    while consecutive_errors < (1 / delay + 5) and not done:
        try:
            while True:
                if consecutive_errors >= (1 / delay + 5):
                    raise common.exceptions.NoSuchElementException  # stop scraping if there have been too many
                # consecutive errors.

                html = browser.find_element_by_xpath(table_xpath).get_attribute('outerHTML')  # get the outer table html
                temp_df = pd.read_html(html)[0]  # create a dataframe from the html table
                if old_html != html:  # if this table is new...
                    consecutive_errors = 0  # the operation was a success, so reset the consecutive errors counter.
                    old_html = html  # swap the html tracker
                    df_list.append(temp_df)  # add the new df the list of all dataframes.
                    next_button = browser.find_element_by_css_selector(next_button_selector)  # find the next button
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
            # print("Something unexpected went wrong on click {}.".format(page_number))
            consecutive_errors += 1
    if len(df_list) > 0:
        return pd.concat(df_list, ignore_index=True)  # concatenate all of the dataframes into one big dataframe.
    else:
        return pd.DataFrame()  # return an empty dataframe if the operation was a failure.


def make_excel_file(name: str, df: pd.DataFrame):
    """
    Write a dataframe to an excel file in one line.
    :param name:
    :param df:
    :return:
    """
    writer = pd.ExcelWriter(name.strip(".xlsx") + ".xlsx")
    df.to_excel(writer, "Sheet1")
    writer.save()
