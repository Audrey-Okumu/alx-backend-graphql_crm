"""
Script: send_order_reminders.py
Description:
Queries the GraphQL endpoint for orders within the last 7 days
and logs reminders to /tmp/order_reminders_log.txt
"""

from datetime import datetime, timedelta
import logging #Python’s built-in logging system used to write messages to a file
import sys #for system-level actions
from gql import gql, Client  #Gql library to send graphql queries
from gql.transport.requests import RequestsHTTPTransport


# === Configuration ===
GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

# === Logging Setup ===
logging.basicConfig(             #configures root logger
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main(): #Where execution begins
    try:
        # Define time range (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

        # Setup GraphQL transport  Set up a connection to the GraphQL API
        transport = RequestsHTTPTransport(
            url=GRAPHQL_URL,
            verify=False,
            retries=3,
        )

        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Define GraphQL query
        query = gql("""
        query GetRecentOrders($date: DateTime!) {
            allOrders(orderDate_Gte: $date) {
                edges {
                    node {
                        id
                        customer {
                            email
                        }
                        orderDate
                    }
                }
            }
        }
        """)

        # Execute query
        params = {"date": seven_days_ago}
        result = client.execute(query, variable_values=params)

        orders = result.get("allOrders", {}).get("edges", [])

        if not orders:
            logging.info("No recent orders found.")
        else:
            for order in orders:
                node = order["node"]
                order_id = node["id"]
                email = node["customer"]["email"]
                order_date = node["orderDate"]
                logging.info(f"Reminder: Order {order_id} for {email} (Date: {order_date})")

        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error running order reminder script: {e}")
        print("Error:", e)
        sys.exit(1)
        
#Only run main() if this file is being executed directly
if __name__ == "__main__":
    main()