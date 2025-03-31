import os
import logging
from typing import Dict, Any, Optional, List
import anthropic
from dataclasses import dataclass
from ..utils.retry import RetryHandler, RetryConfig, RetryableError


class AnthropicAPIError(RetryableError):
    """Error during Anthropic API operations."""
    pass


@dataclass
class AnthropicConfig:
    """Configuration for Anthropic API client."""
    api_key: str
    model: str = 'claude-3-opus-20240229'
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30


class AnthropicClient:
    """Client for interacting with Anthropic's API."""

    def __init__(self, config: AnthropicConfig, retry_handler: Optional[
        RetryHandler]=None) ->None:
        """
        Initialize Anthropic client.
        
        Args:
            config: AnthropicConfig object containing API settings
            retry_handler: Optional retry handler for error recovery
        """
        self.config = config
        self.client = anthropic.Client(api_key=config.api_key)
        self.retry_handler = retry_handler or RetryHandler(RetryConfig())
        self.logger = logging.getLogger(__name__)

    @RetryHandler(RetryConfig())((AnthropicAPIError,))
    def analyze_document(self, text: str, **kwargs) ->Dict[str, Any]:
        """
        Analyze document content using Claude.
        
        Args:
            text: Document text to analyze
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dict containing Claude's analysis
        """
        try:
            response = self.client.messages.create(model=self.config.
                model, max_tokens=self.config.max_tokens, temperature=self.
                config.temperature, messages=[{'role': 'user', 'content':
                text}], **kwargs)
            return {'analysis': response.content[0].text, 'model': response
                .model, 'usage': response.usage}
        except Exception as e:
            self.logger.error(f'Anthropic API error: {str(e)}')
            raise AnthropicAPIError(f'Failed to analyze document: {str(e)}')

    @RetryHandler(RetryConfig())((AnthropicAPIError,))
    def suggest_improvements(self, original_text: str,
        accessibility_issues: List[Dict]) ->Dict[str, Any]:
        """
        Get suggestions for improving document accessibility.
        
        Args:
            original_text: Original document text
            accessibility_issues: List of detected accessibility issues
            
        Returns:
            Dict containing improvement suggestions
        """
        try:
            prompt = f"""Please analyze this text and suggest accessibility improvements:

Text: {original_text}

Detected Issues:
{self._format_issues(accessibility_issues)}

Please provide specific suggestions to improve accessibility while maintaining the document's meaning and structure."""
            response = self.client.messages.create(model=self.config.
                model, max_tokens=self.config.max_tokens, temperature=self.
                config.temperature, messages=[{'role': 'user', 'content':
                prompt}])
            return {'suggestions': response.content[0].text, 'model':
                response.model, 'usage': response.usage}
        except Exception as e:
            self.logger.error(
                f'Error getting improvement suggestions: {str(e)}')
            raise AnthropicAPIError(f'Failed to get suggestions: {str(e)}')

    def _format_issues(self, issues: List[Dict]) ->str:
        """Format accessibility issues for prompt."""
        formatted = []
        for issue in issues:
            formatted.append(
                f"""- Type: {issue.get('type', 'Unknown')}
  Location: {issue.get('location', 'Unknown')}
  Description: {issue.get('description', 'No description')}"""
                )
        return '\n'.join(formatted)


def create_anthropic_client(api_key: Optional[str]=None, model: Optional[
    str]=None, retry_handler: Optional[RetryHandler]=None) ->AnthropicClient:
    """
    Create an instance of AnthropicClient with configuration.
    
    Args:
        api_key: Optional API key (defaults to ANTHROPIC_API_KEY env var)
        model: Optional model name
        retry_handler: Optional retry handler
        
    Returns:
        Configured AnthropicClient instance
    """
    config = AnthropicConfig(api_key=api_key or os.getenv(
        'ANTHROPIC_API_KEY', ''), model=model or 'claude-3-opus-20240229')
    if not config.api_key:
        raise ValueError(
            'Anthropic API key not provided or found in environment')
    return AnthropicClient(config, retry_handler)
