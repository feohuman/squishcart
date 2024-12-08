import os
from time import sleep

from streamlit import rerun, session_state
from streamlit.elements.widgets.selectbox import SelectboxSerde
from datetime import datetime
from middleware import *
from objects import *
from scanner import *
from recalg import *

import streamlit as st
import plotly.express as px
st.set_page_config(layout="wide")
backend =  BackendMiddleware("http://0.0.0.0:8000")
token = None

def load_data():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data

data = load_data()


# Initialize session state for shopping cart
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "cart" not in st.session_state:
    st.session_state.cart = {}

def display_register():
    # Toggle button for the registration form
    if 'show_register_form' not in st.session_state:
        st.session_state.show_register_form = False

    # Display the toggle button
    if st.button("Register an account"):
        # Toggle the visibility of the register form
        st.session_state.show_register_form = not st.session_state.show_register_form

    # Show the registration form if the state is True
    if st.session_state.show_register_form:
        with st.form("register"):
            st.markdown("#### Register an account")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            is_admin = st.checkbox("Admin")
            submit = st.form_submit_button("Register")

            if submit:
                if password == confirm_password:
                    # Call your registration function
                    request = backend.register_user(username=username, password=password, is_admin=is_admin)
                    print(request)
                    st.success("Registration successful")
                    st.session_state.show_register_form = False  # Hide form after successful registration
                    st.rerun()  # Rerun the app to show the login page
                else:
                    st.error("Passwords do not match.")

def display_login():
    placeholder = st.empty()

    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        placeholder.empty()  # Remove the login form once submitted
        st.session_state.logged_in = True

        try:
            request = backend.login_user(username=username, password=password)
            if request and "access_token" in request:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.access_token = request["access_token"]  # Save the token
                st.session_state.is_admin = request.get("is_admin", 0)  # Save the admin status if present
                # print(st.session_state.access_token)

                st.success("Login successful")
                st.rerun()  # Rerun the app to show the logged-in state
            else:
                st.session_state.logged_in = False
                st.success("Invalid credentials. Please try again.")
                st.rerun()
        except ValueError as e:
            st.session_state.logged_in = False
            st.error("Invalid credentials. Please try again.")
            sleep(2)
            st.rerun()


        # Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.cart = {}
    st.success("You have been logged out.")



def display_admin_interface():
    st.title("Admin Interface")
    st.write("Welcome to the admin interface. Here you can manage the products in the store.")

    # Load the data from the JSON file
    with open("data.json", "r") as f:
        data = json.load(f)

    # Display current inventory
    st.subheader("Current Products")
    for product in data["products"]:
        st.write(f"**Name:** {product['name']}")
        st.write(f"**Price:** LEI {product['price']:.2f}")
        st.write(f"**Stock:** {product['number_of_products']}")
        st.write(f"**Expiration Date:** {product['soonest_expiration_date']}")
        # st.image(product["image"], caption=product["name"], width=100)
        st.write("---")

    # Add a new product
    st.subheader("Add New Product")
    with st.form("add_product_form"):
        new_name = st.text_input("Product Name")
        new_price = st.number_input("Product Price", min_value=0.0, step=0.01)
        new_stock = st.number_input("Stock Quantity", min_value=0, step=1)
        new_image = st.text_input("Image Path")
        new_expiration_date = st.date_input("Expiration Date")
        submit_add = st.form_submit_button("Add Product")

        if submit_add:
            new_product = {
                "name": new_name,
                "price": new_price,
                "image": new_image,
                "number_of_products": new_stock,
                "soonest_expiration_date": new_expiration_date.strftime("%m/%d/%y"),
            }
            data["products"].append(new_product)
            with open("data.json", "w") as f:
                json.dump(data, f, indent=4)
            st.success(f"Product '{new_name}' added successfully!")

    # Remove a product
    st.subheader("Remove Product")
    product_to_remove = st.selectbox("Select a product to remove", [p["name"] for p in data["products"]])
    if st.button("Remove Product"):
        data["products"] = [p for p in data["products"] if p["name"] != product_to_remove]
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)
        st.success(f"Product '{product_to_remove}' removed successfully!")

    # Update product details
    st.subheader("Update Product Details")
    product_to_update = st.selectbox("Select a product to update", [p["name"] for p in data["products"]])


    if product_to_update:
        product = next(p for p in data["products"] if p["name"] == product_to_update)
        updated_price = st.number_input("New Price", value=product["price"], step=0.01)
        updated_stock = st.number_input("New Stock", value=product["number_of_products"], step=1)
        updated_expiration_date = st.text_input(
            "New Expiration Date (MM/DD/YY)",
            value=product["soonest_expiration_date"],
        )
        if st.button("Update Product"):
            try:
                # Validate the date format
                datetime.strptime(updated_expiration_date, "%m/%d/%y")
                product["price"] = updated_price
                product["number_of_products"] = updated_stock
                product["soonest_expiration_date"] = updated_expiration_date
                with open("data.json", "w") as f:
                    json.dump(data, f, indent=4)
                st.success(f"Product '{product_to_update}' updated successfully!")
            except ValueError:
                st.error("Invalid date format. Please use MM/DD/YY.")


