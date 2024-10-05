# Streamlit Dashboard

This project is a data analysis dashboard built using Streamlit by Melvin Kent Jonathan. It visualizes and analyzes various datasets related to customer orders, products and sellers.

## Project Structure
```bash
dashboard 
│ └── dashboard.py 
data 
│ ├── customer_dataset.csv 
│ ├── geolocation_dataset.csv 
│ ├── order_items_dataset.csv 
│ ├── order_payments_dataset.csv 
│ ├── order_review_dataset.csv 
│ ├── orders_dataset.csv 
│ ├── product_category_name_translated.csv 
│ ├── products_dataset.csv 
│ └── sellers_dataset.csv 
Proyek_Analisis_Data.ipynb 
README.md 
requirements.txt 
url.txt
```



# Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Set up a virtual environment (optional but recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```
3. Install the required packages
    ```bash
    pip install -r requirements.txt
    ```


# Running the Dashboard
To run the Streamlit dashboard, execute the following command:
```bash
streamlit run dashboard/dashboard.py
```
# Usage
Once the dashboard is running, you can interact with various visualizations and analyses related customer orders, products and sellers data. Use the sidebar to navigate through different sections.
