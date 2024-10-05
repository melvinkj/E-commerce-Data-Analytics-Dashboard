import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import os

# Get the current directory of the script
current_dir = os.path.dirname(__file__)

# Construct paths for all CSV files
path_geolocation = os.path.join(current_dir, '..', 'data', 'geolocation_dataset.csv')
path_customers = os.path.join(current_dir, '..', 'data', 'customers_dataset.csv')
path_order_items = os.path.join(current_dir, '..', 'data', 'order_items_dataset.csv')
path_order_payments = os.path.join(current_dir, '..', 'data', 'order_payments_dataset.csv')
path_orders = os.path.join(current_dir, '..', 'data', 'orders_dataset.csv')
path_product_category_name_translation = os.path.join(current_dir, '..', 'data', 'product_category_name_translation.csv')
path_products = os.path.join(current_dir, '..', 'data', 'products_dataset.csv')
path_sellers = os.path.join(current_dir, '..', 'data', 'sellers_dataset.csv')

# Set the page configuration
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# Read the datasets
df_geolocation = pd.read_csv(path_geolocation)
df_customers = pd.read_csv(path_customers)
df_order_items = pd.read_csv(path_order_items)
df_order_payments = pd.read_csv(path_order_payments)
df_orders = pd.read_csv(path_orders)
df_product_category_name_translation = pd.read_csv(path_product_category_name_translation)
df_products = pd.read_csv(path_products)
df_sellers = pd.read_csv(path_sellers)


def create_delivered_orders():
    # Function that returns data frame of delivered orders with their delivery time
    df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])
    df_orders['order_delivered_customer_date'] = pd.to_datetime(df_orders['order_delivered_customer_date'])

    df_delivered_orders = df_orders[df_orders['order_status'] == 'delivered']
    df_delivered_orders['delivery_time'] = (df_delivered_orders['order_delivered_customer_date'] - 
                                        df_delivered_orders['order_purchase_timestamp']).dt.days

    return df_delivered_orders

def create_order_status_count():
    # Function that groups on-going order by status and count each occurences
    df_on_going_orders = df_orders[df_orders['order_status'] != 'delivered']
    df_order_status_counts = df_on_going_orders['order_status'].value_counts().reset_index()
    df_order_status_counts.columns = ['order_status', 'count']

    return df_order_status_counts

def create_product_english():
    # Function that joins df_products with df_product_category_name_translation to get its english category name
    df_product_english = pd.merge(df_products, df_product_category_name_translation, 'left', on='product_category_name')
    
    return df_product_english

df_product_english = create_product_english()

def create_orders_category():
    # Function that joins df_order_items and df_product_english to know the category of each orders
    df_orders_category = pd.merge(df_order_items, df_product_english, 'left', on='product_id')

    return df_orders_category


def create_top_performing_product_category():
    # Function that returns count of orders per category for top performing categories
    df_orders_category = create_orders_category()

    df_category_counts = df_orders_category['product_category_name_english'].value_counts()

    df_top_categories = df_category_counts.head(9)

    other_count = df_category_counts.iloc[9:].sum() 
    df_top_categories['Others'] = other_count  

    df_top_categories = df_top_categories.reset_index()
    df_top_categories.columns = ['category', 'count'] 

    return df_top_categories

def create_category_sales():
    # Function that returns sales per category
    df_product_order_price = pd.merge(df_order_items, df_product_english, 'left', on='product_id')

    # Aggregate sales per category
    df_category_sales = df_product_order_price.groupby('product_category_name_english')['price'].sum().reset_index()

    return df_category_sales

def count_selected_category_sales(category_sales, selected_category): 
    # Function that gets the sales for the selected category
    return category_sales[category_sales['product_category_name_english'] == selected_category]


