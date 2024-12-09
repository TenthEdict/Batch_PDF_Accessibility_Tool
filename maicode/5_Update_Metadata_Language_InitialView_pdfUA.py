"""
Author: Mai Yamamoto
Drafted with assistance by ChatGPT 4o
Date of Version: 12/09/2024

Description: This program is step two of two in a series that will batch edit the metadata of pdfs.
Specifically, this program batch revises the title and author information based off the metadata spreadsheet,
and the reading language is set to English, the initial view is set to the document title, 
mark the pdf as 'tagged', and the pdfUA-ID.xmp is appended. 

Important: To run this program, the spreadsheet must be completed with the Title and Author information. 
This can be done manually or transfer the relevant information from a separate, ready-made spreadsheet,
such as a batch revise spreadsheet for a collection/series. 
If transferring, an AI agent can readily transfer the information into this current spreadsheet. 

Remember to change the pdf_folder and tiff_folder locations.

Required libraries: PyPDF2; pikepdf
"""
import os
import pandas as pd
import pikepdf

# Step 1: Update PDF Metadata using pikepdf
def update_pdf_metadata(pdf_path, title, authors):
    title = str(title).strip('"') if pd.notna(title) else ''
    authors = ";".join([str(author).strip('"') for author in authors if pd.notna(author)])

    print(f"Updating metadata for: {pdf_path}")
    print(f"Title: {title}")
    print(f"Authors: {authors}")

    # Open the PDF and update its metadata
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        # Update classic metadata dictionary
        docinfo = pdf.docinfo
        docinfo['/Title'] = title
        docinfo['/Author'] = authors

        # Create XMP metadata
        xmp_metadata = f"""
        <x:xmpmeta xmlns:x="adobe:ns:meta/" xmlns:dc="http://purl.org/dc/elements/1.1/">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                <rdf:Description rdf:about=""
                    xmlns:dc="http://purl.org/dc/elements/1.1/"
                    xmlns:xmp="http://ns.adobe.com/xap/1.0/">
                    <dc:title>
                        <rdf:Alt>
                            <rdf:li xml:lang="x-default">{title}</rdf:li>
                        </rdf:Alt>
                    </dc:title>
                    <dc:creator>
                        <rdf:Seq>
                            {"".join(f"<rdf:li>{author}</rdf:li>" for author in authors.split(";"))}
                        </rdf:Seq>
                    </dc:creator>
                </rdf:Description>
            </rdf:RDF>
        </x:xmpmeta>
        """
        # Embed the XMP metadata
        pdf.Root.Metadata = pikepdf.Stream(pdf, xmp_metadata.encode('utf-8'))
        pdf.save(pdf_path)
    print(f"Metadata updated for: {pdf_path}")

# Step 2: Set Language
def set_pdf_language(pdf_path, language="en-US"):
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        pdf.Root['/Lang'] = pikepdf.String(language)
        pdf.save(pdf_path)
        print(f"Set reading language to {language} for: {pdf_path}")

# Step 3: Set Initial View to Show Document Title
def set_initial_view_title(pdf_path):
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        if '/ViewerPreferences' not in pdf.Root:
            pdf.Root['/ViewerPreferences'] = pdf.make_indirect({})
        pdf.Root['/ViewerPreferences']['/DisplayDocTitle'] = True
        pdf.save(pdf_path)
        print(f"Set Initial View to show document title for: {pdf_path}")

# Step 4: Mark PDFs as Tagged
def mark_pdf_as_tagged(pdf_path):
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        if '/MarkInfo' not in pdf.Root:
            pdf.Root['/MarkInfo'] = pdf.make_indirect({})
        pdf.Root['/MarkInfo']['/Marked'] = True  # Indicate that the document is tagged
        pdf.save(pdf_path)
    print(f"Marked as tagged PDF: {pdf_path}")

# Step 5: Append XMP Metadata to PDFs (Preserve Existing Metadata)
def append_xmp_to_multiple_pdfs(pdf_folder, xmp_file):
    if not os.path.exists(xmp_file):
        print(f"Error: The specified XMP file '{xmp_file}' does not exist.")
        return

    # Read the XMP content once (as a string)
    with open(xmp_file, 'r', encoding='utf-8') as xmp:
        xmp_metadata = xmp.read()

    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, pdf_file)

            with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
                # Get existing metadata from the PDF
                existing_metadata = pdf.Root.Metadata.read_bytes().decode('utf-8') if pdf.Root.Metadata else ''

                # Combine existing metadata with the new XMP metadata
                combined_metadata = f"""
                <x:xmpmeta xmlns:x="adobe:ns:meta/" xmlns:dc="http://purl.org/dc/elements/1.1/">
                    {existing_metadata}
                    {xmp_metadata}
                </x:xmpmeta>
                """
                # Write the combined metadata back to the PDF
                pdf.Root.Metadata = pikepdf.Stream(pdf, combined_metadata.encode('utf-8'))
                pdf.save(pdf_path)

            print(f"Appended and preserved metadata for: {pdf_file}")

# Batch Process Function to Combine All Steps
def batch_process_pdfs(excel_file, folder_path, xmp_file):
    # Step 1: Update Metadata
    df = pd.read_excel(excel_file)
    for index, row in df.iterrows():
        filename = row['File Name']
        title = row['Title']
        authors = row.iloc[2:17].values  # Columns C-Q
        pdf_path = os.path.join(folder_path, filename)
        if os.path.exists(pdf_path):
            update_pdf_metadata(pdf_path, title, authors)
        else:
            print(f"PDF not found: {pdf_path}")

    # Step 2: Process PDFs in Folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            set_pdf_language(pdf_path, language="en-US")
            set_initial_view_title(pdf_path)
            mark_pdf_as_tagged(pdf_path)  # Mark each PDF as tagged

    # Step 3: Append XMP Metadata (preserving existing fields)
    append_xmp_to_multiple_pdfs(folder_path, xmp_file)

# Specify the Excel file, PDF folder, and XMP file
excel_file = '/Users/maiyamamoto/Desktop/Working/3_Converted/metadata.xlsx'
pdf_folder = '/Users/maiyamamoto/Desktop/Working/3_Converted'
xmp_file = '/Users/maiyamamoto/Desktop/Working/pdfUA-ID.xmp'

# Run the batch process
batch_process_pdfs(excel_file, pdf_folder, xmp_file)
