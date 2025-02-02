import csv
import statistics
from httpx import ConnectError
from collections import defaultdict
import pandas as pd
import streamlit as st
from helpers.analyzer.classify import classify

# Streamlit Session State
ss = st.session_state

mm_month = {
    1: "January ❄️",
    2: "February ❤️",
    3: "March 🍀",
    4: "April 🌷",
    5: "May 🌸",
    6: "June ☀️",
    7: "July 🎆",
    8: "August 🌻",
    9: "September 🍂",
    10: "October 🎃",
    11: "November 🦃",
    12: "December 🎄"
}
# items grouped by classification
healthy_items = []
unhealthy_items = []
unhealthy_sum = 0
unknown_items = []
healthy_count = 0

# the number of items with each classification
unhealthy_count = 0
unknown_count = 0
total_items = 0

# the total amount spent for each month
mmyy_sum = defaultdict(float)

# item name and the number of times it was purchased
item_occur = {}


# Initialize Session State Variables
if "valid_csv" not in ss:
    ss.valid_csv = False
if "csv_content" not in ss:
    ss.csv_content = ""


st.title("Receipt Analyzer")


# CSV file uploader
uploaded_csv = st.file_uploader(
    "Upload your CSV with existing receipt data", ["csv"],
    accept_multiple_files=False,
    key="user_csv"
)

# Handle uploaded file
if uploaded_csv is None:
    st.warning("Please upload a CSV file", icon=":material/warning:")
else:
    csv_content = uploaded_csv.read().decode("UTF-8").splitlines()
    csv_content = list(csv.reader(csv_content))

    # The file is empty
    if len(csv_content) == 0:
        st.warning("Your CSV file is empty. Upload one with data to gain insights", icon=":material/warning:")
    else:
        st.success("Successfully uploaded CSV", icon=":material/check:")
        ss.csv_content = csv_content
        ss.valid_csv = True


ollama_server_refused = False
if ss.valid_csv:
    dates, items, prices = [], [], []

    # Process each row in the CSV
    for line in ss.csv_content:
        date, item, price = line[0:3]
        dates.append(date)
        items.append(item)
        price = float(price)
        prices.append(price)

        # Classify Item
        classification = ""
        try:
            classification = classify(item)
        except ConnectError as e:
            ollama_server_refused = True
        if classification == "Healthy":
            healthy_count += 1
            healthy_items.append(item)
        elif classification == "Unhealthy":
            unhealthy_count += 1
            unhealthy_items.append(item)
            unhealthy_sum += price
        else:
            unknown_count += 1
            unknown_items.append(item)

        # Monthly Spending Breakdown
        mm, dd, yy = date.split("/")
        mmyy_sum[f"{mm}/{yy}"] += price

        # Item Occurrences
        if item not in item_occur:
            item_occur[item] = 1
        else:
            item_occur[item] += 1

        total_items += 1

    # sort dict by number of occurences in descending order
    item_occur = sorted(item_occur.items(), key=lambda x: x[1], reverse=True)

    # Prepare DataFrames by padding so all lists are the same length
    max_length = max(len(healthy_items), len(unhealthy_items), len(unknown_items))
    healthy_items += [""] * (max_length - len(healthy_items))
    unhealthy_items += [""] * (max_length - len(unhealthy_items))
    unknown_items += [""] * (max_length - len(unknown_items))

    classification_df = pd.DataFrame({
        "Healthy Items": healthy_items,
        "Unhealthy Items": unhealthy_items,
        "Unknown Items": unknown_items
    })


    # VIEW ALL ITEMS (collapsible)
    with st.expander("View All Items", expanded=False):
        df = pd.DataFrame(item_occur, columns=["Item", "Number of Purchases"])
        st.table(df)


    # 80-20 RULE (if server connection is present)
    if not ollama_server_refused:
        st.header("80-20 Rule", divider=True)
        if total_items - unknown_count != 0:
            # Display classification percentages
            st.write(f"""
            **Summary of Purchases**:
            - **Healthy**: {int(100 * (healthy_count / (total_items - unknown_count)))}%
            - **Unhealthy**: {int(100 * (unhealthy_count / (total_items - unknown_count)))}%
            - Note: Items not classified (unknown) are excluded from this breakdown.
            (Numbers may not be 100% accurate and are only meant to give a rough idea)
            """)

            # Collapsible menu for detailed breakdown
            with st.expander("See Detailed Breakdown"):
                st.write("### Item Classification")
                st.table(classification_df)
            st.write(f"You could save ${unhealthy_sum:.2f} by cutting out your unhealthy purchases!")
        else:
            st.write("No classifiable items found in your upload.")


    # MONTHLY SPENDING TRENDS
    st.header("Monthly Spending Trends", divider=True)
    max_spending_key = max(mmyy_sum, key=mmyy_sum.get)
    month, year = max_spending_key.split('/')
    max_spending_month = mm_month[int(month)]
    st.write(f"**Max Spending Month**: {max_spending_month} {year}")
    st.write(f"**Mean Monthly Spending**: ${statistics.mean(mmyy_sum.values()):.2f}")


    # ITEM OCCURRENCES
    st.header("Most Purchased Items", divider=True)
    if not item_occur:
        st.write("No items to display.")
    else:
        # Dynamically generate the output based on the number of items available
        top_items = [
            f"{i + 1}. {item[0]} {'were' if item[0].lower().endswith('s') else 'was'} bought \
            {item[1]} time{'s' if item[1] > 1 else ''}"
            for i, item in enumerate(item_occur[:3])  # get up the top 3 items
        ]
        st.markdown("\n".join(top_items))


    # MONTHLY GRAPHING
    st.header("Graphing Monthly Spending", divider=True)
    month_totals = pd.DataFrame({
        "Month": mmyy_sum.keys(),
        "Spending": mmyy_sum.values()
    })
    month_totals = month_totals.set_index("Month")
    st.bar_chart(
        data=month_totals,
        x_label = "Month",
        y_label = "Spending ($)"
    )

