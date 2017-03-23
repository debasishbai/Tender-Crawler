go_to_tender_page = "Live Tenders"
search_bar = "#sr_buyer_chzn > a > span"
all_dept_names = "#sr_buyer_chzn > div > ul > li:nth-of-type(n+1)"
search_button = '#frm_sr > div.actionBtn > input[type="button"]:nth-child(1)'
type_name = '#sr_buyer_chzn > div > div > input[type="text"]'
scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
lister_scope = "#tblSummary > tbody > tr:nth-of-type(2n+2)"
tender_count = "#uipage > div.bpanel > div.uisummary > form > div:nth-child(1)"
page_count = "#selMQ6_chzn > div > ul > li"
work_name_scope = "#tblSummary > tbody > tr:nth-of-type(2n+3)"
work_name = "td"
tender_no = "td:nth-child(4)"
action = "td:nth-child(2) > a"
show_form = "#action-links > ul > li:nth-child(1) > a"
details_page = "body > div.panel > div.bpanel.p_false > div.info > table > tbody > tr:nth-child(1) > td:nth-child(4) > a"
show_hidden_css = "body > div.panel > div.bpanel > div.summary > form > div.right > a"
random_click = "td:nth-child(3)"

details_scope = {
    "Name of Work": "#descOfWorkspan",
    "Tender No": "#tenderNumberspan",
    "EMD": "#emdspan",
    "Amount of Contract (PAC)": "#estimatedCostspan",
    "Cost of Document": "#formFeespan",
    "Purchase of Tender Start Date": "#recvOfAppFromDatespan",
    "Purchase of Tender End Date": "#recvOfAppToDatespan",
    "Bid Submission End Date": "#receiptOfTendToDatespan"
}

next_page = "#uipage > div.bpanel > div.uisummary > form > div.paginationLinks > div > a:nth-of-type(n+2)"
settings = "chrome://settings-frame/content"
enable_autodownload =  "#content-settings-page > div.content-area > section:nth-child(13) > div > div:nth-child(1) > label > span > span:nth-child(1)"
finish = "#content-settings-overlay-confirm"
