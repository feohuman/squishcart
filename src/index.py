import cv2
import streamlit as st
from PIL import Image
import json
import os

from streamlit import button

from scanner import *
from objects import *

# Initialize session state for shopping cart
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Login function
def display_login():
    placeholder = st.empty()
    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if email == "admin" and password == "admin":
            st.session_state.logged_in = True  # Set logged-in flag
            placeholder.empty()
            st.success("Login successful")
            st.rerun()  # Reload the app with logged-in state
        else:
            st.error("Login failed. Please try again.")

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.cart = {}
    st.success("You have been logged out.")


# Load data from JSON file
def load_data():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data

data = load_data()

# Home page (with recommendations)
def display_home():
    st.title("🌟 Welcome to Mega!")
    st.write("Explore our recommended products and try out our delicious recipes.")

    # Displaying Recommended Products
    st.subheader("💡 Recommended Products")
    recommended_products = data["recommended_products"]

    for product in recommended_products:
        product_info = next((p for p in data["products"] if p["name"] == product), None)

        if product_info is None:
            st.warning(f"Product '{product}' not found in the database.")
            continue  # Skip this product if it's not found

        with st.container():
            col1, col2 = st.columns([1, 3], gap="medium")

            # Display Product Image
            with col1:
                image_path = os.path.join("product_images", product_info["image"])
                if os.path.exists(image_path):
                    st.image(image_path, caption=product_info["name"], use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/150", caption="No image available")  # Placeholder image

            # Display Product Details
            with col2:
                st.write(f"### {product_info['name']}")
                st.write(f"💲 **Price:** ${product_info['price']:.2f}")
                st.write(f"📦 **Stock Available:** {product_info['number_of_products']}")
                st.write(f"⏳ **Soonest Expiration Date:** {product_info['soonest_expiration_date']}")

                # Add to Cart Button
                if st.button(f"🛒 Add {product_info['name']} to Cart", key=f"add_{product_info['name']}"):
                    if product_info['name'] in st.session_state.cart:
                        st.session_state.cart[product_info['name']] += 1
                    else:
                        st.session_state.cart[product_info['name']] = 1
                    st.success(f"Added {product_info['name']} to the cart!")

    st.write("---")  # Separator

    # Displaying Recommended Recipes
    st.subheader("🍴 Recommended Recipes")
    st.write("Here are some of our favorite recipes to try with our products:")

    # Loop through recipes and display them in a styled format
    for recipe in data["recipes"]:
        with st.container():
            st.markdown(f"🔹 **{recipe}**")

    st.write("Happy Shopping and Cooking! 😊")


# Products page
def display_products():
    st.title("Products")
    st.write("Browse our products below and add them to your cart.")

    # Display each product and allow adding to cart
    for product_info in data["products"]:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{product_info['name']}**")
        with col2:
            st.write(f"Price: ${product_info['price']:.2f}")
        with col3:
            # Load product image from the JSON file
            image_path = os.path.join("product_images", product_info["image"])
            if os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
            else:
                st.write("No image available.")
            
            # Add to Cart button
            if st.button(f"Add {product_info['name']} to Cart", key=f"add_{product_info['name']}"):
                if product_info['name'] in st.session_state.cart:
                    st.session_state.cart[product_info['name']] += 1
                else:
                    st.session_state.cart[product_info['name']] = 1
                st.success(f"Added {product_info['name']} to the cart!")

# Shopping Cart page
def display_cart():
    st.title("🛒 Shopping Cart")
    st.write("Here are the items you've added to your cart:")

    if not st.session_state.cart:
        st.info("Your cart is currently empty. Add some products to get started!")
        return

    total_cost = 0

    # Display items in the cart
    for product, quantity in list(st.session_state.cart.items()):  # Use list() to safely iterate and modify
        product_info = next(p for p in data["products"] if p["name"] == product)
        product_price = product_info["price"]
        item_total = product_price * quantity
        total_cost += item_total

        # Enhanced layout for each cart item
        with st.container():
            st.write("---")  # Divider between items
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])

            # Product Image
            with col1:
                image_path = os.path.join("product_images", product_info["image"])
                if os.path.exists(image_path):
                    st.image(image_path, width=80)
                else:
                    st.image("https://via.placeholder.com/80", caption="Image not available")  # Placeholder image

            # Product Details
            with col2:
                st.write(f"**{product_info['name']}**")
                st.write(f"Price per unit: ${product_price:.2f}")
                st.write(f"Quantity: {quantity}")

            # Item Total and Remove Button
            with col3:
                st.write(f"**Item Total:** ${item_total:.2f}")

            # Remove Item Button
            with col4:
                if st.button("➖ Remove 1", key=f"remove_{product}"):
                    st.session_state.cart[product] -= 1
                    if st.session_state.cart[product] <= 0:  # If quantity reaches 0, remove from cart
                        del st.session_state.cart[product]
                        st.success(f"Removed {product} from the cart.")
                    else:
                        st.success(f"Decreased quantity of {product}.")
                    st.rerun()  # Refresh the page

    # Total Cost at the Bottom
    st.write("---")  # Final divider
    st.subheader(f"**Total Cost: ${total_cost:.2f}**")

    # Clear Cart Button
    if st.button("🧹 Clear Cart"):
        st.session_state.cart = {}
        st.success("Your cart has been cleared!")
        st.rerun()



def display_scanner():
    st.title("Scan a Product!")
    decoded = scan_code()

# Display content based on the menu
if st.session_state.logged_in:
    st.sidebar.title("Retail App")
    st.sidebar.write("Logged in as: admin")
    st.sidebar.button("🔓 Logout", on_click=logout)
    scan = st.sidebar.button("Scanner")
    st.sidebar.empty()
    menu = st.sidebar.radio("Navigate", ["Home", "Products", "Shopping Cart"])
    if scan:
        display_scanner()
    if menu == "Home":
        display_home()
    elif menu == "Products":
        display_products()
    elif menu == "Shopping Cart":
        display_cart()
else:
    display_login()
