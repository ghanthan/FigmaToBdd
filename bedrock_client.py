"""
AWS Bedrock Client for generating BDD scenarios from Figma design data
"""

import boto3
import json
import ssl
import certifi
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError, BotoCoreError


class BedrockClient:
    """Client for interacting with AWS Bedrock to generate BDD scenarios"""

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str,
                 region: str = "us-east-1", verify_ssl: bool = True):
        """
        Initialize Bedrock client

        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region: AWS region
            verify_ssl: Whether to verify SSL certificates
        """
        self.region = region
        self.verify_ssl = verify_ssl

        # Configure SSL
        if not verify_ssl:
            ssl._create_default_https_context = ssl._create_unverified_context

        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region,
                verify=verify_ssl
            )
        except Exception as e:
            raise Exception(f"Failed to initialize Bedrock client: {str(e)}")

    def generate_bdd_scenarios(self, figma_data: Dict[str, Any]) -> str:
        """
        Generate BDD scenarios from Figma design data

        Args:
            figma_data: Processed Figma design data

        Returns:
            Generated BDD scenarios as string
        """
        prompt = self._create_bdd_prompt(figma_data)

        try:
            response = self._invoke_claude(prompt)
            return response
        except Exception as e:
            raise Exception(f"Failed to generate BDD scenarios: {str(e)}")

    def _create_bdd_prompt(self, figma_data: Dict[str, Any]) -> str:
        """
        Create a prompt for BDD scenario generation

        Args:
            figma_data: Processed Figma design data

        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are a Business Analyst and Test Automation expert. Based on the following Figma design data, 
generate comprehensive BDD (Behavior Driven Development) scenarios in Gherkin format.

Design Data:
{json.dumps(figma_data, indent=2)}

Please analyze the design and create BDD scenarios that cover:

1. User Interface Elements:
   - All interactive elements (buttons, forms, links)
   - Text content and labels
   - Navigation elements
   - Visual components

2. User Journeys:
   - Primary user flows
   - Secondary user flows
   - Error scenarios
   - Edge cases

3. Functional Requirements:
   - Form validations
   - Data entry scenarios
   - Search functionality
   - Filter and sorting features

Generate the scenarios in proper Gherkin format with:
- Feature descriptions
- Background steps (if applicable)
- Scenario outlines with examples
- Given-When-Then steps
- Tags for categorization

Focus on creating scenarios that are:
- Testable and measurable
- Clear and understandable
- Comprehensive but not redundant
- Aligned with user experience goals

Format the output as a complete BDD document with proper Gherkin syntax.
"""
        return prompt

    def _invoke_claude(self, prompt: str, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> str:
        """
        Invoke Claude model via Bedrock

        Args:
            prompt: Input prompt
            model_id: Claude model ID

        Returns:
            Generated response
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "top_p": 0.9
        }

        try:
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            raise Exception(f"Bedrock API error ({error_code}): {error_message}")
        except Exception as e:
            raise Exception(f"Unexpected error calling Bedrock: {str(e)}")

    def generate_test_scenarios(self, figma_data: Dict[str, Any], scenario_type: str = "functional") -> str:
        """
        Generate specific types of test scenarios

        Args:
            figma_data: Processed Figma design data
            scenario_type: Type of scenarios (functional, ui, accessibility, performance)

        Returns:
            Generated scenarios
        """
        specialized_prompts = {
            "functional": self._create_functional_test_prompt(figma_data),
            "ui": self._create_ui_test_prompt(figma_data),
            "accessibility": self._create_accessibility_test_prompt(figma_data),
            "performance": self._create_performance_test_prompt(figma_data)
        }

        prompt = specialized_prompts.get(scenario_type, self._create_bdd_prompt(figma_data))

        try:
            return self._invoke_claude(prompt)
        except Exception as e:
            raise Exception(f"Failed to generate {scenario_type} scenarios: {str(e)}")

    def _create_functional_test_prompt(self, figma_data: Dict[str, Any]) -> str:
        """Create prompt for functional test scenarios"""
        return f"""
Generate functional BDD test scenarios for the following UI design:

{json.dumps(figma_data, indent=2)}

Focus on:
- Business logic validation
- Data flow testing
- Integration points
- Workflow completion
- Error handling

Use Gherkin syntax with clear Given-When-Then steps.
"""

    def _create_ui_test_prompt(self, figma_data: Dict[str, Any]) -> str:
        """Create prompt for UI test scenarios"""
        return f"""
Generate UI-focused BDD test scenarios for the following design:

{json.dumps(figma_data, indent=2)}

Focus on:
- Element visibility and positioning
- Responsive design behavior
- Visual consistency
- Interaction feedback
- Layout validation

Use Gherkin syntax with visual verification steps.
"""

    def _create_accessibility_test_prompt(self, figma_data: Dict[str, Any]) -> str:
        """Create prompt for accessibility test scenarios"""
        return f"""
Generate accessibility-focused BDD test scenarios for the following design:

{json.dumps(figma_data, indent=2)}

Focus on:
- WCAG 2.1 compliance
- Keyboard navigation
- Screen reader compatibility
- Color contrast
- Focus management
- Alt text for images

Use Gherkin syntax with accessibility-specific verification steps.
"""

    def _create_performance_test_prompt(self, figma_data: Dict[str, Any]) -> str:
        """Create prompt for performance test scenarios"""
        return f"""
Generate performance-focused BDD test scenarios for the following design:

{json.dumps(figma_data, indent=2)}

Focus on:
- Page load times
- Image optimization
- API response times
- Resource loading
- Memory usage
- Mobile performance

Use Gherkin syntax with performance metrics validation.
"""
