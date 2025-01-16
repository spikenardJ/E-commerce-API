# Mini-Project: E-commerce API

# Task 1: Customer and CustomerAccount Management

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields 
from marshmallow import ValidationError
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:!Jaedyn77@localhost/ecom_db"
db = SQLAlchemy(app)
ma = Marshmallow(app)

# MARK: Schemas 

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("id", "name", "email", "phone")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Integer(required=True)

    class Meta:
        fields = ("username", "password", "customer_id")

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

class ProductSchema(ma.Schema):
    id = fields.Int()
    name = fields.String(required=True)
    price = fields.Float(required=True)
    stock_quantity = fields.Integer(required=True)

    class Meta:
        fields = ("id", "name", "price", "stock_quantity")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# helps us process the products related to orders to make sure we 
# are getting the product_id and quantity from the order data 
class OrderProductSchema(ma.Schema):
    # product_id = fields.Integer(required=True)
    product = fields.Nested(ProductSchema)
    quantity = fields.Integer(required=True)

    class Meta:
        fields = ("product", "quantity")

# Retrieving order with the id of id

class OrderSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    expected_delivery_date = fields.Date(required=True)
    customer_id = fields.Integer(required=True)
    # products = fields.List(fields.Nested(ProductSchema),required=True)
    order_products = fields.List(fields.Nested(OrderProductSchema))

    class Meta:
        fields = ("id", "date", "expected_delivery_date", "customer_id", "products", "order_products")

class PlaceOrderProductSchema(ma.Schema):
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True)

    class Meta:
        fields = ("product_id", "quantity")

class PlaceOrderSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    expected_delivery_date = fields.Date(required=True)
    customer_id = fields.Integer(required=True)
    products = fields.List(fields.Nested(PlaceOrderProductSchema),required=True)

    class Meta:
        fields = ("id", "date", "expected_delivery_date", "customer_id", "products")

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
place_order_schema = PlaceOrderSchema()
place_orders_schema = PlaceOrderSchema(many=True)

# TODO: Can probably comment out if not being used below 
place_order_product_schema = PlaceOrderProductSchema()
place_order_products_schema = PlaceOrderProductSchema(many=True)

# MARK: Models 
# back_populates better than backref

class OrderProduct(db.Model):
    __tablename__ = "OrderProducts"
    order_id = db.Column(db.Integer, db.ForeignKey("Orders.id"), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("Products.id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship("Product", back_populates="product_orders")
    order = db.relationship("Order", back_populates="order_products")


class Customer(db.Model):
    __tablename__ = "Customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    # One Customer has many orders
    orders = db.relationship("Order", back_populates="customer")

# order_product = db.Table("OrderProduct", 
#     db.Column("order_id", db.Integer, db.ForeignKey("Orders.id"), primary_key=True), 
#     db.Column("product_id", db.Integer, db.ForeignKey("Products.id"), primary_key=True))

class Order(db.Model): 
    __tablename__ = "Orders" 
    id = db.Column(db.Integer, primary_key=True) 
    date = db.Column(db.Date, nullable=False) 
    expected_delivery_date = db.Column(db.Date, nullable=False) 
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id")) 
    customer = db.relationship("Customer", back_populates="orders") 
    # products = db.relationship( "Product", secondary=order_product, back_populates="orders" )
    order_products = db.relationship("OrderProduct", back_populates="order", cascade="all, delete-orphan")


class CustomerAccount(db.Model):
    __tablename__ = "CustomerAccounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id"))
    customer = db.relationship("Customer", backref="customer_account", uselist=False)

class Product(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

    # Relationship to OrderProduct for detailed order information
    product_orders = db.relationship("OrderProduct", back_populates="product", overlaps="product")


@app.route("/", methods=["GET"])
def home():
    return "Welcome Home"

# Create Customer
@app.route("/customers", methods=["POST"])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(name=customer_data["name"], email=customer_data["email"], phone=customer_data["phone"])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"MESSAGE": "New customer added successfully."}), 201

# Get all Customers
@app.route("/customers", methods=["GET"])
def get_customers():
    try:
        customers = Customer.query.all()
        return customers_schema.jsonify(customers)
    except ValidationError as err:
        return jsonify(err.messages), 400

# Read Customer
@app.route("/customers/<int:id>", methods=["GET"])
def get_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        return customer_schema.jsonify(customer)
    except ValidationError as err:
        return jsonify(err.messages), 400

# Update Customer
@app.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data["name"]
    customer.email = customer_data["email"]
    customer.phone = customer_data["phone"]
    db.session.commit()
    return jsonify({"MESSAGE": "Customer details updated successfully."}), 200

# Delete Customer
@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"MESSAGE": "Customer removed successfully."}), 200

