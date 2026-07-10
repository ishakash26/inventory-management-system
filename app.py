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
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM admin WHERE name=%s AND password=%s",
            (username, password)
        )

        user = cursor.fetchone()

        if user:
            return redirect(f"/dashboard?username={username}")
        else:
            return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")

# Dashboardvg
@app.route("/dashboard")
def dashboard():
    username = request.args.get("username", "Admin")
    # Total Products
    cursor.execute("SELECT COUNT(*) AS total FROM products")
    total_products = cursor.fetchone()["total"]

    # Total Categories
    cursor.execute("SELECT COUNT(*) AS total FROM categories")
    total_categories = cursor.fetchone()["total"]

    # Total Warehouses
    cursor.execute("SELECT COUNT(*) AS total FROM warehouse")
    total_warehouse = cursor.fetchone()["total"]

    # Total Orders
    cursor.execute("SELECT COUNT(*) AS total FROM orders")
    total_orders = cursor.fetchone()["total"]

    # Recent Products
    cursor.execute("""
        SELECT product_name, status
        FROM products
        ORDER BY product_id DESC
        LIMIT 5
    """)
    recent_products = cursor.fetchall()

       # Low Stock Products
    cursor.execute("""
        SELECT product_name, quantity
        FROM products
        WHERE quantity <= 10
    """)
    low_stock = cursor.fetchall()

    cursor.execute("SELECT name FROM admin WHERE id=1")
    admin = cursor.fetchone()

    # Products by Category Chart
    cursor.execute("""
        SELECT category, COUNT(*) AS total
        FROM products
        GROUP BY category
    """)
    category_chart = cursor.fetchall()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_categories=total_categories,
        total_warehouse=total_warehouse,
        total_orders=total_orders,
        recent_products=recent_products,
        low_stock=low_stock,
        admin_name=username,
        category_chart=category_chart,
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
    cursor.execute("SELECT * FROM admin WHERE id=1")
    admin = cursor.fetchone()

    return render_template("settings.html", admin=admin)


@app.route("/logout")
def logout():
    return redirect("/")

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        cursor.execute(
            "UPDATE admin SET name=%s, email=%s WHERE id=1",
            (name, email)
        )
        db.commit()

        return redirect("/settings")

    return render_template("edit_profile.html")

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        cursor.execute("SELECT password FROM admin WHERE id=1")
        admin = cursor.fetchone()

        if admin["password"] == old_password:
            cursor.execute(
                "UPDATE admin SET password=%s WHERE id=1",
                (new_password,)
            )
            db.commit()
            return redirect("/settings")
        else:
            return "Old Password is Incorrect"

    return render_template("change_password.html")

@app.route("/suppliers")
def suppliers():
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    return render_template("suppliers.html", suppliers=suppliers)


