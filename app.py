from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="isha262005",
    database="inventory_system"
)

cursor = db.cursor(dictionary=True)

# Login Page
@app.route("/")
def login():
    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    cursor.execute("SELECT COUNT(*) AS total FROM products")
    total_products = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS instock FROM products WHERE status='In Stock'")
    in_stock = cursor.fetchone()["instock"]

    cursor.execute("SELECT COUNT(*) AS outstock FROM products WHERE status='Out of Stock'")
    out_stock = cursor.fetchone()["outstock"]

    return render_template(
        "dashboard.html",
        total_products=total_products,
        in_stock=in_stock,
        out_stock=out_stock
    )

# Products Page
@app.route("/products")
def products():

    search = request.args.get("search")

    if search:
        cursor.execute("""
            SELECT * FROM products
            WHERE product_name LIKE %s
            OR category LIKE %s
            OR variant LIKE %s
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))
    else:
        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    return render_template("products.html", products=products)

# Add Product
@app.route("/add_product", methods=["POST"])
def add_product():

    print(request.form)
    print(request.form["quantity"])

    product_name = request.form["product_name"]
    category = request.form["category"]
    variant = request.form["variant"]
    quantity = request.form["quantity"]
    price = request.form["price"]
    expiry_date = request.form["expiry_date"]
    warehouse = request.form["warehouse"]
    supplier = request.form["supplier"]
    status = request.form["status"]

    cursor.execute("""
        INSERT INTO products
        (product_name, category, variant, quantity, price, expiry_date, warehouse, supplier, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        product_name,
        category,
        variant,
        quantity,
        price,
        expiry_date,
        warehouse,
        supplier,
        status
    ))

    db.commit()

    return redirect("/products")

@app.route("/edit_product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]
        variant = request.form["variant"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        expiry_date = request.form["expiry_date"]
        warehouse = request.form["warehouse"]
        supplier = request.form["supplier"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE products
            SET product_name=%s,
                category=%s,
                variant=%s,
                quantity=%s,
                price=%s,
                expiry_date=%s,
                warehouse=%s,
                supplier=%s,
                status=%s
            WHERE product_id=%s
        """, (
            product_name,
            category,
            variant,
            quantity,
            price,
            expiry_date,
            warehouse,
            supplier,
            status,
            id
        ))

        db.commit()
        return redirect("/products")

    cursor.execute("SELECT * FROM products WHERE product_id=%s", (id,))
    product = cursor.fetchone()

    return render_template("edit_product.html", product=product)

@app.route("/delete_product/<int:id>")
def delete_product(id):
    cursor.execute("DELETE FROM products WHERE product_id=%s", (id,))
    db.commit()
    return redirect("/products")

@app.route("/update_product/<int:id>", methods=["POST"])
def update_product(id):

    product_name = request.form["product_name"]
    category = request.form["category"]
    variant = request.form["variant"]
    quantity = request.form["quantity"]

    cursor.execute("""
        UPDATE products
        SET product_name=%s,
            category=%s,
            variant=%s,
            quantity=%s
        WHERE product_id=%s
    """, (
        product_name,
        category,
        variant,
        quantity,
        id
    ))

    db.commit()

    return redirect("/products")
@app.route("/reports")
def reports():

    cursor.execute("SELECT COUNT(*) AS total FROM products")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS low FROM products WHERE quantity<=10")
    low = cursor.fetchone()["low"]

    cursor.execute("SELECT COUNT(*) AS outstock FROM products WHERE status='Out of Stock'")
    outstock = cursor.fetchone()["outstock"]

    return render_template(
        "reports.html",
        total=total,
        low=low,
        outstock=outstock
    )

@app.route("/settings")
def settings():
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(debug=True)