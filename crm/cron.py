from datetime import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# === Configuration ===
GRAPHQL_URL = "http://localhost:8000/graphql"
HEARTBEAT_LOG_FILE = "/tmp/crm_heartbeat_log.txt"
LOW_STOCK_LOG_FILE = "/tmp/low_stock_updates_log.txt"

def log_crm_heartbeat():
    """Logs a heartbeat message and optionally checks GraphQL hello field."""
    try:
        now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        message = f"{now} CRM is alive"

        logging.basicConfig(
            filename=HEARTBEAT_LOG_FILE,
            level=logging.INFO,
            format="%(message)s"
        )
        logging.info(message)

        # Optional GraphQL hello check
        transport = RequestsHTTPTransport(
            url=GRAPHQL_URL,
            verify=False,
            retries=3,
        )

        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""
        query {
            hello
        }
        """)

        result = client.execute(query)
        response_message = result.get("hello", "No response from GraphQL")
        logging.info(f"GraphQL hello response: {response_message}")

    except Exception as e:
        logging.error(f"Error in CRM heartbeat: {e}")


# ===========================
# Low Stock Updater
# ===========================
def update_low_stock():
    """Runs a GraphQL mutation to restock low-stock products (stock < 10)."""
    try:
        transport = RequestsHTTPTransport(
            url=GRAPHQL_URL,
            verify=False,
            retries=3,
        )

        client = Client(transport=transport, fetch_schema_from_transport=True)

        mutation = gql("""
        mutation {
            updateLowStockProducts {
                message
                updatedProducts {
                    name
                    stock
                }
            }
        }
        """)

        result = client.execute(mutation)
        data = result.get("updateLowStockProducts", {})

        # Log results
        logging.basicConfig(
            filename=LOW_STOCK_LOG_FILE,
            level=logging.INFO,
            format="%(message)s"
        )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"[{now}] Low stock update triggered")

        message = data.get("message", "No message returned")
        updated = data.get("updatedProducts", [])

        logging.info(message)
        for p in updated:
            logging.info(f" - {p['name']}: new stock = {p['stock']}")

    except Exception as e:
        with open(LOW_STOCK_LOG_FILE, "a") as f:
            f.write(f"[{datetime.now()}] Error updating stock: {e}\n")
