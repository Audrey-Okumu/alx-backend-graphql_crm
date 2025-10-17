from crm.models import Customer, Product

def run():
    Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
    Product.objects.create(name="Phone", price=500.00, stock=5)
    Product.objects.create(name="Laptop", price=999.99, stock=10)
