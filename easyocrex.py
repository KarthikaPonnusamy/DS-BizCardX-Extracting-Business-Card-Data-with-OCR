import easyocr as easyocr
import pandas as pd
import cv2
import plotly.express as px
import pymysql
import streamlit as st
import os
from PIL import Image
from streamlit_option_menu import option_menu
from io import StringIO
import matplotlib.pyplot as plt
import re

# Move set_page_config to the top
icon = Image.open("easyocricon.jpg")
st.set_page_config(page_title= "DS-BizCardX: Extracting Business Card Data with OCR",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded"
                   )

# After set_page_config, you can define other functions and variables
reader = easyocr.Reader(['en'])
#CONNECT WITH LOCAL DB
mydb = pymysql.connect(host="127.0.0.1",
                        user="root",
                        password="admin@123",
                        database="easyocrex"
                    )
cursor = mydb.cursor()

#mysql table creation
cursor.execute('''CREATE TABLE IF NOT EXISTS card_data
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number TEXT,
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code TEXT,
                    image LONGBLOB
                    )''')


# SETTING-UP BACKGROUND IMAGE
def setting_bg():
    st.markdown(f""" 
    <style>
        .stApp {{
            background: linear-gradient(to right, #e9bfed, #e9bfed);
            background-size: cover;
            transition: background 0.5s ease;
        }}
        h1,h2,h3,h4,h5,h6 {{
            color: #e9bfed;
            font-family: 'Roboto', sans-serif;
        }}
        .stButton>button {{
            color: #e9bfed;
            background-color: #e9bfed;
            transition: all 0.3s ease-in-out;
        }}
        .stButton>button:hover {{
            color: #e9bfed;
            background-color: #2b5876;
        }}
        .stTextInput>div>div>input {{
            color: #e9bfed;
            background-color: #e9bfed;
        }}
    </style>
    """,unsafe_allow_html=True) 

# Call the setting_bg function
setting_bg()

# Define other parts of your Streamlit app

selected = option_menu(None, ["Home","Upload & Extract","Modify"], 
                       icons=["house","cloud-upload","pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "20px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})




if selected == "Home":

    st.markdown("## :blue[DS-BizCardX: Extracting Business Card Data with OCR]")
    st.markdown("## :blue[A User-Friendly Tool Using Streamlit and Plotly]")
    col1,col2 = st.columns([2,2],gap="medium")
    with col1:
        st.markdown("##")
        st.image("home.png")

    with col2:
        st.markdown("##")
        text = """
            *EasyOCR is a flexible and easy-to-use Python module for Optical Character Recognition (OCR). It enables computers to identify and extract text from photographs or scanned documents. OCR technology is valuable for various tasks, including data entry automation and image analysis*.

            **Applications of EasyOCR:**

            - Data Entry Automation
            - Image Analysis

            **EasyOCR** can be applied in a variety of real-world scenarios. Here are some potential applications:

            - Receipt and Invoice Data Extraction
            - Document Digitization
            - License Plate Recognition
            - Image Search
            """


        st.markdown(text, unsafe_allow_html=True)
        st.write("---")

