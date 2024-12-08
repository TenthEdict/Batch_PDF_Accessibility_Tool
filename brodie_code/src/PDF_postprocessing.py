"""
Author: 
Brodie Schipp

Code Inspo:
Copilot

Date:
11/04/2024

Description:
This script is for batchable post-processing
to set tab order by document structure and set the 
language to english after a PDF has been remediated.
It also sets the metadata to indicate the PDF-UA xmp
identifier, as well as mark it as a tagged document. 

It will print out if a given file is successful or not.

Paths to Change:
- input_directory
- output_directory
- xmp_path

Required libraries: fitz 
Required package: PyMuPDF
"""

import os
import pikepdf
from libxmp import XMPFiles, XMPMeta, consts

def process_pdf(input_dir, output_dir, xmp_path):
    # Load the XMP metadata from a file
    with open(xmp_path, "rb") as xmp_file:
        xmp_data = xmp_file.read()

    # Create an XMPMeta object from the XMP data
    xmp_meta = XMPMeta(xmp_str=xmp_data.decode('utf-8'))

    # Iterate over all PDF files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            # Open the PDF file
            pdf = pikepdf.open(input_path)

            # Check for existing title in the PDF metadata
            existing_title = pdf.docinfo.get('/Title', None)
            if existing_title:
                # Set the title in the XMP metadata
                xmp_meta.set_property(consts.XMP_NS_DC, 'title', str(existing_title))

            # Set the document language to English
            pdf.Root[pikepdf.Name('/Lang')] = pikepdf.String('en-US')

            # Mark the document as a tagged PDF
            pdf.Root[pikepdf.Name('/MarkInfo')] = pikepdf.Dictionary()
            pdf.Root.MarkInfo[pikepdf.Name('/Marked')] = True

            # Set the tab order by document structure
            for page in pdf.pages:
                page[pikepdf.Name('/Tabs')] = pikepdf.Name('/S')

            # Attach the XMP metadata to the PDF
            xmpfile = XMPFiles(file_path=input_path, open_forupdate=True)
            xmpfile.put_xmp(xmp_meta)
            xmpfile.close_file()

            # Ensure the Metadata entry is a stream
            if '/Metadata' in pdf.Root:
                del pdf.Root[pikepdf.Name('/Metadata')]
            pdf.Root[pikepdf.Name('/Metadata')] = pdf.make_stream(xmp_meta.serialize_to_str().encode('utf-8'))

            # Save the updated PDF to the output directory
            pdf.save(output_path)

# Example usage
input_directory = '/Volumes/ePubs/Accessibility_Project/p_series/pmrg/02_postprocess'
output_directory = '/Volumes/ePubs/Accessibility_Project/p_series/pmrg/03_check'
xmp_metadata_path = '/Volumes/ePubs/Accessibility_Project/pdfUA-ID.xmp'

# Create output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

process_pdf(input_directory, output_directory, xmp_metadata_path)
