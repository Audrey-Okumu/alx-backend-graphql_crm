import re     #For regular expression pattern matching (phone validation)
import graphene
from graphene_django import DjangoObjectType
from django.db import IntegrityError, transaction
from django.utils import timezone
from .models import Customer, Product, Order
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter


# ===========================
# GraphQL Types
# ===========================
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filter_fields = []
        interfaces = (graphene.relay.Node,)  #gives it unique GraphQL ID.


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = []
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filter_fields = []
        interfaces = (graphene.relay.Node,)


# ===========================
# Mutations
# ===========================

# Create Customer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    #outputs the mutation will return
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if phone and not re.match(r"^\+?\d[\d\-]+$", phone):
            raise Exception("Invalid phone format. Use +1234567890 or 123-456-7890")

        try:
            customer = Customer.objects.create(name=name, email=email, phone=phone)
            return CreateCustomer(customer=customer, message="Customer created successfully!")
        except IntegrityError:
            raise Exception("Email already exists.")


# Bulk Create Customers(Many customers at once)
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic  #ensures that if one record fails, you can handle it safely without breaking the entire batch.
    def mutate(self, info, input):
        created = []
        errors = []
        for record in input:
            try:
                name = record.get("name")
                email = record.get("email")
                phone = record.get("phone")

                if not name or not email:
                    raise ValueError("Name and email are required.")

                if Customer.objects.filter(email=email).exists():
                    raise ValueError(f"Email '{email}' already exists.")

                if phone and not re.match(r"^\+?\d[\d\-]+$", phone):
                    raise ValueError(f"Invalid phone format: {phone}")

                customer = Customer(name=name, email=email, phone=phone)
                customer.save()
                created.append(customer)

            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created, errors=errors)


# Create Product
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


# Create Order
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        if not product_ids:
            raise Exception("At least one product is required.")

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more product IDs are invalid.")

        total_amount = sum([p.price for p in products])
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date or timezone.now()
        )
        order.products.set(products)
        order.save()
        return CreateOrder(order=order)


# ===========================
# Query Class
# ===========================
class Query(graphene.ObjectType):
    # Filtered and sortable queries
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter,
        order_by=graphene.String(required=False)
    )
    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter,
        order_by=graphene.String(required=False)
    )
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter,
        order_by=graphene.String(required=False)
    )

    # Single-object lookups
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True))

    # === Resolvers ===     Functions that tell GraphQL how to actually get the data from the database.
    def resolve_all_customers(root, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_products(root, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_orders(root, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_customer(root, info, id):
        return Customer.objects.get(pk=id)

    def resolve_product(root, info, id):
        return Product.objects.get(pk=id)

    def resolve_order(root, info, id):
        return Order.objects.get(pk=id)


# ===========================
# Root Mutation   Entry Point for Changes
# ===========================
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
  #registers all mutations so GraphQL knows they exist.