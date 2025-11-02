from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import logging
import requests

GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/crm_report_log.txt"

@shared_task
def generate_crm_report():
    try:
        transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=False, retries=3)
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""
        query {
            allCustomers { totalCount }
            allOrders { totalCount }
        }
        """)

        result = client.execute(query)
        customers = result["allCustomers"]["totalCount"]
        orders = result["allOrders"]["totalCount"]

        # Optional: revenue calculation using a custom query if needed
        revenue_query = gql("""
        query {
            allOrders {
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
        """)
        rev_result = client.execute(revenue_query)
        revenue = sum(float(o["node"]["totalAmount"]) for o in rev_result["allOrders"]["edges"])

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"{now} - Report: {customers} customers, {orders} orders, {revenue} revenue"

        logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(message)s")
        logging.info(report)
    except Exception as e:
        logging.error(f"Error generating CRM report: {e}")
