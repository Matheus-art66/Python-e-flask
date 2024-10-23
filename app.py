from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

login_manager = LoginManager()
app = Flask(__name__)
app.config['SECRET_KEY'] = "minha_chave_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# user(id,username,password)
class User(db.Model, UserMixin):
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(80), nullable = False, unique = True)
     password = db.Column(db.String(80), nullable = False)
     cart = db.relationship('CartItem', backref='user', lazy=True)

# modelagem
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas do produto
@app.route('/login', methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()

    if user and data.get("password") == user.password:
            login_user(user)
            return jsonify({"message": "logged in succesfully"}), 200
    return jsonify({"message": "UNAUTHORIZED. invalid"}), 401
        
            
@app.route('/logout',methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "logout succesfully"})
     
@app.route('/api/products/add HTTP/1.1', methods=["POST"])
@login_required
def add_product():

    data = request.json

    if 'name' in data and 'price' in data:
        product= Product(name=data["name"],price=data["price"],description=data.get("description",""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "product added succesfully"})
    
    return jsonify({"message": "Invalid product data"}), 400

@app.route('/api/products/delete/HTTP 1.1/<int:product_id>', methods=['DELETE'])
@login_required
def app_delete(product_id):

    product= Product.query.get(product_id)

    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "product deleted succesfully"})
    
    return jsonify({"message": "product not found"}), 404

@app.route('/api/products/HTTP 1.1/<int:product_id>', methods=['GET'])
def get_product_details(product_id):

    product= Product.query.get(product_id)

    if product:
        return jsonify({"id":product.id,
                        "Name": product.name,
                        "Price":product.price,
                        "Description":product.description})
    return jsonify({"message": "product not found"}), 404

@app.route('/api/products/update/HTTP 1.1/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):

    product = Product.query.get(product_id)

    if not product:
        return jsonify({"message": "product not found"}), 404
    
    data = request.json

    if 'name' in data:
        product.name = data['name']

    if 'price' in data:
        product.price = data['price']

    if 'description' in data:
        product.description = data['description']
    
    db.session.commit()
    return jsonify({'messagen': 'Product update successfully'})

@app.route('/api/products', methods=["GET"])
def get_products():
    products = Product.query.all()

    product_list=[]

    for product in products:
        product_data={"id":product.id,
                        "Name": product.name,
                        "Price":product.price,}
        product_list.append(product_data)

    return jsonify(product_list)

# checkout
@app.route('/api/cart/add/<int:product_id>', methods=["POST"])
@login_required
def add_to_cart(product_id):
    # usuario
    user = User.query.get(int(current_user.id))
    # produto
    product = Product.query.get(product_id)

    if user and product :
        cart_item = CartItem(user_id=user.id, product_id= product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({'menssage':'Item added to the cart successfully'})
    return jsonify({'menssage':'Failed to add item to the cart'}), 400

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@login_required
def remove_to_cart(product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'menssage':'Item removed form the cart successfully'})
    return jsonify({'menssage':'Failed to remove item form the cart'}), 400

@app.route('/api/catr', methods=['GET'])
@login_required
def view_cart():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    cart_content= []
    for cart_item in cart_items:
        product= Product.query.get(cart_item.product_id)
        cart_content.append({"id":cart_item.id,
                        "user_id": cart_item.user_id,
                        "product_name":product.name,
                        "product_price":product.price
                        })
        return jsonify(cart_content)

@app.route('/api/cart/checkout', methods=["POST"])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'menssage': 'Checkout successful. Cart has been cleared.'}), 200

# definir uma rota da pagina inicial e a função requisição do usuario

@app.route('/')
def hello():
    return 'Hello World'
if __name__ == "__main__":
    app.run(debug=True)