@app.route("/add-supplier", methods=["GET", "POST"])
def add_supplier():
    if request.method == "POST":
        supplier_name = request.form["supplier_name"]
        company_name = request.form["company_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        cursor.execute("""
            INSERT INTO suppliers
            (supplier_name, company_name, phone, email, address)
            VALUES (%s, %s, %s, %s, %s)
        """, (supplier_name, company_name, phone, email, address))

        db.commit()
        return redirect("/suppliers")

    return render_template("add_supplier.html")

@app.route("/delete-supplier/<int:id>")
def delete_supplier(id):
    cursor.execute("DELETE FROM suppliers WHERE id=%s", (id,))
    db.commit()
    return redirect("/suppliers")
@app.route("/edit-supplier/<int:id>", methods=["GET", "POST"])
def edit_supplier(id):

    if request.method == "POST":
        supplier_name = request.form["supplier_name"]
        company_name = request.form["company_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        cursor.execute("""
        UPDATE suppliers
        SET supplier_name=%s,
            company_name=%s,
            phone=%s,
            email=%s,
            address=%s
        WHERE id=%s
        """,(supplier_name, company_name, phone, email, address, id))

        db.commit()
        return redirect("/suppliers")

    cursor.execute("SELECT * FROM suppliers WHERE id=%s",(id,))
    supplier = cursor.fetchone()

    return render_template("edit_supplier.html", supplier=supplier)

@app.route("/orders")
def orders():
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    return render_template("orders.html", orders=orders)


@app.route("/add-order", methods=["GET", "POST"])
def add_order():

    if request.method == "POST":

        product_name = request.form["product_name"]
        supplier_name = request.form["supplier_name"]
        quantity = request.form["quantity"]
        order_date = request.form["order_date"]
        status = request.form["status"]

        cursor.execute("""
        INSERT INTO orders
        (product_name,supplier_name,quantity,order_date,status)
        VALUES(%s,%s,%s,%s,%s)
        """,(product_name,supplier_name,quantity,order_date,status))

        db.commit()

        return redirect("/orders")

    return render_template("add_order.html")
@app.route("/edit-order/<int:id>", methods=["GET", "POST"])
def edit_order(id):

    if request.method == "POST":

        product_name = request.form["product_name"]
        supplier_name = request.form["supplier_name"]
        quantity = request.form["quantity"]
        order_date = request.form["order_date"]
        status = request.form["status"]

        cursor.execute("""
        UPDATE orders
        SET product_name=%s,
            supplier_name=%s,
            quantity=%s,
            order_date=%s,
            status=%s
        WHERE id=%s
        """, (product_name, supplier_name, quantity, order_date, status, id))

        db.commit()

        return redirect("/orders")

    cursor.execute("SELECT * FROM orders WHERE id=%s", (id,))
    order = cursor.fetchone()

    return render_template("edit_order.html", order=order)
@app.route("/delete-order/<int:id>")
def delete_order(id):
    cursor.execute("DELETE FROM orders WHERE id=%s", (id,))
    db.commit()
    return redirect("/orders")
@app.route("/categories")
def categories():
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    return render_template("categories.html", categories=categories)
@app.route("/add-category", methods=["GET","POST"])
def add_category():

    if request.method=="POST":

        category_name=request.form["category_name"]

        cursor.execute(
            "INSERT INTO categories(category_name) VALUES(%s)",
            (category_name,)
        )

        db.commit()

        return redirect("/categories")

    return render_template("add_category.html")


@app.route("/edit-category/<int:id>", methods=["GET","POST"])
def edit_category(id):

    if request.method=="POST":

        category_name=request.form["category_name"]

        cursor.execute(
            "UPDATE categories SET category_name=%s WHERE id=%s",
            (category_name,id)
        )

        db.commit()

        return redirect("/categories")

    cursor.execute("SELECT * FROM categories WHERE id=%s",(id,))
    category=cursor.fetchone()

    return render_template("edit_category.html",category=category)


@app.route("/delete-category/<int:id>")
def delete_category(id):

    cursor.execute("DELETE FROM categories WHERE id=%s",(id,))
    db.commit()

    return redirect("/categories")
@app.route("/warehouse")
def warehouse():
    cursor.execute("SELECT * FROM warehouse")
    warehouses = cursor.fetchall()
    return render_template("warehouse.html", warehouses=warehouses)


@app.route("/add-warehouse", methods=["GET","POST"])
def add_warehouse():

    if request.method=="POST":

        warehouse_name=request.form["warehouse_name"]
        location=request.form["location"]
        manager_name=request.form["manager_name"]
        capacity=request.form["capacity"]

        cursor.execute("""
        INSERT INTO warehouse
        (warehouse_name,location,manager_name,capacity)
        VALUES(%s,%s,%s,%s)
        """,(warehouse_name,location,manager_name,capacity))

        db.commit()

        return redirect("/warehouse")

    return render_template("add_warehouse.html")


@app.route("/edit-warehouse/<int:id>", methods=["GET","POST"])
def edit_warehouse(id):

    if request.method=="POST":

        warehouse_name=request.form["warehouse_name"]
        location=request.form["location"]
        manager_name=request.form["manager_name"]
        capacity=request.form["capacity"]

        cursor.execute("""
        UPDATE warehouse
        SET warehouse_name=%s,
            location=%s,
            manager_name=%s,
            capacity=%s
        WHERE id=%s
        """,(warehouse_name,location,manager_name,capacity,id))

        db.commit()

        return redirect("/warehouse")

    cursor.execute("SELECT * FROM warehouse WHERE id=%s",(id,))
    warehouse=cursor.fetchone()

    return render_template("edit_warehouse.html",warehouse=warehouse)


@app.route("/delete-warehouse/<int:id>")
def delete_warehouse(id):

    cursor.execute("DELETE FROM warehouse WHERE id=%s",(id,))
    db.commit()

    return redirect("/warehouse")
    
    
if __name__ == "__main__":
    app.run(debug=True)