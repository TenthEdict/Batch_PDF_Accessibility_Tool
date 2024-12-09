from typing import Dict, List, Optional
import os
from pathlib import Path
from pikepdf import Pdf, Name, String, Dictionary, Stream
import sys

# Handle imports whether run as script or module
try:
    # When run as module
    from ..utils.retry import RetryHandler, RetryConfig, ProcessingError
except ImportError:
    # When run as script
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from accessibility_checker.utils.retry import RetryHandler, RetryConfig, ProcessingError

class PDFPostProcessor:
    def __init__(self, config: dict, retry_handler: RetryHandler):
        self.config = config
        self.retry_handler = retry_handler
        self.xmp_path = config.get('xmp_metadata_path')

    def _create_metadata_stream(self, pdf: Pdf, xmp_data: bytes) -> Stream:
        """Create a metadata stream with proper dictionary entries."""
        metadata_dict = {
            Name('/Type'): Name('/Metadata'),
            Name('/Subtype'): Name('/XML')
        }
        return pdf.make_stream(xmp_data, metadata_dict)

    def _traverse_structure_tree(self, node) -> Optional[str]:
        """Recursively traverse the structure tree looking for H1."""
        try:
            if isinstance(node, Dictionary):
                # Check if this is an H1 element
                if node.get(Name('/S')) == Name('/H1'):
                    # Try to get text from different possible locations
                    if Name('/T') in node:
                        return str(node[Name('/T')])
                    elif Name('/K') in node:
                        k = node[Name('/K')]
                        if isinstance(k, String):
                            return str(k)
                        elif isinstance(k, Dictionary) and Name('/MCID') in k:
                            page = k.get(Name('/Pg'))
                            if page and hasattr(page, 'get_text'):
                                text = page.get_text()
                                if text:
                                    return text.strip()

                # If not found, check children
                for key in node.keys():
                    value = node[key]
                    if isinstance(value, (Dictionary, list)):
                        result = self._traverse_structure_tree(value)
                        if result:
                            return result
            elif isinstance(node, list):
                for item in node:
                    result = self._traverse_structure_tree(item)
                    if result:
                        return result
                        
        except Exception as e:
            print(f"Warning: Error traversing node: {str(e)}")
        return None

    def _find_first_h1_text(self, pdf: Pdf) -> Optional[str]:
        """Find the first Heading Level 1 text in the document."""
        try:
            # Get the structure tree root
            struct_tree = pdf.Root.get(Name('/StructTreeRoot'))
            if not struct_tree:
                print("Warning: No structure tree found in PDF")
                return None

            return self._traverse_structure_tree(struct_tree)
            
        except Exception as e:
            print(f"Warning: Could not extract H1 title: {str(e)}")
            return None

    @RetryHandler(RetryConfig()).__call__((ProcessingError,))
    def process_pdf(self, input_path: str, output_path: str) -> bool:
        """
        Post-process a PDF file to ensure accessibility compliance.
        """
        try:
            print(f"Processing {input_path}")
            
            # Open and process PDF
            with Pdf.open(input_path) as pdf:
                print("PDF opened successfully")
                
                # Debug: Print PDF Root keys
                print("PDF Root keys:", [str(k) for k in pdf.Root.keys()])
                
                try:
                    # Set language first
                    print("Setting language...")
                    pdf.Root[Name('/Lang')] = String('en-US')
                    
                    # Mark as tagged PDF
                    print("Setting MarkInfo...")
                    mark_info = Dictionary({
                        Name('/Marked'): True
                    })
                    pdf.Root[Name('/MarkInfo')] = mark_info
                    
                    # Set tab order
                    print("Setting tab order...")
                    for page in pdf.pages:
                        page[Name('/Tabs')] = Name('/S')
                    
                    # Set basic PDF info
                    print("Setting document info...")
                    if not hasattr(pdf, 'docinfo'):
                        pdf.docinfo = Dictionary()
                    pdf.docinfo[Name('/Title')] = String(Path(input_path).stem)
                    
                    # Try creating metadata separately
                    print("Creating metadata...")
                    try:
                        with open(self.xmp_path, 'rb') as f:
                            xmp_data = f.read()
                            print(f"Read {len(xmp_data)} bytes of XMP data")
                            
                            # Create metadata dictionary
                            meta_dict = {
                                Name('/Type'): Name('/Metadata'),
                                Name('/Subtype'): Name('/XML')
                            }
                            
                            # Create the stream
                            metadata = pdf.make_stream(xmp_data, meta_dict)
                            print("Metadata stream created")
                            
                            # Set metadata in Root
                            pdf.Root[Name('/Metadata')] = metadata
                            print("Metadata set in Root")
                    except Exception as meta_error:
                        print(f"Metadata error: {str(meta_error)}")
                        raise
                    
                    print("Saving PDF...")
                    pdf.save(output_path)
                    print(f"Successfully saved to {output_path}")
                    
                except Exception as inner_error:
                    print(f"Inner error: {str(inner_error)}")
                    raise
                
            return True
            
        except Exception as e:
            raise ProcessingError(f"PDF post-processing failed: {str(e)}")
        
    def process_tagged_batch(self, tagged_dir: str, final_dir: str) -> Dict[str, bool]:
        """
        Process all tagged PDFs in the tagged directory.
        
        Args:
            tagged_dir: Directory containing tagged PDFs
            final_dir: Directory to save UA-compliant PDFs
            
        Returns:
            Dict mapping filenames to processing success status
        """
        results = {}
        tagged_path = Path(tagged_dir)
        final_path = Path(final_dir)
        
        # Create final directory if it doesn't exist
        final_path.mkdir(exist_ok=True)
        
        print(f"\nProcessing PDFs from: {tagged_path}")
        print(f"Saving results to: {final_path}")
        
        # Process each PDF in the tagged directory
        for pdf_file in tagged_path.glob("*.pdf"):
            output_path = final_path / f"{pdf_file.stem}_ua{pdf_file.suffix}"
            try:
                success = self.process_pdf(
                    input_path=str(pdf_file),
                    output_path=str(output_path)
                )
                results[pdf_file.name] = success
            except ProcessingError as e:
                print(f"Error processing {pdf_file.name}: {str(e)}")
                results[pdf_file.name] = False
                
        return results

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent.parent
    
    # Initialize configuration and processor
    config = {
        'xmp_metadata_path': str(project_root / "pdfUA-ID.xmp")
    }
    retry_handler = RetryHandler(RetryConfig())
    processor = PDFPostProcessor(config, retry_handler)
    
    # Define directories
    base_dir = project_root / "output"
    tagged_dir = base_dir / "tagged"
    final_dir = base_dir / "final"
    
    print(f"Project root: {project_root}")
    print(f"XMP template path: {config['xmp_metadata_path']}")
    
    # Process all tagged PDFs
    results = processor.process_tagged_batch(
        tagged_dir=str(tagged_dir),
        final_dir=str(final_dir)
    )
    
    # Print results
    print("\nPDF/UA Processing Results:")
    for filename, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {filename}")

if __name__ == "__main__":
    main()
