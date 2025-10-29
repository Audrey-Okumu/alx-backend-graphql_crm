from datetime import datetime
import os
import requests  # optional, used to ping GraphQL

LOG_FILE = "/tmp/crm_heartbeat_log.txt"
GRAPHQL_URL = "http://localhost:8000/graphql"  # update if needed

def log_crm_heartbeat():
    """Logs a heartbeat message to confirm CRM app is alive."""
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{now} CRM is alive\n"

    # Append heartbeat to the log file
    with open(LOG_FILE, "a") as f:
        f.write(message)

    #  Verify GraphQL hello field
    try:
        query = {"query": "{ hello }"}
        response = requests.post(GRAPHQL_URL, json=query, timeout=5)
        if response.status_code == 200:
            print(f"{now} GraphQL endpoint responded successfully")
        else:
            print(f"{now} GraphQL endpoint returned error {response.status_code}")
    except Exception as e:
        print(f"{now} GraphQL heartbeat failed: {e}")
