class ProcessingError(Exception):
    """Exception raised when processing a document fails."""
    pass

class TextExtractor:
    def extract_text_with_positions(self) ->None:
        """Extract text with improved error handling and OCR triggering."""
        total_blocks = 0
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text_dict = page.get_text('dict')
            if not text_dict or 'blocks' not in text_dict:
                self.logger.warning(f'No text blocks found on page {page_num + 1}')
                continue
            page_blocks = 0
            for block in text_dict['blocks']:
                if 'lines' not in block:
                    continue
                for line in block['lines']:
                    if 'spans' not in line:
                        continue
                    for span in line.get('spans', []):
                        if self._process_span(span, page_num):
                            page_blocks += 1
            if page_blocks == 0:
                self.logger.warning(
                    f'No processable text found on page {page_num + 1}')
            total_blocks += page_blocks
        if total_blocks == 0:
            self.logger.error('No text content extracted from document')
            if self.enable_ocr and self.ocr_processor:
                self.logger.info('Attempting OCR processing')
                self._force_ocr_processing()
            else:
                raise ProcessingError(
                    'Document appears to be scanned/image-based and OCR is not enabled'
                    )

    def analyze_reading_order(self) ->None:
        """Analyze and assign reading order to document elements with error handling."""
        try:
            for page_num in range(len(self.doc)):
                page_elements = [te for te in self.text_elements if te and te.
                    page_num == page_num and all(hasattr(te, attr) for attr in
                    ['x', 'y', 'width', 'height'])]
                reading_order = 0
                for level in range(1, 7):
                    headings = [te for te in page_elements if hasattr(te,
                        'heading_level') and te.heading_level == level]
                    for heading in sorted(headings, key=lambda e: (e.y, e.x)):
                        heading.reading_order = reading_order
                        reading_order += 1
                if self.tables:
                    for table in self.tables:
                        if table and table.rows:
                            for row in table.rows:
                                if row:
                                    for cell in row:
                                        if cell and hasattr(cell, 'reading_order'):
                                            cell.reading_order = reading_order
                                            reading_order += 1
                remaining = [te for te in page_elements if (not hasattr(te,
                    'heading_level') or te.heading_level is None) and (not
                    hasattr(te, 'table_cell') or te.table_cell is None)]
                if remaining:
                    column_threshold = 50
                    columns = defaultdict(list)
                    for element in remaining:
                        try:
                            column_key = round(element.x / column_threshold
                                ) * column_threshold
                            columns[column_key].append(element)
                        except (AttributeError, TypeError):
                            continue
                    for x in sorted(columns.keys()):
                        column_elements = columns[x]
                        try:
                            for element in sorted(column_elements, key=lambda e:
                                e.y):
                                if hasattr(element, 'reading_order'):
                                    element.reading_order = reading_order
                                    reading_order += 1
                        except (AttributeError, TypeError) as e:
                            self.logger.warning(
                                f'Error sorting column elements: {str(e)}')
                            continue
        except Exception as e:
            self.logger.error(f'Error in analyze_reading_order: {str(e)}')
            raise

