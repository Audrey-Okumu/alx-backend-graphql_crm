from datetime import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# === Configuration ===
GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """Logs a heartbeat message and optionally checks GraphQL hello field."""

    try:
        # 1️⃣ Log heartbeat message
        now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        message = f"{now} CRM is alive"

        # Use logging to append to file
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format="%(message)s"
        )
        logging.info(message)

        # 2️⃣ Optional: GraphQL health check
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