# Create CustomerAccount
@app.route("/customer_accounts", methods=["POST"])
def add_customer_account():
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer_account = CustomerAccount(username=customer_account_data["username"], password=customer_account_data["password"], customer_id=customer_account_data["customer_id"])
    db.session.add(new_customer_account)
    db.session.commit()
    return jsonify({"MESSAGE": "New customer account added successfully."}), 201

# Read CustomerAccount
@app.route("/customer_accounts/<int:id>", methods=["GET"])
def get_customer_account(id):
    try:
        customer_account = CustomerAccount.query.get_or_404(id)
        return customer_account_schema.jsonify(customer_account)
    except ValidationError as err:
        return jsonify(err.messages), 400

# Update CustomerAccount
@app.route("/customer_accounts/<int:id>", methods=["PUT"])
def update_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer_account.username = customer_account_data["username"]
    customer_account.password = customer_account_data["password"]
    customer_account.customer_id = customer_account_data["customer_id"]
    db.session.commit()
    return jsonify({"MESSAGE": "Customer account details updated successfully."}), 200

# Delete CustomerAccount
@app.route("/customer_accounts/<int:id>", methods=["DELETE"])
def delete_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify({"MESSAGE": "Customer account removed successfully."}), 200


# Task 2: Product Catalog

# Create Product
@app.route("/products", methods=["POST"])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data["name"], price=product_data["price"], stock_quantity=product_data["stock_quantity"])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"MESSAGE": "New product added successfully."}), 201

# Read Product
@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    try:
        product = Product.query.get_or_404(id)
        return product_schema.jsonify(product)
    except ValidationError as err:
        return jsonify(err.messages), 400

# Update Product
@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.name = product_data["name"]
    product.price = product_data["price"]
    product.stock_quantity = product_data["stock_quantity"]
    db.session.commit()
    return jsonify({"MESSAGE": "Product details updated successfully."}), 200

# Delete Product
@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"MESSAGE": "Product removed successfully."}), 200

# List Products
@app.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

# View and Manage Product Stock Levels (Bonus)

# Restock Products When Low (Bonus)
@app.route("/products/restock", methods=["POST"])
def restock_product():
    data = request.json
    product = Product.query.get_or_404(data["product_id"])
    product.stock_quantity += data["quantity"]
    db.session.commit()
    return jsonify({"MESSAGE": "Product restocked successfully."}), 200


# Task 3: Order Processing
# MARK: Orders

@app.route("/orders", methods=["POST"])
def add_order():
    try:
        order_data = place_order_schema.load(request.json)
        print("Order Data:", order_data)
    except ValidationError as err:
        print("Validation Error:", err.messages)
        return jsonify(err.messages), 400

    if not order_data["products"]:
        return jsonify({"error": "Order must include at least one product."}), 400

    new_order = Order(date=order_data["date"], customer_id=order_data["customer_id"], expected_delivery_date=order_data["expected_delivery_date"])

    for product in order_data["products"]:
        product_object = Product.query.get_or_404(product["product_id"])

        if product["quantity"] > product_object.stock_quantity:
            return jsonify({"error": f"Insufficient stock for product ID {product['product_id']}."}), 400
        
        product_object.stock_quantity -= product["quantity"]

        order_product_entry = OrderProduct(order=new_order, product=product_object, quantity=product["quantity"])
        db.session.add(order_product_entry)

    db.session.add(new_order)
    db.session.commit()
    return jsonify({ "message": "New order added successfully.", "order_id": new_order.id }), 201




# Retrieve All Orders
@app.route("/orders", methods=["GET"])
def get_orders():
    try:
        orders = Order.query.all()
        return orders_schema.jsonify(orders)
    except ValidationError as err:
        return jsonify(err.messages), 400

# Retrieve Order
# Retrieving order with the id of id
@app.route("/orders/<int:id>", methods=["GET"])
def get_order(id):
    try:
        order = Order.query.get_or_404(id)
        return order_schema.jsonify(order)
    except ValidationError as err:
        return jsonify(err.messages), 400

# Track Order
@app.route("/orders/<int:id>", methods=["GET"])
def track_order_status(id):
    try:
        order = Order.query.get_or_404(id)
        return order_schema.jsonify(order)
    except ValidationError as err:
        return jsonify(err.messages), 400

# Manage Order History (Bonus)
@app.route("/orders/<int:id>", methods=["PUT"])
def update_order(id):
    order = Order.query.get_or_404(id)
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    order.date = order_data["date"]
    order.expected_delivery_date = order_data["expected_delivery_date"]
    order.customer_id = order_data["customer_id"]
    db.session.commit()
    return jsonify({"MESSAGE": "Order details updated successfully."}), 200

# Cancel Order (Bonus)
@app.route("/orders/<int:id>", methods=["DELETE"])
def cancel_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"MESSAGE": "Order cancelled successfully."}), 200

# Calculate Order Total Price (Bonus)


# Database Integration


if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        db.create_all()
    app.run(debug=True)

# Data Validation and Error Handling

# User Interface (Postman)

# GitHub Repository