# Mini-Project: E-commerce API

# Task 1: Customer and CustomerAccount Management

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields 
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:!Jaedyn77@localhost/e_commerce_db"
db = SQLAlchemy(app)
ma = Marshmallow(app)

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone")

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
    # id = fields.Int()
    name = fields.String(required=True)
    price = fields.Float(required=True)
    stock_quantity = fields.Integer(required=True)

    class Meta:
        fields = ("id", "name", "price", "stock_quantity")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class OrderSchema(ma.Schema):
    date = fields.Date(required=True)
    expected_delivery_date = fields.Date(required=True)
    customer_id = fields.Integer(required=True)
    products = fields.List(fields.Nested(ProductSchema),required=True)

    class Meta:
        fields = ("date", "expected_delivery_date", "customer_id", "products")

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

class Customer(db.Model):
    __tablename__ = "Customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship("Order", backref="customer")

order_product = db.Table("OrderProduct", 
    db.Column("order_id", db.Integer, db.ForeignKey("Orders.id"), primary_key=True), 
    db.Column("product_id", db.Integer, db.ForeignKey("Products.id"), primary_key=True))

class Order(db.Model):
    __tablename__ = "Orders"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    expected_delivery_date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id"))
    products = db.relationship("Product", secondary=order_product, backref=db.backref("orders_products"))

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
    orders = db.relationship("Order", secondary=order_product, backref=db.backref("products_orders"))


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


# Task 3: Order Processing

# Place Order
@app.route("/orders", methods=["POST"])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_order = Order(date=order_data["date"], customer_id=order_data["customer_id"], expected_delivery_date=order_data["expected_delivery_date"])
    for product in order_data["products"]:
        product_object = Product.query.get_or_404(product["id"])
        new_order.products.append(product_object)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"MESSAGE": "New order added successfully."}), 201

# Retrieve Order
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