# Home page (with recommendations)
def display_home():

    st.title("🌟 Welcome to Mega!")
    st.write("Explore our recommended products and try out our delicious recipes.")

    # Create a two-column layout
    col1, col2 = st.columns([2, 1], gap="large")

    # Left Column: Recommended Products and Recipes
    with col1:
        # Displaying Recommended Products
        st.subheader("💡 Recommended Products")
        recommended_products = data["recommended_products"]

        for product in recommended_products:
            product_info = next((p for p in data["products"] if p["name"] == product), None)

            if product_info is None:
                st.warning(f"Product '{product}' not found in the database.")
                continue  # Skip this product if it's not found

            with st.container():
                col1_inner, col2_inner = st.columns([1, 3], gap="medium")

                # Display Product Image
                with col1_inner:
                    image_path = os.path.join(os.curdir, product_info["image"])
                    if os.path.exists(image_path):
                        st.image(image_path, caption=product_info["name"], use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/150", caption="No image available")

                # Display Product Details
                with col2_inner:
                    st.write(f"### {product_info['name']}")
                    st.write(f"💲 **Price:** LEI {product_info['price']:.2f}")
                    st.write(f"📦 **Stock Available:** {product_info['number_of_products']}")
                    st.write(f"⏳ **Expiration Date:** {product_info['soonest_expiration_date']}")

        st.write("---")  # Separator

        # Displaying Recommended Recipes
        st.subheader("🍴 Recommended Recipes")
        st.write("Here are some of our favorite recipes to try with our products:")
        with open("recommendations_Marcel.json", "r") as f:
            buf = json.load(f)

        if "recipes" in buf and buf["recipes"]:
            for recipe in buf["recipes"]:
                with st.container():
                    st.write(f"- **{recipe['name']}**: {recipe['instructions']}")
        else:
            st.write("Come back when we get to know each other more 😊")

    # Right Column: Most Purchased Products Chart
    with col2:
        most_purchased_products()

# Products page
def display_products():
    st.title("🛍️ Browse Products")
    st.markdown("Discover our range of high-quality products and add them to your cart!")

    # Display each product as a styled card
    for product_info in data["products"]:
        with st.container():
            st.write("---")  # Divider between products
            col1, col2 = st.columns([1, 3], gap="medium")

            # Product Image
            with col1:
                image_path = os.path.join(os.curdir, product_info["image"])
                print(image_path)
                if os.path.exists(image_path):
                    st.image(image_path, caption=product_info["name"], use_container_width=True)
                else:

                    st.image("https://via.placeholder.com/150", caption="No image available")  # Placeholder image

            # Product Details
            with col2:
                st.markdown(f"### {product_info['name']}")
                st.write(f" **Price:** LEI {product_info['price']:.2f}")
                st.write(f"📦 **Stock Available:** {product_info['number_of_products']}")
                st.write(f"⏳ **Expiration Date:** {product_info['soonest_expiration_date']}")

                # # Add to Cart Button with spacing
                # st.markdown(" ")
                # if st.button(f"🛒 Add {product_info['name']} to Cart", key=f"add_{product_info['name']}"):
                #     if product_info['name'] in st.session_state.cart:
                #         st.session_state.cart[product_info['name']] += 1
                #     else:
                #         st.session_state.cart[product_info['name']] = 1
                #     st.success(f"Added {product_info['name']} to the cart!")

    st.write("---")  # Final separator

# Shopping Cart page
# Shopping Cart page
def display_cart():
    import os
    from datetime import datetime

    st.title("🛒 Shopping Cart")
    st.write("Here are the items you've added to your cart:")

    # Check if the cart is empty
    if not st.session_state.get("cart", {}):  # Use get() to avoid errors if 'cart' is not initialized
        st.info("Your cart is currently empty. Add some products to get started!")
        return

    total_cost = 0
    discount_threshold_date = datetime.strptime("13/12/2024", "%d/%m/%Y")

    # Display items in the cart
    for product, cart_item in list(st.session_state.cart.items()):  # Safely iterate and modify
        # Fetch product details
        product_info = next((p for p in data["products"] if p["name"] == product), None)
        if not product_info:
            st.warning(f"Product '{product}' not found in database. Removing from cart.")
            del st.session_state.cart[product]
            continue

        product_price = product_info["price"]
        quantity = cart_item["quantity"]
        produce_date_str = cart_item["produce_date"]
        produce_date = datetime.strptime(produce_date_str, "%d/%m/%Y")

        # Apply discount if applicable
        if produce_date < discount_threshold_date:
            product_price *= 0.5

        item_total = product_price * quantity
        total_cost += item_total

        # Enhanced layout for each cart item
        with st.container():
            st.write("---")  # Divider between items
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])

            # Product Image
            with col1:
                image_path = os.path.join(os.curdir, product_info["image"])
                if os.path.exists(image_path):
                    st.image(image_path)
                else:
                    st.image("https://via.placeholder.com/80", caption="Image not available")  # Placeholder image

            # Product Details
            with col2:
                st.write(f"**{product_info['name']}**")
                st.write(f"Price per unit: LEI {product_price:.2f}")
                st.write(f"Quantity: {quantity}")
                st.write(f"Expiration Date: {produce_date.strftime('%d/%m/%Y')}")
                if produce_date < discount_threshold_date:
                    st.write("**50% Discount Applied**")

            # Item Total and Remove Button
            with col3:
                st.write(f"**Item Total:** LEI {item_total:.2f}")

            with col4:
                if st.button("➖ Remove 1", key=f"remove_{product}"):
                    st.session_state.cart[product]["quantity"] -= 1
                    if st.session_state.cart[product]["quantity"] <= 0:  # Remove if quantity reaches 0
                        del st.session_state.cart[product]
                        st.success(f"Removed {product} from the cart.")
                    else:
                        st.success(f"Decreased quantity of {product}.")
                    st.rerun()  # Refresh the page

    # Total Cost at the Bottom
    st.write("---")  # Final divider
    st.subheader(f"**Total Cost: LEI {total_cost:.2f}**")

    # Clear Cart Button
    if st.button("🧹 Clear Cart"):
        st.session_state.cart = {}
        st.success("Your cart has been cleared!")
        st.rerun()


