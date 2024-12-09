"""
Author: Mai Yamamoto
Drafted with assistance by ChatGPT 4o
Date of Version: 12/09/2024

Description: This program is step one of two in a series that will batch edit the metadata of pdfs.
Specifically, this program creates a spreadsheet for metadata batch processing.
The first columns is the 'File name', followed by 'Title', and fifteen "Author" columns. 

Important: The spreadsheet must be completed with the Title and Author information. 
This can be done manually or transfer the relevant information from a separate, ready-made spreadsheet,
such as a batch revise spreadsheet for a collection/series. 
If transferring, an AI agent can readily transfer the information into this current spreadsheet. 

Remember to change the pdf_folder and tiff_folder locations.

Required libraries: pandas; openpyxl
"""

import pandas as pd
import os

# Function to write filenames to Excel with correct headers
def batch_process_pdfs(excel_file, pdf_folder):
    # Create a dataframe to store the PDF details
    df = pd.DataFrame(columns=['File Name', 'Title', 'Author 1', 'Author 2', 'Author 3', 'Author 4', 
                               'Author 5', 'Author 6', 'Author 7', 'Author 8', 'Author 9', 
                               'Author 10', 'Author 11', 'Author 12', 'Author 13', 'Author 14', 'Author 15'])

    # Loop through each PDF file in the folder
    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            # Add the filename to the first column
            df = df._append({'File Name': filename}, ignore_index=True)
    
    # Write the dataframe to an Excel file
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, startrow=0)  # Write headers in row 1 (startrow=0)

# Example usage
pdf_folder = '/Users/maiyamamoto/Desktop/Working/3_Converted'  # Replace with your folder path
excel_file = '/Users/maiyamamoto/Desktop/Working/3_Converted/metadata.xlsx'  # Replace with your output file path

batch_process_pdfs(excel_file, pdf_folder)