if selected == "Upload & Extract":



    
   
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here", label_visibility="collapsed", type=["png", "jpeg", "jpg"])
    #st.write(uploaded_card)

    if uploaded_card is not None:
        
        def save_card(uploaded_card):
            
            with open(os.path.join("uploaded_cards",uploaded_card.name),"wb") as f:
                f.write(uploaded_card.getbuffer())
        save_card(uploaded_card)
 
    # elif uploaded_card is None:
    #     st.write("error")

        def image_preview(image,res):
            for (bbox, text, prob) in res:
                (tl,tr,br,bl) = bbox

                tl = (int(tl[0]),int(tl[1]))
                tr = (int(tr[0]),int(tr[1]))
                br = (int(br[0]),int(br[1]))
                bl = (int(bl[0]),int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15, 15)
            plt.axis('off')
            plt.imshow(image)

        # DISPLAYING THE UPLOADED CARD
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)

        with col2:
                st.markdown("#     ")
                st.markdown("#     ")
                with st.spinner("Processing image Please wait ..."):

                    st.set_option('deprecation.showPyplotGlobalUse', False)
                    saved_img = os.getcwd() + "\\" + "uploaded_cards" + "\\" + uploaded_card.name
                    image = cv2.imread(saved_img)
                    res= reader.readtext(saved_img)

                    st.markdown("### Image Processed and Data Extracted")
                    st.pyplot(image_preview(image, res))

    
        saved_img = os.getcwd() + "\\" + "uploaded_cards" + "\\" + uploaded_card.name
        result_reader = reader.readtext(saved_img,detail=0,paragraph=False)

        def binary_img(file_path):
            with open(file_path,'rb') as file:
                binaryData = file.read()
            return binaryData
        
        data = {"company_name": [],
                    "card_holder": [],
                    "designation": [],
                    "mobile_number": [],
                    "email": [],
                    "website": [],
                    "area": [],
                    "city": [],
                    "state": [],
                    "pin_code": [],
                    "image": binary_img(saved_img)
                    }
        
        def get_data(res):
                for ind, i in enumerate(res):
                    if "www " in i.lower() or "www." in i.lower():  # Website with 'www'
                        data["website"].append(i)
                    elif "WWW" in i:  # In case the website is in the next elements of the 'res' list
                        website = res[ind + 1] + "." + res[ind + 2]
                        data["website"].append(website)
                    elif '@' in i:
                        data["email"].append(i)
                    # To get MOBILE NUMBER
                    elif "-" in i:
                        data["mobile_number"].append(i)
                        if len(data["mobile_number"]) == 2:
                            data["mobile_number"] = " & ".join(data["mobile_number"])
                    # To get COMPANY NAME
                    elif ind == len(res) - 1:
                        data["company_name"].append(i)
                    # To get Card Holder Name
                    elif ind == 0:
                        data["card_holder"].append(i)
                    #To get designation
                    elif ind == 1:
                        data["designation"].append(i)

                    #To get area
                    if re.findall('^[0-9].+, [a-zA-Z]',i):
                        data["area"].append(i.split(',')[0])
                    elif re.findall('[0-9] [a-zA-z]+',i):
                        data["area"].append(i)
                    #To get city name
                    match1 = re.findall('.+St , ([a-zA-Z]+).+',i)
                    match2 = re.findall('.+St,,([a-zA-Z]+).+',i)
                    match3 = re.findall('^[E].*',i)
                    if match1:
                        data["city"].append(match1[0])
                    elif match2:
                        data["city"].append(match2[0])
                    elif match3:
                        data["city"].append(match3[0])

                    #To get state name
                    state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                    if state_match:
                        data["state"].append(i[:9])
                    elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                        data["state"].append(i.split()[-1])
                    if len(data["state"]) == 2:
                        data["state"].pop(0)

                    #To get Pincode
                    if len(i) >= 6 and i.isdigit():
                        data["pin_code"].append(i)
                    elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                        data["pin_code"].append(i[10:])
        get_data(result_reader)

        df = pd.DataFrame(data)
        st.success("Data Extracted ")
        st.write(df)


        button_style = """
                            <style>
                                .stButton>button {
                                    background-color: #ff6347; /* Change the background color here */
                                    color: white; /* Optionally change the text color */
                                }
                            </style>
                            """
        
        st.markdown(button_style, unsafe_allow_html=True)
        
        #save data
        btn1 = st.button("Save data",use_container_width=True)

        if btn1:
            for i,row in df.iterrows():
                insert_data = '''insert into card_data(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                values = ( row['company_name'], row['card_holder'], row['designation'],
                        row['mobile_number'], row['email'], row['website'],
                        row['area'], row['city'], row['state'], row['pin_code'],
                        row['image']
                            )
                #st.write(insert_data)
                #st.write(values)
                cursor.execute(insert_data,values)
                mydb.commit()
            st.success("Data saved")

if selected == "Modify":
    
    col1,col2,col3 = st.columns([3,3,2])    
    column1,column2 = st.columns(2,gap='large')

    try:
  
        with column1:
            cursor.execute("select card_holder from card_data")
            result = cursor.fetchall()
            #st.write(result)
            business_card= {}

            for row in result:
                business_card[row[0]] = row[0]
            #st.markdown("<p style='color: blue; font-weight: bold;'>Select card_holder name to Update</p>", unsafe_allow_html=True)
            selected_card = st.selectbox("Select card_holder name to Update",list(business_card.keys()))
        
            
            st.write("<p style='color: green; font-weight: bold;'>Update any data listed below</p>", unsafe_allow_html=True)
            cursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data where card_holder=%s ",(selected_card,))
            result = cursor.fetchone()
            
            text_color_style = """
                            <style>
                                .stTextInput>div>div>input {
                                    color: #F50D0D; /* Change the text color here */
                                    font-size: 16px; /* Change the text size here */
                                    font-weight: bold; /* Make the text bold */


                                }
                            </style>
                            """
            st.markdown(text_color_style, unsafe_allow_html=True)
            
            if result is not None:
                col4, col5 = st.columns(2,gap='medium')
                with col4:
                    company_name = st.text_input("COMPANY NAME", result[0])        
                    card_holder = st.text_input("CARD HOLDER", result[1])
                    designation = st.text_input("DESIGNATION", result[2])
                    mobile_number = st.text_input("MOBILE NO", result[3])
                    email = st.text_input("eMAIL", result[4])
                with col5:
                    website = st.text_input("WEBSITE", result[5])
                    area = st.text_input("AREA", result[6])
                    city = st.text_input("CITY", result[7])
                    state = st.text_input("STATE", result[8])
                    pin_code = st.text_input("PINCODE", result[9])

            else:
                st.write("No record found for the selected card holder.")


            button_style = """
                            <style>
                                .stButton>button {
                                    background-color: #ff6347; /* Change the background color here */
                                    color: white; /* Optionally change the text color */
                                }
                            </style>
                            """
            st.markdown(button_style, unsafe_allow_html=True)

            if st.button("Save Data"):
                cursor.execute("""update card_data SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s WHERE card_holder=%s """,(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,selected_card))
                mydb.commit()
                st.success("Modified data updated successfully")

        with column2:
            cursor.execute("select card_holder from card_data")
            result = cursor.fetchall()
            #st.write(result)
            business_card= {}

            for row in result:
                business_card[row[0]] = row[0]

            #st.markdown("<p style='color: blue; font-weight: bold;'>Select card_holder name to Delete</p>", unsafe_allow_html=True)
            selected_card = st.selectbox("Select card_holder name to Delete",list(business_card.keys()))
            st.write(f"Proceed to delete this card? :green[**{selected_card}'s**] ")
            

            if st.button("Delete"):
                cursor.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Selected card_holder record deleted")

    except:
        st.warning("There is no data available in the database")
    

    #view data

    if st.button("View data"):
        cursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")
        view_df= pd.DataFrame(cursor.fetchall(),columns=["company_name","card_holder","designation","mobile_number","email","website","area","city","state","pin_code"])
        st.write(view_df)


                
            







