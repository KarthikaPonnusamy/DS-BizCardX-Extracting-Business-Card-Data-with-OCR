# DS-BizCardX-Extracting-Business-Card-Data-with-OCR
## OCR 
- Optical character recognition, or OCR, defines the process of mechanically or electronically converting scanned images of handwritten, typed or printed text into machine-encoded text.
## BizCardX
 - BizCardX is a Stream lit web application designed to effortlessly extract data from business cards using Optical Character Recognition (OCR) technology.
 - With BizCardX, users can easily upload images of business cards, and the application leverages the powerful easyOCR library to extract pertinent information from the cards.
 - The extracted data is then presented in a user-friendly format and can be stored in a SQL database for future reference and management.
## libraries 
 - Streamlit
 - Pandas
 - easyOCR
 - PIL
 - cv2
 - pymysql
## Upload & Extract
This pivotal section empowers users to upload images of business cards. Once an image is uploaded, BizCardX undertakes the image processing using the easyOCR library to extract essential details from the card. The extracted information encompasses:
Company name Card holder's name Designation Mobile number Email address Website URL Area City State Pin code Image of the card.
## Modify
The modify section of BizCardX allows users to interact with the data extracted from business cards. Through a user-friendly dropdown menu, users can select specific entries from the database. This selection enables them to either update or delete the chosen entry. Any modifications performed are promptly saved in the database.
