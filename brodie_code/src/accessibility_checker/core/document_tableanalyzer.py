class TableAnalyzer:
    def detect_tables(self) ->None:
        for page_num in range(len(self.doc)):
            page_elements = [te for te in self.text_elements if te and te.
                page_num == page_num and hasattr(te, 'x') and hasattr(te, 'y') and
                hasattr(te, 'width')]
            if not page_elements:
                continue
            rows = defaultdict(list)
            for element in page_elements:
                try:
                    row_key = round(element.y / 5) * 5
                    rows[row_key].append(element)
                except (TypeError, AttributeError):
                    continue
            current_table = None
            consecutive_row_count = 0
            for y, row_elements in sorted(rows.items()):
                if len(row_elements) >= 2:
                    try:
                        row_elements.sort(key=lambda e: e.x)
                        spaces = []
                        for i in range(len(row_elements) - 1):
                            try:
                                current = row_elements[i]
                                next_elem = row_elements[i + 1]
                                if all(hasattr(current, attr) for attr in ['x',
                                    'width']) and hasattr(next_elem, 'x'):
                                    space = next_elem.x - (current.x + current.
                                        width)
                                    spaces.append(space)
                            except (AttributeError, TypeError):
                                continue
                        is_table_row = False
                        if spaces:
                            space_range = max(spaces) - min(spaces)
                            is_table_row = space_range < 10
                        if not is_table_row and row_elements:
                            try:
                                mean_width = np.mean([el.width for el in
                                    row_elements if hasattr(el, 'width')])
                                is_table_row = any(hasattr(e, 'width') and e.
                                    width > mean_width * 1.5 for e in row_elements)
                            except (AttributeError, TypeError):
                                pass
                        if is_table_row:
                            if not current_table:
                                current_table = TableStructure()
                                consecutive_row_count = 0
                            consecutive_row_count += 1
                            current_table.rows.append(row_elements)
                        elif current_table and consecutive_row_count >= 2:
                            self._finalize_table(current_table)
                            self.tables.append(current_table)
                            current_table = None
                        else:
                            current_table = None
                            consecutive_row_count = 0
                    except Exception as e:
                        self.logger.warning(
                            f'Error processing row in table detection: {str(e)}')
                        continue

