# TODO: Fix users with the same name and different email
# TODO: Add check for failure for each user using try, except and add to did_not_finish list
# TODO: Parallel webdriver for Chrome to reduce the cycle time

import pandas
import os
import numpy
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import json

CONFIG_FILE_NAME = os.path.join(os.path.dirname(__file__), 'input_info.json')


def create_new_report(chrome_driver_inner, report_info_inner):

    add_new_report = chrome_driver_inner.find_element_by_id('MainContent_MainActionCreate')
    add_new_report.click()

    next_button = chrome_driver_inner.find_element_by_id('MainContent_AAWiz__Next')
    next_button.click()

    name_text = chrome_driver_inner.find_element_by_id('MainContent_ClientProjectName')
    name_text.clear()
    name_text.send_keys('{} - {} - {}'.format(report_info_inner['new_report_string'],
                                              report_info_inner['start_date'],
                                              report_info_inner['end_date']))

    start_date_text = chrome_driver_inner.find_element_by_id('MainContent_StartDate_input')
    start_date_text.clear()
    start_date_text.send_keys(report_info_inner['start_date'])

    end_date_text = chrome_driver_inner.find_element_by_id('MainContent_EndDate_input')
    end_date_text.clear()
    end_date_text.send_keys(report_info_inner['end_date'])



def execute_expense_report(report_filename=CONFIG_FILE_NAME,
                           report_info=None):

    if report_filename and not report_info:
        with open(report_filename, 'r') as input_file:
            report_info = json.load(input_file)
        report_info['password'] = ''
        report_info['user_name'] = ''
        
    file_name = report_info['reconciliation_report_location']
    excel_file = pandas.ExcelFile(file_name)
    pcard_df = excel_file.parse(excel_file.sheet_names, skiprows=8)

    recon_df = pcard_df['PCard Reconciliation Report']

    names = recon_df['Employee Name'].dropna().unique()

    #did_not_finish_list = process_names(names, report_info)
    did_not_finish_list = []

    number_of_parallel_workers = 4

    with multiprocessing.Pool(processes=number_of_parallel_workers) as pool:

        result_list = [pool.apply_async(process_names, (split_names, report_info))
                       for split_names in numpy.array_split(names,
                                                            number_of_parallel_workers)]

        for result in result_list:
            did_not_finish_list.extend(result.get())

    print('Did not finish: {}'.format(did_not_finish_list))


def process_names(names, report_info):

    chrome_driver = webdriver.Chrome(os.path.join(os.path.dirname(__file__), 'chromedriver.exe'))

    did_not_finish_list = []
    finished_users = []

    logon_website = report_info['logon_website']

    chrome_driver.get(logon_website)

    chrome_driver.find_element_by_id('userNameInput').send_keys(report_info['email_address'])
    chrome_driver.find_element_by_id('passwordInput').send_keys(report_info['password'])
    chrome_driver.find_element_by_id('passwordInput').send_keys(Keys.ENTER)

    chosen_names = names

    for current_id, the_name in enumerate(chosen_names):

        try:
            chrome_driver.implicitly_wait(0)

            print('Processing user {} of {}, {}'.format(current_id+1, len(chosen_names), the_name))

            current_user_dropdown = Select(chrome_driver.find_element_by_id('CurrentUserDropdown'))
            current_user_dropdown.select_by_visible_text(report_info['user_name'])

            configuration_link = chrome_driver.find_element_by_id('topNavToolsConfigurationLink')
            configuration_link.click()

            view_and_edit_users = chrome_driver.find_element_by_id('MainContent_ctl69')
            view_and_edit_users.click()

            last_name = chrome_driver.find_element_by_id('MainContent_LName')
            last_name_str = the_name.split()[1]

            last_name.send_keys(last_name_str)
            last_name.send_keys(Keys.ENTER)

            user_tag = chrome_driver.find_element_by_xpath("//nobr[text() = \"{}\"]".format(the_name))
            edit_user = user_tag.find_elements_by_xpath("../..//img[@src='images/16_edit.png']")
            edit_user[0].click()

            switch_user = chrome_driver.find_element_by_link_text('Switch to this User')
            switch_user.click()

            more_items = chrome_driver.find_element_by_id('MainContent_lblWalletMoreItems')
            more_items.click()

            transaction_list = chrome_driver.find_elements_by_xpath("//*[@class='feed_row-primary']//img[@src='images/16_credit-card.png']")
            for i_val in transaction_list:
                i_val.find_element_by_xpath("../..//input[@type='checkbox']").click()

            try:
                add_content = chrome_driver.find_element_by_id('MainContent_Add')
                add_content.click()
            except:
                did_not_finish_list.append(the_name)
                continue

            #time.sleep(3)

            chrome_driver.implicitly_wait(int(report_info['wait_time']))

            try:
                add_to_existing = chrome_driver.find_element_by_id('MainContent_MainActionAdd')
                add_to_existing.click()
            except NoSuchElementException:
                did_not_finish_list.append(the_name)
                continue

            chrome_driver.implicitly_wait(0)

            if add_to_existing.get_attribute('disabled') == 'true':
                create_new_report(chrome_driver, report_info)
            else:
                next_button = chrome_driver.find_element_by_id('MainContent_AAWiz__Next')
                next_button.click()

                selected_report = Select(chrome_driver.find_element_by_id('MainContent_SelectedExpenseReport'))

                try:
                    selected_report.select_by_visible_text('{} - {} - {}'.format(report_info['report_executive_string'],
                                                                                 report_info['start_date'],
                                                                                 report_info['end_date']))
                except NoSuchElementException:
                    back_button = chrome_driver.find_element_by_id('MainContent_AAWiz__Back')
                    back_button.click()

                    create_new_report(chrome_driver, report_info)


            next_button_2= chrome_driver.find_element_by_id('MainContent_AAWiz__Next')
            next_button_2.click()

            finished_users.append(the_name)

            current_user_dropdown = Select(chrome_driver.find_element_by_id('CurrentUserDropdown'))
            current_user_dropdown.select_by_visible_text(report_info['user_name'])
        except Exception as e:
            print('Caught an exception on user {}: {}'.format(the_name, e))
            did_not_finish_list.append(the_name)

    return did_not_finish_list

if __name__ == '__main__':
    execute_expense_report()