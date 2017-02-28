from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from tender_log import set_logger
from selenium import webdriver
from datetime import datetime
from time import sleep
import logging
import mppaths
import database
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
        display = Display(visible=1, size=(1366, 768))  # Make visible to 0 to run chrome headless.
        display.start()
        options = self.chrome_options()
        driver = webdriver.Chrome(executable_path="/home/debasish/chromedriver", chrome_options=options)
        logging.info("Started Chrome.")
        driver.maximize_window()
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
    def scroll_down(driver, lister):
        lister.find_element_by_css_selector(mppaths.random_click).click()
        sleep(1)
        # Scroll down to make the objects visible.
        driver.find_element_by_tag_name("body").send_keys(Keys.ARROW_DOWN, Keys.ARROW_DOWN)
        sleep(1)

    @staticmethod
    def strip_time(date_time):
        stripped_date = {}
        sdate = datetime.strptime(date_time["Purchase of Tender Start Date"], "%d-%m-%Y %H:%M")
        stripped_date["Purchase of Tender Start Date"] = datetime.strftime(sdate, "%Y-%m-%d %H:%M")
        edate = datetime.strptime(date_time["Bid Submission End Date"], "%d-%m-%Y %H:%M")
        stripped_date["Bid Submission End Date"] = datetime.strftime(edate, "%Y-%m-%d %H:%M")
        return stripped_date

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
        logging.info("Searching Dept . . .")
        search = driver.find_element_by_css_selector(mppaths.search_button).send_keys(Keys.ENTER)
        logging.info("Search Completed!")
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
        scopes = {}
        scope = driver.find_elements_by_css_selector(mppaths.lister_scope)
        work_name_scope = driver.find_elements_by_css_selector(mppaths.work_name_scope)
        scopes["lister_scope"] = scope
        scopes["work_name"] = work_name_scope
        return scopes

    def tender_details(self, driver, lister_obj):
        """
        This function does the work of fetching all the details from the tender's detail page.
        :param driver:
        :param lister_obj:
        :return:
        """
        for obj in range(len(lister_obj["lister_scope"])):
            duplicate_tender = self.check_for_duplicates(lister_obj["lister_scope"][obj], lister_obj["work_name"][obj])
            if duplicate_tender:
                logging.warning("Duplicate Tender")
                logging.info("Skipping . . .")
                self.scroll_down(driver, lister_obj["lister_scope"][obj])
                continue
            else:
                logging.info("New Tender")
                logging.info("Processing . . .")
            documents = self.document_page(driver, lister_obj["lister_scope"][obj])
            main_window = driver.window_handles[0]
            document_window = driver.window_handles[1]
            driver.switch_to.window(document_window)    # Document Page
            details_page = driver.find_element_by_css_selector(mppaths.details_page).send_keys(Keys.ENTER)
            sleep(1)
            driver.switch_to.window(driver.window_handles[2])    # Details Page
            driver.maximize_window()
            logging.info("Reached details page.")
            # Checking whether the details are hidden or not.
            try:
                show_if_hidden = driver.find_element_by_css_selector(mppaths.show_hidden_css)
                show_if_hidden.click()
                logging.info("Details were Hidden.")
            except Exception:
                pass
            details = {}
            for extractor in mppaths.details_scope.keys():
                data = driver.find_element_by_css_selector(mppaths.details_scope[extractor])
                details[extractor] = data.text
            print details
            logging.info("Details Fetched.")
            # Store details
            self.store_to_database(documents, details)
            driver.close()
            driver.switch_to.window(document_window)
            driver.close()
            # Coming to lister page.
            driver.switch_to_window(main_window)
            sleep(1)
            # Scroll Down
            self.scroll_down(driver, lister_obj["lister_scope"][obj])

    @staticmethod
    def check_for_duplicates(tender_scope, work_name_scope):
        """
        Reads the database to check whether the tender already exists or not.
        :param tender_scope:
        :param work_name_scope:
        :return: tender count
        """
        initiate_cur = database.store_data()
        tender_no = tender_scope.find_element_by_css_selector(mppaths.tender_no).text
        raw_work_name = work_name_scope.find_element_by_css_selector(mppaths.work_name).text.strip()
        work_name = re.match(r".+\n(.+)$", raw_work_name).groups()[0]
        initiate_cur[1].execute(database.check_in_database, (work_name, tender_no))
        tender_count = initiate_cur[1].fetchone()[0]
        return tender_count

    def store_to_database(self, documents, details):
        """
        This function stores all the tender details into database.
        :param documents:
        :param details:
        :return:
        """
        get_datetime = self.strip_time(details)
        initiate_cur = database.store_data()
        initiate_cur[1].execute(database.insert_into_main_table, (details["Name of Work"], details["Tender No"], details["EMD"], details["Amount of Contract (PAC)"], details["Cost of Document"], get_datetime["Purchase of Tender Start Date"], get_datetime["Bid Submission End Date"]))

        initiate_cur[1].execute(database.fetch_primary_id, (details["Name of Work"], details["Tender No"]))
        primary_id = initiate_cur[1].fetchone()[0]
        for name in documents:
            initiate_cur[1].execute(database.insert_into_doc_table, (primary_id, name))
        initiate_cur[0].commit()
        logging.info("Tender Saved into Database!")

    @staticmethod
    def document_page(driver, lister_obj):
        """
        Download all the documents available.
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
        document_name = []
        try:
            no_of_files = driver.find_elements_by_class_name("tr_odd")
            print "No.of files:", len(no_of_files)
            for name in no_of_files:
                file_name = name.find_elements_by_css_selector("td")
                valid_document = re.match(r".+\.(docx|pdf|doc)$", file_name[1].text)
                if valid_document:
                    document_name.append(file_name[1].text)
                    download = file_name[2].find_element_by_partial_link_text("Download").send_keys(Keys.ENTER)
                    logging.info("Documents downloaded!")
        except Exception as e:
            logging.info("No documents found.")
            return driver.window_handles

        return document_name

    @staticmethod
    def enable_autodownload(driver):
        """
        Turn On the Auto-download option from chrome's settings.
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
            while tenders >= 1:
                if flag:
                    page_count += 1
                    next_page = driver.find_element_by_partial_link_text(str(page_count)).click()
                lister = self.lister_objects(driver)
                logging.info("Fetched the lister page scopes.")
                self.tender_details(driver, lister)
                flag = True
                tenders -= len(lister["lister_scope"])
                print "Tenders remaining:", tenders


start = MpTenders()
start.main()