def display_scanner():
    st.title("📷 Scan a Product!")
    decoded = scan_code()  # Get the scanned product name and expiration date from the scanned code
    # st.text(decoded)

    if decoded != "Checkout":
        # Parse product name and produce date from decoded string
        try:
            product_name = decoded.split("\n")[0]
            produce_date = decoded.split("\n")[1]
            # Assume name and date are separated by a newline
            product_name = product_name.strip()
            produce_date = produce_date.strip()

            # Find the product in the data
            product_info = next((p for p in data["products"] if p["name"].lower() == product_name.lower()), None)

            if product_info:
                # Check if the product is already in the cart
                if product_info["name"] in st.session_state.cart:
                    st.session_state.cart[product_info["name"]]["quantity"] += 1
                else:
                    # Add product to the cart with the expiration date
                    st.session_state.cart[product_info["name"]] = {
                        "quantity": 1,
                        "produce_date": produce_date,
                        "price" : product_info["price"]
                    }

                st.success(f"✅ {product_info['name']} has been added to your cart!")
            else:
                st.error(f"❌ Product '{product_name}' not found in the database.")
        except ValueError:
            st.error("❌ Failed to parse the scanned code. Ensure it includes both product name and expiration date.")

    elif decoded == "Checkout":
        # Decrement quantities in the JSON data
        for product_name, cart_item in st.session_state.cart.items():
            product_info = next((p for p in data["products"] if p["name"] == product_name), None)
            sender = Product(product_name, cart_item["quantity"], cart_item["price"], cart_item["produce_date"])
            addpurchasetojson(sender.jsonify(), "Marcel.json")
            recalg("Marcel.json", "recipes.json", "recommendations_Marcel.json")
            if product_info:
                product_info["number_of_products"] -= cart_item["quantity"]

                # Ensure stock doesn't go below zero
                if product_info["number_of_products"] < 0:
                    product_info["number_of_products"] = 0

        # Clear the cart after checkout
        st.session_state.cart = {}

        # Save updated product data back to JSON
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

        st.success("🛒 Checkout completed! Stock quantities updated.")

    else:
        # If decoding fails
        st.warning("No product detected. Please try scanning again!")

