from pathlib import Path
from pikepdf import Pdf, Name, String, Dictionary
from libxmp import XMPFiles, XMPMeta, consts
import logging

class PDFPostProcessor:
    def __init__(self, config: dict, retry_handler):
        self.config = config
        self.retry_handler = retry_handler
        self.xmp_path = config.get('xmp_metadata_path')
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

    def process_pdf(self, input_path: str, output_path: str) -> bool:
        """Process PDF file with libxmp for metadata handling."""
        try:
            print(f"\nProcessing {input_path}")
            
            # Load the XMP metadata from template
            with open(self.xmp_path, "rb") as xmp_file:
                xmp_data = xmp_file.read()
            
            # Create XMPMeta object from template
            xmp_meta = XMPMeta(xmp_str=xmp_data.decode('utf-8'))
            
            with Pdf.open(input_path) as pdf:
                print("PDF opened successfully")
                print("PDF Root keys:", [str(k) for k in pdf.Root.keys()])
                
                # Set language
                print("Setting language...")
                pdf.Root[Name('/Lang')] = String('en-US')
                
                # Set MarkInfo
                print("Setting MarkInfo...")
                mark_info = Dictionary()
                mark_info[Name('/Marked')] = True
                pdf.Root[Name('/MarkInfo')] = mark_info
                print("MarkInfo created and set")
                
                # Set tab order
                print("Setting tab order...")
                for page in pdf.pages:
                    page[Name('/Tabs')] = Name('/S')
                
                # Handle document info
                print("Setting document info...")
                if hasattr(pdf, 'docinfo') and pdf.docinfo.get('/Title'):
                    xmp_meta.set_property(
                        consts.XMP_NS_DC,
                        'title',
                        str(pdf.docinfo['/Title'])
                    )
                
                # Update XMP metadata
                print("Creating metadata...")
                try:
                    # First update using XMPFiles
                    xmpfile = XMPFiles(file_path=input_path, open_forupdate=True)
                    xmpfile.put_xmp(xmp_meta)
                    xmpfile.close_file()
                    
                    # Then ensure it's properly set in the PDF
                    if Name('/Metadata') in pdf.Root:
                        del pdf.Root[Name('/Metadata')]
                    
                    pdf.Root[Name('/Metadata')] = pdf.make_stream(
                        xmp_meta.serialize_to_str().encode('utf-8'),
                        {
                            Name('/Type'): Name('/Metadata'),
                            Name('/Subtype'): Name('/XML')
                        }
                    )
                    print("Metadata updated successfully")
                    
                except Exception as meta_error:
                    print(f"Metadata error: {str(meta_error)}")
                    print("Continuing without metadata modification...")
                
                # Save the PDF
                print(f"Saving PDF to {output_path}...")
                pdf.save(output_path)
                print(f"Successfully saved to {output_path}")
            
            return True
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            raise

    def process_tagged_batch(self, tagged_dir: str, final_dir: str) -> dict:
        """Process batch of tagged PDFs."""
        results = {}
        tagged_path = Path(tagged_dir)
        final_path = Path(final_dir)
        
        final_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\nProcessing PDFs from: {tagged_path}")
        print(f"Saving results to: {final_path}")
        
        pdf_files = list(tagged_path.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {tagged_path}")
            return results
        
        for pdf_file in pdf_files:
            output_path = final_path / f"{pdf_file.stem}_ua{pdf_file.suffix}"
            try:
                success = self.process_pdf(
                    input_path=str(pdf_file),
                    output_path=str(output_path)
                )
                results[pdf_file.name] = success
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {str(e)}")
                results[pdf_file.name] = False
        
        print("\nProcessing Summary:")
        success_count = sum(1 for success in results.values() if success)
        print(f"Total files processed: {len(results)}")
        print(f"Successfully processed: {success_count}")
        print(f"Failed: {len(results) - success_count}")
        
        return results