import psycopg2


def store_data():
    database_list = []
    conn = psycopg2.connect(host="localhost", user="", password="", dbname="")
    cur = conn.cursor()
    database_list.append(conn)
    database_list.append(cur)
    return database_list

insert_into_main_table = """

    INSERT INTO mp_tenders \
    (work_name, tender_no, emd, amount_of_contract, cost_of_document, purchase_start_date, bid_submission_end_date)
    VALUES (%s,%s,%s,%s,%s,%s,%s)

    """

insert_into_doc_table = "INSERT INTO documents (document_id, document_name) VALUES (%s,%s)"

fetch_primary_id = "SELECT id FROM mp_tenders WHERE work_name = %s AND tender_no = %s"

check_in_database = "SELECT count(*) FROM mp_tenders WHERE work_name = %s AND tender_no = %s"
