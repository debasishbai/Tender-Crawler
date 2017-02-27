from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from tender_log import set_logger
from datetime import datetime
from time import sleep
import logging
import psycopg2
import mppaths
import re
import os


class MpTenders(object):
    set_logger()

    @staticmethod
    def chrome_options():
        options = webdriver.ChromeOptions()
        download_dir = os.path.join(os.getcwd(), "Documents")
        prefs = {"download.default_directory": download_dir}
        options.add_experimental_option("prefs", prefs)
        return options

    def init_chrome(self):
        """
        Initialize chrome, go to homepage and click on tenders link.
        :return: driver
        """
        display = Display(visible=0, size=(1366, 768))
        display.start()
        options = self.chrome_options()
        driver = webdriver.Chrome(executable_path="/home/debasish/chromedriver", chrome_options=options)
        logging.info("Started Chrome.")
        # driver.maximize_window()
        self.enable_autodownload(driver)
        driver.get("https://www.mpeproc.gov.in/ROOTAPP/tender.jsp?Identity=MPSEDC&db=P")
        driver.find_element_by_link_text(mppaths.go_to_tender_page).click()
        return driver

    @staticmethod
    def get_all_dept(driver):
        """
        This function will fetch all the department names.
        :param driver:
        :return: departments
        """
        get_dept = driver.find_elements_by_css_selector(mppaths.all_dept_names)
        return get_dept

    @staticmethod
    def get_html(content):
        html_content = content.get_attribute("innerHTML")
        return html_content

    @staticmethod
    def do_search(driver, dept):
        """
        Search each department name.
        :param driver:
        :param dept:
        :return: total tenders of each department.
        """
        select_dept = driver.find_element_by_css_selector(mppaths.search_bar).click()
        type_dept_name = driver.find_element_by_css_selector(mppaths.type_name).send_keys(dept, Keys.ENTER)
        logging.info("Searching the dept . . .")
        search = driver.find_element_by_css_selector(mppaths.search_button).send_keys(Keys.ENTER)
        logging.info("Search completed!")
        print "Dept Name:", dept
        total_tender_scope = driver.find_element_by_css_selector(mppaths.tender_count)
        total_tender = re.findall(r".+:\s?(\w+)", total_tender_scope.text)
        if total_tender[0] == "0":
            return False
        else:
            return int(total_tender[0])

    @staticmethod
    def lister_objects(driver):
        """
        Fetches all the scope of the current lister page.
        :param driver:
        :return: scope
        """
        scope = driver.find_elements_by_css_selector(mppaths.lister_scope)
        return scope

    def tender_details(self, driver, lister_obj):
        """
        This function does the work of fetching all the details from the tender's detail page.
        :param driver:
        :param lister_obj:
        :return:
        """
        for obj in range(len(lister_obj)):
            self.document_page(driver, lister_obj[obj])
            # print "Before:", driver.window_handles
            main_window = driver.window_handles[0]
            document_window = driver.window_handles[1]
            driver.switch_to.window(document_window)    # Document Page
            details_page = driver.find_element_by_css_selector(mppaths.details_page).send_keys(Keys.ENTER)
            sleep(1)
            # print "After:", driver.window_handles
            driver.switch_to.window(driver.window_handles[2])    # Details Page
            driver.maximize_window()
            logging.info("Reached details page.")
            # Checking whether the details are hidden or not.
            try:
                show_if_hidden = driver.find_element_by_css_selector(mppaths.show_hidden_css)
                show_if_hidden.click()
                logging.info("Details were hidden.")
            except Exception:
                pass
            details = {}
            for extractor in mppaths.details_scope.keys():
                data = driver.find_element_by_css_selector(mppaths.details_scope[extractor])
                details[extractor] = data.text
            print details
            logging.info("Details fetched.")
            # Closing the windows after their usage is completed.
            driver.close()
            driver.switch_to.window(document_window)
            driver.close()
            # Coming to lister page.
            driver.switch_to_window(main_window)
            sleep(1)
            lister_obj[obj].find_element_by_css_selector(mppaths.random_click).click()
            sleep(1)
            # Scroll down to make the objects visible.
            driver.find_element_by_tag_name("body").send_keys(Keys.ARROW_DOWN, Keys.ARROW_DOWN)
            sleep(1)

    @staticmethod
    def document_page(driver, lister_obj):
        """
        This handles the popup dialog and goes to the document page.
        :param driver:
        :param lister_obj:
        :return:
        """
        action = lister_obj.find_element_by_css_selector(mppaths.action).click()
        show_form = driver.find_element_by_css_selector(mppaths.show_form)
        point = ActionChains(driver)
        point.move_to_element(show_form).click().perform()
        driver.switch_to_alert().accept()
        sleep(1)
        driver.switch_to.window(driver.window_handles[1])
        logging.info("Reached document page.")
        try:
            no_of_files = driver.find_elements_by_class_name("tr_odd")
            print "No.of files:-", len(no_of_files)
            for name in no_of_files:
                file_name = name.find_elements_by_css_selector("td")
                valid_document = re.match(r".+\.(docx|pdf|doc)$", file_name[1].text)
                if valid_document:
                    download = file_name[2].find_element_by_partial_link_text("Download").send_keys(Keys.ENTER)
                    logging.info("Documents downloaded.")
        except Exception as e:
            logging.info("No documents found.")
            pass

        return driver.window_handles

    @staticmethod
    def enable_autodownload(driver):
        """
        Turn On the auto-download option from chrome's settings.
        :param driver:
        :return:
        """
        settings = driver.get(mppaths.settings)
        advanced_settings = driver.find_element_by_css_selector(mppaths.enable_autodownload).click()
        finish = driver.find_elements_by_css_selector(mppaths.finish)
        logging.info("Enabled Auto-download.")

    def main(self):
        """
        Parent function that will call the rest of the functions
        """
        driver = self.init_chrome()
        departments = self.get_all_dept(driver)
        dept_names = [self.get_html(name) for name in departments]
        logging.info("Fetched all the department names.")
        print "No.of Departments:", len(dept_names)
        for dept in dept_names:
            search_dept = self.do_search(driver, dept)
            if not search_dept:
                print "Number of Tenders: 0"
                continue
            else:
                print "Number of Tenders:", search_dept
            tenders = search_dept
            flag = False
            page_count = 1
            while tenders:
                if flag:
                    page_count += 1
                    next_page = driver.find_element_by_partial_link_text(str(page_count)).click()
                lister = self.lister_objects(driver)
                logging.info("Fetched the lister page scopes.")
                self.tender_details(driver, lister)
                flag = True
                tenders -= len(lister)
                print "Tenders remaining:", tenders


start = MpTenders()
start.main()

