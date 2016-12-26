from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import paths
import psycopg2
from datetime import datetime


def init_chrome():
    """
        This function will go to homepage and click on tenders link
    """
    driver = webdriver.Chrome("/opt/google/chrome/chromedriver")
    driver.maximize_window()
    driver.get("https://www.mpeproc.gov.in/ROOTAPP/tender.jsp?Identity=MPSEDC&db=P")
    driver.find_element_by_link_text(paths.go_to_tender_page).click()
    return driver


def get_lister_objects(page_no, driver):
    """
        This function clicks on the current page link, gives a list of all the tender names.
    """
    driver.execute_script(paths.scroll_down)
    page_no.click()
    scope = driver.find_elements_by_css_selector(paths.scope)
    print "Number of Tenders:", len(scope)
    print
    return scope


def get_tender_details(lister_objects, driver, cur, conn):
    """
        This function iterates through every tender and returns a dict containing tender details.
    """
    for obj in range(len(lister_objects)):
        tender_link = lister_objects[obj].find_element_by_css_selector(paths.click_selector)
        print lister_objects[obj].text
        action = ActionChains(driver)
        action.move_to_element(tender_link).click().perform()
        driver.switch_to.window(driver.window_handles[1])
        # Checking whether the details are hidden or not.
        try:
            show_if_hidden = driver.find_element_by_css_selector(paths.show_hidden_css)
            show_if_hidden.click()
        except Exception:
            pass
        store_detail = dict()
        for extractor_name in paths.paths_dict.keys():
            try:
                css_extractor = paths.paths_dict[extractor_name]
                data = driver.find_elements_by_css_selector(css_extractor)
                store_detail[extractor_name] = data[0].text
            except Exception:
                store_detail[extractor_name] = 'Not Found'
        print store_detail
        store_to_database(store_detail, cur, conn)
        driver.switch_to.window(driver.window_handles[0])
        print
        # This is to scroll down after the details of the top five tenders are fetched.
        if obj >= 5:
            driver.execute_script(paths.scroll_down)


def store_to_database(get_data, cur, conn):

    date1 = datetime.strptime(get_data['Start Date'], "%d-%m-%Y %H:%M")
    sdate = datetime.strftime(date1, "%Y-%m-%d %H:%M")
    date2 = datetime.strptime(get_data["End Date"], "%d-%m-%Y %H:%M")
    edate = datetime.strftime(date2, "%Y-%m-%d %H:%M")
    cur.execute(paths.insert_data, (get_data["Tender No"], get_data["Work Name"], get_data["Estimated Cost"], get_data["EMD"], get_data["Form Fee"], sdate, edate))
    conn.commit()


def main():
    """
    Parent function that will call the rest of the functions
    """
    driver = init_chrome()
    conn = psycopg2.connect(host="localhost", user="", password="", dbname="postgres")
    cur = conn.cursor()
    print "Database Opened"
    cur.execute("DELETE FROM mp")
    count = 1
    page_count = 1
    pages = driver.find_elements_by_css_selector(paths.page_links)
    print "No.Of Pages:", len(pages)

    # This loop will continue till 'pages' contain any element.
    while pages:

        # Fetching one page at a time from the list of pages.
        lister_objects = get_lister_objects(pages[0], driver)

        # Getting Data from selected page and storing in the database.
        get_tender_details(lister_objects, driver, cur, conn)

        print
        # 'page_count' will keep track of no.of pages that are clicked before moving to the next frame.
        # Once all the pages of the current frame are visited then it is reset.
        page_count += 1

        if page_count > 11:
            page_count = 2
        # 'count' provides the specific page that is to be clicked.
        # After going through all the pages on the current frame, it is reset to 3.
        # Because the first two buttons are meant to visit previous pages.
            count = 3

        # Make sure that the element is attached to the document
        pages = driver.find_elements_by_css_selector(paths.page_links)

        # Moving to next page
        pages = pages[count:]

        count += 1
        print "Moving to Next Page..."
        print

    print "THE END"
    cur.close()
    conn.close()
    print "Database Closed"


if __name__ == "__main__":
    main()
