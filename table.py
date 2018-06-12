import pandas as pd
from selenium import webdriver
from selenium import common as common
import time


def read_extended_table(link: str, table_xpath: str, next_button_selector: str, delay=.1):
    """
    Read HTML tables that show a limited number of rows at a time.
    :param delay: Delay between clicking the next buttons.
    :param link: The link to the page where the table is located.
    :param table_xpath: The xpath to the table.
    :param next_button_selector: The CSS selector for the next button
    :return: A dataframe consisting of all of the data from the HTML table.
    """
    browser = webdriver.Chrome()
    try:
        browser.get(link)
        print("Waiting to verify that the page is fully loaded...")
        time.sleep(5)
        browser.find_element_by_xpath(table_xpath).get_attribute('outerHTML')
        next_button = browser.find_element_by_css_selector(next_button_selector)
    except common.exceptions.NoSuchElementException:
        print("Unable to locate the xpath or next button.")
    except common.exceptions.WebDriverException:
        print("Cannot navigate to invalid URL.")
    except Exception:
        print("Something went wrong.  Try again later.")

    page_number = 1
    df_list = []
    consecutive_errors = 0
    old_html = ""
    done = False
    print("Scraping page 1...")
    while consecutive_errors < (1 / delay + 5) and not done:
        try:
            while True:
                if consecutive_errors >= (1 / delay + 5):
                    raise common.exceptions.NoSuchElementException

                html = browser.find_element_by_xpath(table_xpath).get_attribute('outerHTML')
                temp_df = pd.read_html(html)[0]
                if old_html != html:
                    consecutive_errors = 0
                    old_html = html
                    df_list.append(temp_df)
                    next_button = browser.find_element_by_css_selector(next_button_selector)
                    browser.execute_script("arguments[0].click();", next_button)
                    page_number += 1
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
        return pd.concat(df_list, ignore_index=True)
    else:
        return pd.DataFrame()



def make_excel_file(name: str, df: pd.DataFrame):
    writer = pd.ExcelWriter(name.strip(".xlsx") + ".xlsx")
    df.to_excel(writer, "Sheet1")
    writer.save()
