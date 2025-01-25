import io
import cv2
import numpy as np
import streamlit as st
from helpers.scanner.receipt import Receipt
from helpers.scanner.parsers import *


ss = st.session_state


def get_choice_of_two(choice1: str, choice2: str):
    """
    Displays two buttons side by side and dims/disables the other option
    based on the user's selection.
    """
    if "selected_choice" not in ss:
        ss.selected_choice = None

    col1, col2 = st.columns(2)

    with col1:
        if st.button(choice1, disabled=(ss.selected_choice == choice2)):
            ss.selected_choice = choice1

    with col2:
        if st.button(choice2, disabled=(ss.selected_choice == choice1)):
            ss.selected_choice = choice2

    return ss.selected_choice


def reset():
    file_prev_key = int(ss.file_uploader_key)
    store_prev_key = int(ss.store_choice_key)
    # Reset session state and mark reset flag
    for key in list(ss.keys()):
        del ss[key]

    ss.file_uploader_key = str(file_prev_key + 1)
    ss.store_choice_key = str(store_prev_key + 1)


st.title("Receipt Scanner")


# Collapsable How to Use
with st.expander("Getting the Best Results"):
    st.write(
        """
        The receipt shouldn't be faded to oblivion! The higher the quality of the image the better
        the output will be. An ideal receipt consists of the following...
        - **Cropped** such that only the receipt is visible
        - As little shadow as possible
        - Good lighting
        - Minimal drawings or marks on the receipt
        - Prominent text
        """)


# Reset Button
if st.button("Reset Scanner"):
    reset()
    st.rerun()

receiptType_parser = {
    "Target": TargetParser(),
    "Costco": CostcoParser(),
    "Walmart": WalmartParser(),
    "Other": GeneralParser(),
}
SUPPORTED_STORES = list(receiptType_parser.keys())
SUPPORTED_STORES.remove("Other")

if "receipt" not in ss or ss.receipt is None:
    ss.receipt = Receipt()
if "user_csv" not in ss:
    ss.user_csv = None
if "ready_to_add_to_csv" not in ss:
    ss.ready_to_add_to_csv = False
if "ready_to_output_csv" not in ss:
    ss.ready_to_output_csv = False
if "csv_choice" not in ss:
    ss.csv_choice = None
if "final_output" not in ss:
    ss.final_output = ""
if "file_uploader_key" not in ss:
    ss.file_uploader_key = "0"
if "store_choice_key" not in ss:
    ss.store_choice_key = str(int(ss.file_uploader_key) + 1)  # since keys must be unique

# Receipt Uploader Widget
uploaded_file = st.file_uploader(
    "Upload your receipt",
    type=["heic", "jpg", "jpeg", "png"],
    accept_multiple_files=False,
    key=ss.file_uploader_key,
)
if uploaded_file is not None:
    ss.receipt.file = uploaded_file

# Warn user if a receipt is not uploaded
if ss.receipt.file:
    st.success("Successfully uploaded 1 receipt", icon=":material/check:")
else:
    st.warning("No receipt uploaded", icon=":material/warning:")


if "receipt.store" not in ss:
    ss.receipt.store = ""
# Receipt Type Dropdown
receipt_store = st.selectbox(
    "What store is your receipt from?",
    SUPPORTED_STORES + ["Other"],
    index=None,
    key=ss.store_choice_key,
    placeholder="Select an option...",
)

# Receipt Type Warning if not selected
if receipt_store:
    ss.receipt.store = receipt_store
    if receipt_store != "Other":
        st.success(
            f"Your receipt is from {ss.receipt.store}",
            icon=":material/check:"
        )
    else:
        st.success(
            "You have uploaded a receipt not present in the dropdown menu",
            icon=":material/check:"
        )
else:
    st.warning("Please the store your receipt is from", icon=":material/warning:")




items, prices = [], []
output_csv = ""
if ss.receipt.store and ss.receipt.file and not ss.ready_to_add_to_csv:
    # Convert file upload into opencv readable format
    file_bytes = np.frombuffer(ss.receipt.file.read(), np.uint8)
    ss.receipt.file = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Identify best parser for the receipt
    parser = receiptType_parser[ss.receipt.store]

    # Use parser to extract information
    receipt_ocr = parser.ocr_receipt(ss.receipt.file)
    ss.receipt.items, ss.receipt.prices = parser.group_ocr_result(receipt_ocr)
    month, day, year = parser.extract_date(receipt_ocr)

    # Any date field is empty
    if month == "" or day == "" or year == "":
        st.write("No date could be extracted. Please enter it manually")
        tmp = st.date_input(
            "Select the receipt date",
            value=None,
            format="MM/DD/YYYY",
            disabled=(ss.receipt.date != "")
        )
        ss.receipt.date = tmp.strftime("%x") if tmp else None

    # Date was properly and fully extracted. Now make sure it is correct
    else:
        st.write(f"Does this date look correct? (mm/dd/yyyy): {month}/{day}/{year}")
        choice = get_choice_of_two("Yes", "No")
        if choice == "Yes":
            ss.receipt.date = f"{month}/{day}/{year}"
        elif choice == "No":
            tmp = st.date_input(
                "Select the receipt date", value=None, format="MM/DD/YYYY",
                disabled=(ss.receipt.date != "")
            )
            ss.receipt.date = tmp.strftime("%x") if tmp else None

    if ss.receipt.date and ss.receipt.items != [] and ss.receipt.prices != []:
        for j in range(len(ss.receipt.items)):
            ss.final_output += f"{ss.receipt.date}, {ss.receipt.items[j]}, {ss.receipt.prices[j]}\n"
        ss.ready_to_add_to_csv = True


# Get the user's CSV preference
if ss.ready_to_add_to_csv:
    st.write("Do you want to add to an existing CSV or create a new one?")
    ss.csv_choice = st.radio(
        "Choose your option:",
        options=["Create new", "Add to existing"],
        index=0,  # Default selection
    )

if ss.csv_choice == "Add to existing":
    uploaded_csv = st.file_uploader(
        "Upload your CSV with the existing receipt data", ["csv"],
        accept_multiple_files=False,
        key="user_csv"
    )
    if uploaded_csv is None:
        st.warning("Please upload a CSV file")


if ss.ready_to_add_to_csv and ss.get("user_csv") is not None:
    uploaded_file = io.StringIO(ss.user_csv.getvalue().decode('utf-8'))
    ss.final_output = uploaded_file.read() + ss.final_output
    ss.ready_to_output_csv = True
    st.success("Successfully uploaded CSV", icon=":material/check:")

if ss.ready_to_output_csv or ss.csv_choice == "Create new":
    name = "receipt_data.csv"  # the display name is the same as the file name
    st.download_button(
        label=name,
        data=ss.final_output,
        file_name=name,
        icon=":material/download:"
    )

