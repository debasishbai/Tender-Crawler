
paths_dict = {
    'Tender No': "#tenderNumberspan",
    'Work Name': "#descOfWorkspan",
    'Estimated Cost': "#estimatedCostspan",
    'EMD': "#emdspan",
    'Form Fee': "#formFeespan",
    'Start Date': "#recvOfAppFromDatespan",
    'End Date': "#recvOfAppToDatespan"
}

go_to_tender_page = "Live tenders"
page_links = "body > center:nth-child(10) > div > table > tbody > tr > td > table > tbody > tr > td"
scope = "body > table.tblsummary > tbody > tr:nth-of-type(2n)"
click_selector = "td:nth-child(5) > a"
show_hidden_css = "body > div.panel > div.bpanel > div.summary > form > div.right > a"
scroll_down = "window.scrollTo(0, document.body.scrollHeight);"

insert_data = "INSERT INTO mp (tenderno, workname, estimatedcost, emd, formfee, startdate, enddate) VALUES (%s,%s,%s,%s,%s,%s,%s)"