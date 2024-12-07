import streamlit as st
from PIL import Image
import json
import os

# Initialize session state for shopping cart
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Load data from JSON file
def load_data():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data

data = load_data()

# Home page (with recommendations)
def display_home():
    st.title("Welcome to the Retail Store!")
    st.write("Browse our recommended products and try out our recipes.")

    # Displaying recommendations
    st.subheader("Recommended Products")
    recommended_products = data["recommended_products"]
    
    for product in recommended_products:
        product_info = next((p for p in data["products"] if p["name"] == product), None)
        
        if product_info is None:
            st.write(f"Product '{product}' not found.")
            continue  # Skip this product if it's not found

        col1, col2 = st.columns([1, 3])
        with col1:
            # Load product image from the JSON file
            image_path = os.path.join("product_images", product_info["image"])
            if os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
            else:
                st.write("No image available.")
        with col2:
            st.write(f"**{product_info['name']}**")
            st.write(f"Price: ${product_info['price']:.2f}")
            if st.button(f"Add {product_info['name']} to Cart", key=f"add_{product_info['name']}"):
                if product_info['name'] in st.session_state.cart:
                    st.session_state.cart[product_info['name']] += 1
                else:
                    st.session_state.cart[product_info['name']] = 1
                st.success(f"Added {product_info['name']} to the cart!")

    st.subheader("Recommended Recipes")
    st.write("Here are some of our favorite recipes that go well with our products.")
    for recipe in data["recipes"]:
        st.write(f"- {recipe}")

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
    st.title("Shopping Cart")
    if not st.session_state.cart:
        st.write("Your cart is empty.")
    else:
        total_cost = 0
        st.write("Here are the items in your cart:")
        
        # To avoid changing the dictionary size during iteration, collect products to remove in a list
        products_to_remove = []

        # Iterate over the cart to display the items
        for product, quantity in st.session_state.cart.items():
            product_info = next(p for p in data["products"] if p["name"] == product)
            price = product_info["price"] * quantity
            total_cost += price
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"**{product}**")
            with col2:
                st.write(f"Quantity: {quantity}")
            with col3:
                st.write(f"${price:.2f}")
            with col4:
                if st.button(f"Remove {product}", key=f"remove_{product}"):
                    # Instead of removing immediately, mark this product for removal
                    products_to_remove.append(product)

        # Remove products after iterating
        for product in products_to_remove:
            del st.session_state.cart[product]
            st.success(f"Removed {product} from the cart.")

        st.write("---")
        st.write(f"**Total: ${total_cost:.2f}**")

    # Clear Cart Button
    if st.button("Clear Cart"):
        st.session_state.cart = {}
        st.success("Cart cleared!")


# Sidebar menu for navigation
st.sidebar.title("Retail App")
menu = st.sidebar.radio("Navigate", ["Home", "Products", "Shopping Cart"])

# Display content based on the menu
if menu == "Home":
    display_home()
elif menu == "Products":
    display_products()
elif menu == "Shopping Cart":
    display_cart()