def create_top_categories_by_sales():
    # Function that returns the top sales per category

    # Sort and get top 10 categories
    df_top_categories_by_sales = df_category_sales.nlargest(10, 'price')

    # Aggregate other categories into 'Others'
    df_other_sales = df_category_sales[~df_category_sales['product_category_name_english'].isin(df_top_categories_by_sales['product_category_name_english'])]
    total_other_sales = df_other_sales['price'].sum()

    # Append 'Others' category
    if total_other_sales > 0:
        df_others = pd.DataFrame({'product_category_name_english': ['Others'], 'price': [total_other_sales]})
        df_top_categories_by_sales = pd.concat([df_top_categories_by_sales, df_others], ignore_index=True)

    return df_top_categories_by_sales

def create_top_cities_with_seller():
    # Function to return the top cities with seller

    # Prepare data for pie chart
    df_city_counts = df_sellers['seller_city'].value_counts()

    # Select the top 9 cities and aggregate others
    df_top_cities = df_city_counts.head(9)
    other_count = df_city_counts.iloc[9:].sum()
    df_top_cities['Others'] = other_count  

    df_top_cities = df_top_cities.reset_index()
    df_top_cities.columns = ['seller_city', 'count'] 
    
    return df_top_cities

def create_monthly_sales():
    # Function to return month-to-month sales data 

    merged = pd.merge(df_orders, df_order_payments, 'inner', on='order_id')
    
    # Ensure 'order_purchase_timestamp' is a datetime type
    merged['order_purchase_timestamp'] = pd.to_datetime(merged['order_purchase_timestamp'])

    # Group by month and sum the payment value
    df_monthly_sales = merged.groupby(merged['order_purchase_timestamp'].dt.to_period('M'))['payment_value'].sum().reset_index()

    # Convert the period back to a datetime for plotting
    df_monthly_sales['order_purchase_timestamp'] = df_monthly_sales['order_purchase_timestamp'].dt.to_timestamp()

    return df_monthly_sales


st.sidebar.title("E-commerce Data Analytics Dashboard")

menu_options = ["Home", "Delivery Tracking", "Products", "Sellers", "Transactions"]

# Create a radio button for menu options
selection = st.sidebar.radio("Menu", menu_options)

# Content based on selection
if selection == "Home":
    st.header("Home")
    st.write("Welcome! I'm Melvin Kent Jonathan, a junior machine learning engineer.")
    st.markdown("This dashboard is created to gather insights from [E-commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) as a demonstration of my data analytics skills.")
    st.write("You can select the menu from the sidebar to see the functionalities.")
    
    st.markdown("")
    st.markdown("[Click here to contact me](https://www.linkedin.com/in/melvinkentjonathan/)")

