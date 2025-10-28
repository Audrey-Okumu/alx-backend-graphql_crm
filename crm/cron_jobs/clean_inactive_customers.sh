#!/bin/bash
# Script: clean_inactive_customers.sh
# Description: Deletes customers with no orders in the past year and logs the result.

# Navigate to the Django project directory
cd "/mnt/c/Users/PC/Desktop/graphql/alx-backend-graphql_crm"

# Activate the virtual environment 
 source .env/bin/activate  

# Define log file
LOG_FILE="/tmp/customer_cleanup_log.txt" 

# Run the Django command via the manage.py shell
COUNT=$(python3 manage.py shell <<EOF
from django.utils import timezone
from crm.models import Customer, Order
from datetime import timedelta

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(id__in=Order.objects.filter(order_date__gte=one_year_ago).values('customer_id'))
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log the result with a timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $COUNT inactive customers" >> "$LOG_FILE"
