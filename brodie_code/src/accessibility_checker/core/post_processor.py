import os
from pathlib import Path
import pikepdf


def set_pdf_language(pdf_path, language='en-US') ->None:
    """Set PDF language."""
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        pdf.Root['/Lang'] = pikepdf.String(language)
        pdf.save(pdf_path)
        print(f'Set reading language to {language} for: {pdf_path}')


def set_initial_view_title(pdf_path) ->None:
    """Set initial view to show document title."""
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        if '/ViewerPreferences' not in pdf.Root:
            pdf.Root['/ViewerPreferences'] = pdf.make_indirect({})
        pdf.Root['/ViewerPreferences']['/DisplayDocTitle'] = True
        pdf.save(pdf_path)
        print(f'Set Initial View to show document title for: {pdf_path}')


def mark_pdf_as_tagged(pdf_path) ->None:
    """Mark PDF as tagged."""
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        if '/MarkInfo' not in pdf.Root:
            pdf.Root['/MarkInfo'] = pdf.make_indirect({})
        pdf.Root['/MarkInfo']['/Marked'] = True
        pdf.save(pdf_path)
        print(f'Marked as tagged PDF: {pdf_path}')


def ensure_fonts_embedded(pdf_path) ->None:
    """Ensure all fonts are embedded in the PDF."""
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        fonts_to_embed = set()
        for page in pdf.pages:
            if '/Resources' not in page:
                continue
            resources = page['/Resources']
            if '/Font' not in resources:
                continue
            font_dict = resources['/Font']
            for font_name, font_obj in font_dict.items():
                if not isinstance(font_obj, pikepdf.Dictionary):
                    continue
                is_embedded = False
                if '/FontDescriptor' in font_obj:
                    descriptor = font_obj['/FontDescriptor']
                    if any(f'/FontFile{i}' in descriptor for i in ['', '2',
                        '3']):
                        is_embedded = True
                if not is_embedded:
                    fonts_to_embed.add(font_name)
        if fonts_to_embed:
            print(
                f'Found {len(fonts_to_embed)} unembedded fonts in: {pdf_path}')
            for font_name in fonts_to_embed:
                try:
                    for page in pdf.pages:
                        if '/Resources' in page and '/Font' in page[
                            '/Resources']:
                            font_dict = page['/Resources']['/Font']
                            if font_name in font_dict:
                                font_obj = font_dict[font_name]
                                font_obj['/BaseFont'] = pikepdf.Name(
                                    '/Helvetica')
                                font_obj['/Subtype'] = pikepdf.Name('/Type1')
                                if '/FontDescriptor' in font_obj:
                                    del font_obj['/FontDescriptor']
                except Exception as e:
                    print(f'Warning: Could not process font {font_name}: {e}')
            pdf.save(pdf_path)
            print(f'Replaced unembedded fonts with Helvetica in: {pdf_path}')
        else:
            print(f'All fonts are properly embedded in: {pdf_path}')


def append_xmp_to_multiple_pdfs(pdf_folder, xmp_file) ->None:
    """Append XMP metadata to PDFs."""
    if not os.path.exists(xmp_file):
        print(f'Error: XMP file not found: {xmp_file}')
        return False
    print(f'\nReading XMP template from: {xmp_file}')
    try:
        with open(xmp_file, 'r', encoding='utf-8') as xmp:
            pdfua_content = xmp.read()
            start = pdfua_content.find('<rdf:Description')
            end = pdfua_content.find('</rdf:Description>', start)
            if start != -1 and end != -1:
                pdfua_description = pdfua_content[start:end + 20]
            else:
                print('Error: Could not find PDF/UA description in template')
                return False
    except Exception as e:
        print(f'Error reading XMP template: {e}')
        return False
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            print(f'\nProcessing: {pdf_path}')
            try:
                with pikepdf.open(pdf_path, allow_overwriting_input=True
                    ) as pdf:
                    existing_metadata = ''
                    if pdf.Root.get('/Metadata'):
                        metadata_bytes = pdf.Root.Metadata.read_bytes().decode(
                            'utf-8')
                        start = metadata_bytes.find('<rdf:Description')
                        if start != -1:
                            end = metadata_bytes.find('</rdf:Description>',
                                start)
                            if end != -1:
                                existing_metadata = metadata_bytes[start:
                                    end + 20]
                    metadata = f"""<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.2-c001 63.139439, 2010/09/27-13:37:26        ">
   <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      {existing_metadata}
      {pdfua_description}
   </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""
                    pdf.Root['/Metadata'] = pdf.make_stream(metadata.encode
                        ('utf-8'), {'/Type': pikepdf.Name('/Metadata'),
                        '/Subtype': pikepdf.Name('/XML')})
                    pdf.save()
                    print(f'Successfully processed: {pdf_file}')
            except Exception as e:
                print(f'Error processing {pdf_file}: {e}')
                return False
    return True


def batch_process_pdfs(tagged_dir, final_dir, xmp_path) ->None:
    """Process all PDFs in the tagged directory."""
    print(f'\nStarting batch processing...')
    print(f'Tagged directory: {tagged_dir}')
    print(f'Final directory: {final_dir}')
    os.makedirs(final_dir, exist_ok=True)
    for pdf_file in os.listdir(tagged_dir):
        if pdf_file.endswith('.pdf'):
            input_path = os.path.join(tagged_dir, pdf_file)
            output_filename = f'{Path(pdf_file).stem}_ua.pdf'
            output_path = os.path.join(final_dir, output_filename)
            print(f'\nProcessing: {pdf_file}')
            with pikepdf.open(input_path) as pdf:
                pdf.save(output_path)
            set_pdf_language(output_path)
            set_initial_view_title(output_path)
            mark_pdf_as_tagged(output_path)
            ensure_fonts_embedded(output_path)
    append_xmp_to_multiple_pdfs(final_dir, xmp_path)


def main() ->None:
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent.parent
    tagged_dir = project_root / 'output' / 'tagged'
    final_dir = project_root / 'output' / 'final'
    xmp_path = project_root / 'pdfUA-ID.xmp'
    print(f'Project root: {project_root}')
    print(f'Tagged directory: {tagged_dir}')
    print(f'Final directory: {final_dir}')
    print(f'XMP template path: {xmp_path}')
    if not tagged_dir.exists():
        print(f'Error: Tagged directory not found at {tagged_dir}')
        return
    if not xmp_path.exists():
        print(f'Error: XMP template not found at {xmp_path}')
        return
    batch_process_pdfs(str(tagged_dir), str(final_dir), str(xmp_path))


if __name__ == '__main__':
    main()