elif selection == "Delivery Tracking":
    st.header("Delivery Tracking")
    df_delivered_orders = create_delivered_orders()

    col1, col2 = st.columns(2)

    #####################################
    col1.subheader("Overall Performance")
    col1.write(f"Average delivery time  : {df_delivered_orders['delivery_time'].mean():.2f} days")
    col1.write(f"Shortest delivery time : {df_delivered_orders['delivery_time'].min():.2f} days")
    col1.write(f"Longest delivery time  : {df_delivered_orders['delivery_time'].max():.2f} days")

    #####################################
    col2.subheader("On-going Order Status")
    col2.write("Double-click on legend to isolate one trace")
    df_order_status_counts = create_order_status_count()
    
    # Create a donut chart
    fig = px.pie(
        df_order_status_counts,
        names='order_status',
        values='count',
        hole=0.4,  
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    col2.plotly_chart(fig) # Display the donut chart

    #####################################
    st.subheader("Delivery Time Distribution")
    plt.figure(figsize=(10, 6))
    plt.hist(df_delivered_orders['delivery_time'].dropna(), bins=150, color='skyblue', edgecolor='black')
    plt.title('Histogram of Delivery Time', color='white')
    plt.xlabel('Delivery Time (Days)', color='white')
    plt.ylabel('Frequency', color='white')
    plt.grid(axis='y', alpha=0.75, color='white')
    plt.gca().tick_params(axis='both', colors='white')

    st.pyplot(plt, transparent=True)
    plt.clf()

elif selection == "Products":
    st.header("Products")
    df_category_sales = create_category_sales()

    col1, col2 = st.columns(2)

    #####################################
    col1.subheader("Item Sold per Category")
    col1.write("Double-click on legend to isolate one trace")

    df_top_categories = create_top_performing_product_category()
    # Create an interactive pie chart
    fig = px.pie(
        df_top_categories, 
        names='category', 
        values='count', 
        hover_data=['count'],
        labels={'count': '#Sold Items'}
    )

    col1.plotly_chart(fig)
    
    #####################################
    col2.subheader("Sales per Category")
   
    categories = df_product_english['product_category_name_english'].unique()

    selected_category = col2.selectbox('Select a category:', categories)
    

    selected_sales = count_selected_category_sales(df_category_sales, selected_category)

    # Display sales for the selected category
    if not selected_sales.empty:
        col2.write(f"Sales for {selected_category}:")
        col2.write(f"${selected_sales['price'].values[0]:,.2f}")

    #####################################
    st.subheader('Sales per Category')
    
    df_top_categories_by_sales = create_top_categories_by_sales()
    # Create a bar chart
    fig = px.bar(
        df_top_categories_by_sales,
        x='product_category_name_english',
        y='price',
        title='Total Sales per Category (Top 10)',
        labels={'price': 'Total Sales', 'product_category_name_english': 'Category'},
        text='price'
    )

    # Show the bar chart
    st.plotly_chart(fig)

elif selection == "Sellers":
    st.header("Sellers")

    # SELLERS LOCATION HEATMAP
    st.subheader('Sellers Location Distribution')
    st.write('Please wait for the map to load...')
    sellers_geolocation = pd.merge(df_sellers, df_geolocation, left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='inner')  # You can change 'inner' to 'left', 'right', or 'outer' as needed

    m = folium.Map(location=[sellers_geolocation['geolocation_lat'].mean(), sellers_geolocation['geolocation_lng'].mean()], zoom_start=4)

    # Create heat data from latitude and longitude
    heat_data = [[row['geolocation_lat'], row['geolocation_lng']] for index, row in sellers_geolocation.iterrows()]

    # Add heatmap layer
    HeatMap(heat_data).add_to(m)

    folium_static(m)

    #####################################
    col1, col2 = st.columns(2)

    col1.subheader("Sellers City")
    cities = df_sellers['seller_city'].unique()
    selected_city = col1.selectbox('Select a city:', cities)
    df_filtered_sellers = df_sellers[df_sellers['seller_city'] == selected_city]

    # Display the list of sellers for the selected city
    if not df_filtered_sellers.empty:
        col1.write(f"Sellers (seller_id) in {selected_city}:")
        for index, row in df_filtered_sellers.iterrows():
            col1.write(row['seller_id'])
    else:
        col1.write("No sellers found for this city.")
    

        
    #####################################
    col2.subheader("Sellers by City ")
    col2.write("Double-click on legend to isolate one trace")
    df_top_cities = create_top_cities_with_seller()

    # Create an interactive pie chart
    fig = px.pie(
        df_top_cities,
        names='seller_city', 
        values='count', 
        title='Sellers by City',
        hover_data=['count'],
        labels={'count': 'Number of Sellers'}
    )

    col2.plotly_chart(fig) 

elif selection == "Transactions":
    st.header("Transactions")
    #####################################

    # Count the occurrences of each order status
    order_payment_counts = df_order_payments['payment_type'].value_counts().reset_index()
    order_payment_counts.columns = ['payment_type', 'count']

    # Create a donut chart 
    fig = px.pie(
        order_payment_counts,
        names='payment_type',
        values='count',
        title='Payment Type Distribution',
        hole=0.4,  
        color_discrete_sequence=px.colors.qualitative.Plotly
    )

    # Display the donut chart
    st.plotly_chart(fig)


    ###################################################
    df_monthly_sales = create_monthly_sales()
    # Create a line chart 
    fig = px.line(
        df_monthly_sales,
        x='order_purchase_timestamp',
        y='payment_value',
        title='Transaction Value Month-to-Month',
        labels={'order_purchase_timestamp': 'Month', 'payment_value': 'Total Sales'},
        markers=True  # Adds markers to the line for better visibility
    )

    # Display the line chart
    st.plotly_chart(fig)