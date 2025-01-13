import csv
import statistics
import pandas as pd
import streamlit as st
from analyzer_helpers import classify

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
# Initialize variables
healthy_items = []    # items grouped by classification
unhealthy_items = []
unhealthy_sum = 0
unknown_items = []
healthy_count = 0
unhealthy_count = 0   # the number of items with each classification
unknown_count = 0
total_items = 0
mm_sum = {}           # the total amount spent for each month
item_occur = {}       # item name and the number of times it was purchased


# Initialize Session State Variables
if "valid_csv" not in ss:
    ss.valid_csv = False
if "csv_content" not in ss:
    ss.csv_content = ""


st.title("Receipt Analyzer™")


# CSV file uploader
uploaded_csv = st.file_uploader(
    "Upload your CSV with the existing receipt data", ["csv"],
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
        classification = classify(item)
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
        mm = int(mm)
        if mm not in mm_sum:
            mm_sum[mm] = price
        else:
            mm_sum[mm] += price

        # Item Occurrences
        if item not in item_occur:
            item_occur[item] = 1
        else:
            item_occur[item] += 1

        total_items += 1

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

    # 80-20 RULE
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
    max_spending_month = mm_month[max(mm_sum, key=mm_sum.get)]
    st.write(f"**Max Spending Month**: {max_spending_month}")
    st.write(f"**Mean Monthly Spending**: ${statistics.mean(mm_sum.values()):.2f}")


    # ITEM OCCURRENCES
    st.header("Most Purchased Items", divider=True)
    item_occur = sorted(item_occur.items(), key=lambda x: x[1])  # ascending order
    if not item_occur:
        st.write("No items to display.")
    else:
        # Dynamically generate the output based on the number of items available
        top_items = [
            f"{i + 1}. {item[0]} {'were' if item[0].lower().endswith('s') else 'was'} bought \
            {item[1]} time{'s' if item[1] > 1 else ''}"
            for i, item in enumerate(item_occur[-1:-4:-1])  # get up the top 3 items
        ]
        st.markdown("\n".join(top_items))


    # MONTHLY GRAPHING
    st.header("Graphing Monthly Spending", divider=True)
    month_totals = pd.DataFrame({
        "Month": mm_sum.keys(),
        "Spending": mm_sum.values()
    })
    month_totals = month_totals.set_index("Month")
    st.bar_chart(
        data=month_totals,
        x_label = "Month",
        y_label = "Spending ($)"
    )

