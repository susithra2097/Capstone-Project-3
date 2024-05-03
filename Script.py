import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3


def image_to_text(path):
    input_img = Image.open(path)
    image_array = np.array(input_img)
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_array, detail=0)
    return text, input_img


def extracted_text(texts):
    extracted_dict = {"NAME": [], "DESIGNATION": [], "COMPANY_NAME": [], "CONTACT": [], "EMAIL": [], "WEBSITE": [],
                      "ADDRESS": [], "PINCODE": []}

    extracted_dict["NAME"].append(texts[0])
    extracted_dict["DESIGNATION"].append(texts[1])

    for i in range(2, len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-", "").isdigit() and '-' in texts[i]):
            extracted_dict["CONTACT"].append(texts[i])
        elif "@" in texts[i] and ".com" in texts[i]:
            extracted_dict["EMAIL"].append(texts[i])
        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            small = texts[i].lower()
            extracted_dict["WEBSITE"].append(small)
        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
            extracted_dict["PINCODE"].append(texts[i])
        elif re.match(r'^[A-Za-z]', texts[i]):
            extracted_dict["COMPANY_NAME"].append(texts[i])
        else:
            remove_colon = re.sub(r'[,;]', '', texts[i])
            extracted_dict["ADDRESS"].append(remove_colon)

    for key, value in extracted_dict.items():
        if len(value) > 0:
            concatenate = " ".join(value)
            extracted_dict[key] = [concatenate]
        else:
            value = "NA"
            extracted_dict[key] = [value]

    return extracted_dict


# Streamlit part

st.set_page_config(layout="wide")
st.title("Bizcard: Business Card Data Extraction with OCR")

with st.sidebar:
    select_option = option_menu("Main Menu", ["Home", "Upload & Save", "Modify", "Delete"])

if select_option == "Home":
    # Existing code for the Home section
    pass

elif select_option == "Upload & Save":
    # Existing code for the Upload & Save section
    pass

elif select_option == "Delete":
    # Existing code for the Delete section
    pass

elif select_option == "Modify":
    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()

    # select query
    select_query = "SELECT * FROM bizcard_details"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
                                            "ADDRESS", "PINCODE", "IMAGE"))

    col1, col2 = st.columns(2)
    with col1:
        selected_name = st.selectbox("Select the name", table_df["NAME"])

    df_3 = table_df[table_df["NAME"] == selected_name]

    if not df_3.empty:  # Check if df_3 is not empty
        df_4 = df_3.copy()

        # Streamlit UI for modifying data

        col1, col2 = st.columns(2)
        with col1:
            mo_name = st.text_input("Name", df_3["NAME"].iloc[0])
            mo_desi = st.text_input("Designation", df_3["DESIGNATION"].iloc[0])
            mo_com_name = st.text_input("Company_name", df_3["COMPANY_NAME"].iloc[0])
            mo_contact = st.text_input("Contact", df_3["CONTACT"].iloc[0])
            mo_email = st.text_input("Email", df_3["EMAIL"].iloc[0])

            df_4["NAME"] = mo_name
            df_4["DESIGNATION"] = mo_desi
            df_4["COMPANY_NAME"] = mo_com_name
            df_4["CONTACT"] = mo_contact
            df_4["EMAIL"] = mo_email

        with col2:
            mo_website = st.text_input("Website", df_3["WEBSITE"].iloc[0])
            mo_addre = st.text_input("Address", df_3["ADDRESS"].iloc[0])
            mo_pincode = st.text_input("Pincode", df_3["PINCODE"].iloc[0])
            mo_image = st.text_input("Image", df_3["IMAGE"].iloc[0])

            df_4["WEBSITE"] = mo_website
            df_4["ADDRESS"] = mo_addre
            df_4["PINCODE"] = mo_pincode
            df_4["IMAGE"] = mo_image

        st.write("---")
        st.write("### Modify Data")
        st.dataframe(df_4)

        col1, col2 = st.columns(2)
        with col1:
            button_modify = st.button("Modify", use_container_width=True)

        if button_modify:
            # Update Query
            update_query = '''UPDATE bizcard_details SET name=?, designation=?, company_name=?, contact=?, 
                              email=?, website=?, address=?, pincode=?, image=? WHERE name=?'''

            # Convert dataframe row to tuple for SQL insertion
            new_data = tuple(df_4.values.tolist()[0] + [selected_name])

            cursor.execute(update_query, new_data)
            mydb.commit()

            st.success("Modified successfully.")
