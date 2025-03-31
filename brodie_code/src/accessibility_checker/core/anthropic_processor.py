from typing import Dict, Any, List
from ..core.document import AccessibilityDocumentProcessor
from ..utils.anthropic_client import AnthropicClient, create_anthropic_client
from ..core.enhance import AccessibilityViolation


class AnthropicEnhancedProcessor(AccessibilityDocumentProcessor):
    """Enhanced document processor that uses Claude for additional analysis."""

    def __init__(self, pdf_path: str, anthropic_client: AnthropicClient, **
        kwargs) ->None:
        super().__init__(pdf_path, **kwargs)
        self.anthropic_client = anthropic_client
        self.ai_suggestions: Dict[int, List[Dict]] = {}

    def analyze_with_claude(self) ->Dict[str, Any]:
        """
        Perform enhanced accessibility analysis using Claude.
        
        Returns:
            Dict containing Claude's analysis and suggestions
        """
        text_content = []
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            if text.strip():
                text_content.append(f'Page {page_num + 1}:\n{text}\n')
        full_text = '\n'.join(text_content)
        analysis = self.anthropic_client.analyze_document(full_text)
        if self.violations:
            suggestions = self.anthropic_client.suggest_improvements(
                full_text, [v.__dict__ for v in self.violations])
            analysis['improvement_suggestions'] = suggestions.get('suggestions'
                , '')
        return analysis

    def export_enhanced_report(self, output_path: str):
        """
        Export enhanced accessibility report including Claude's analysis.
        
        Args:
            output_path: Path where to save the report
        """
        report = {'document_structure': {'pages': len(self.doc),
            'heading_hierarchy': self._analyze_heading_hierarchy(),
            'tables': len(self.tables), 'reading_order': self.
            _export_reading_order()}, 'corrections': self.corrections,
            'tables': self._export_table_structures(), 'violations': [v.
            __dict__ for v in self.violations]}
        claude_analysis = self.analyze_with_claude()
        report['ai_analysis'] = claude_analysis
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)


def create_enhanced_processor(pdf_path: str, api_key: str=None, model: str=
    None, **kwargs) ->AnthropicEnhancedProcessor:
    """
    Create an instance of AnthropicEnhancedProcessor.
    
    Args:
        pdf_path: Path to PDF file
        api_key: Optional Anthropic API key
        model: Optional model name
        **kwargs: Additional arguments for AccessibilityDocumentProcessor
        
    Returns:
        Configured AnthropicEnhancedProcessor instance
    """
    anthropic_client = create_anthropic_client(api_key, model)
    return AnthropicEnhancedProcessor(pdf_path, anthropic_client, **kwargs)