# a pie chart of the most purchased products
# data from Marcel.json
def load_purchases():
    with open('Marcel.json', 'r') as f:
        purchases = json.load(f)
    return purchases


# def most_purchased_products():
#     products = data["products"]
#     purchases = load_purchases()
#     # print(purchases['history'])
#     product_purchases = {}
#
#     for product in purchases['history']:
#         print(product)
#         if(not product):
#             continue
#         for key in products:
#
#             if key['name'] == product['name']:
#                 if key['name'] in product_purchases:
#                     product_purchases[key['name']] += 1
#                 else:
#                     product_purchases[key['name']] =1
#
#     # draw a pie chart
#     fig, ax = plt.subplots()
#     ax.pie(product_purchases.values(), labels = product_purchases.keys(), autopct='%1.1ff%%' )
#     ax.axis('equal')
#     st.pyplot(fig)

import plotly.express as px
import streamlit as st

def most_purchased_products():
    # Assuming data and purchases are loaded elsewhere in your app
    products = data["products"]
    purchases = load_purchases()
    product_purchases = {}

    for product in purchases['history']:
        if not product:
            continue
        for key in products:
            if key['name'] == product['name']:
                if key['name'] in product_purchases:
                    product_purchases[key['name']] += 1
                else:
                    product_purchases[key['name']] = 1

    # Create a pie chart using Plotly
    fig = px.pie(
        names=list(product_purchases.keys()),
        values=list(product_purchases.values()),
        title="Most Purchased"
    )

    # Customize the chart to match the website theme
    fig.update_layout(
        title_font=dict(family="sans serif", size=20, color="#333333"),  # Title font
        font=dict(family="sans serif", color="#333333"),  # General font
        paper_bgcolor="#eaf4e1",  # Light green background
        plot_bgcolor="#eaf4e1",  # Light green plot background
        # margin=dict(t=40, b=40, l=40, r=40),  # Adjust margins for better fit
        showlegend=True,  # Show the legend
        height=400,  # Set custom height for the chart
        width=800,   # Set custom width for the chart
    )

    # Update the colors for the chart slices
    fig.update_traces(
        marker=dict(
            colors=['#d0e6c1', '#a1c6a1', '#7bbd7b', '#5fa65f', '#4b9b4b'],  # Custom colors based on your theme
        )
    )

    # Display the chart in Streamlit, ensuring it uses full container width
    st.plotly_chart(fig, use_container_width=True)



# Sidebar Navigation with Icons
if st.session_state.logged_in:
    st.sidebar.title("🌟 Welcome to Mega!")
    st.sidebar.write(f"Logged in as: {st.session_state.username}")

    st.sidebar.button("🔓 Logout", on_click=logout, key="logout")

    scan = st.sidebar.button("📷 Scan Product", key="scan")

    # Create an attractive navigation menu with icons
    if st.session_state.is_admin:
        menu = st.sidebar.radio(
            "Navigate",
            ["🏠 Home", "🛍️ Products", "🛒 Shopping Cart", "🛠️ Admin"],
            key="nav",
            label_visibility="collapsed"
        )
    else:
        menu = st.sidebar.radio(
            "Navigate",
            ["🏠 Home", "🛍️ Products","🛒 Shopping Cart"],
            key="nav",
            label_visibility="collapsed"
        )

    # Handle the "Scan" button action
    if scan:
        display_scanner()
        st.rerun()

    if menu == "🛠️ Admin":
        display_admin_interface()
    elif menu == "🏠 Home":
        display_home()
    elif menu == "🛍️ Products":
        display_products()
    elif menu == "🛒 Shopping Cart":
        display_cart()
else:
    display_login()
    display_register()