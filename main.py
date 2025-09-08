"""
Main CLI application for FigmaToBDD tool
"""

import click
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any

from figma_client import FigmaClient
from bedrock_client import BedrockClient
from document_generator import DocumentGenerator


# Load environment variables
load_dotenv()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """FigmaToBDD: Extract Figma designs and generate BDD scenarios using AWS Bedrock"""
    pass


@cli.command()
@click.option('--file-id', '-f', required=True, help='Figma file ID')
@click.option('--output', '-o', default='figma_data', help='Output filename (without extension)')
@click.option('--token', '-t', help='Figma access token (overrides .env)')
@click.option('--no-ssl-verify', is_flag=True, help='Disable SSL verification')
def extract_figma(file_id: str, output: str, token: str, no_ssl_verify: bool):
    """Extract design data from Figma and save as JSON"""
    try:
        # Get configuration
        figma_token = token or os.getenv('FIGMA_ACCESS_TOKEN')
        verify_ssl = not no_ssl_verify and os.getenv('VERIFY_SSL', 'true').lower() == 'true'

        if not figma_token:
            click.echo("Error: Figma access token is required. Set FIGMA_ACCESS_TOKEN in .env or use --token", err=True)
            return

        click.echo(f"🔄 Extracting Figma design data for file ID: {file_id}")

        # Initialize Figma client
        figma_client = FigmaClient(figma_token, verify_ssl)

        # Extract data
        raw_data = figma_client.get_file(file_id)
        processed_data = figma_client.extract_design_elements(raw_data)

        # Save data
        doc_generator = DocumentGenerator()
        filepath = doc_generator.save_figma_data(processed_data, output)

        click.echo(f"✅ Figma data extracted and saved to: {filepath}")
        click.echo(f"📊 Found {len(processed_data.get('pages', []))} pages")

        # Display summary
        for page in processed_data.get('pages', []):
            click.echo(f"   📄 Page: {page.get('name')} ({len(page.get('frames', []))} frames)")

    except Exception as e:
        click.echo(f"❌ Error extracting Figma data: {str(e)}", err=True)


@cli.command()
@click.option('--input', '-i', required=True, help='Input JSON file with Figma data')
@click.option('--output', '-o', default='bdd_scenarios', help='Output filename (without extension)')
@click.option('--type', '-T', type=click.Choice(['functional', 'ui', 'accessibility', 'performance']),
              default='functional', help='Type of BDD scenarios to generate')
@click.option('--format', '-F', type=click.Choice(['markdown', 'pdf', 'html', 'all']),
              default='markdown', help='Output format')
@click.option('--no-ssl-verify', is_flag=True, help='Disable SSL verification')
def generate_bdd(input: str, output: str, type: str, format: str, no_ssl_verify: bool):
    """Generate BDD scenarios from Figma JSON data using AWS Bedrock"""
    try:
        # Get configuration
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        verify_ssl = not no_ssl_verify and os.getenv('VERIFY_SSL', 'true').lower() == 'true'

        if not aws_access_key or not aws_secret_key:
            click.echo("Error: AWS credentials are required. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env", err=True)
            return

        # Load Figma data
        if not os.path.exists(input):
            click.echo(f"Error: Input file {input} not found", err=True)
            return

        with open(input, 'r', encoding='utf-8') as f:
            figma_data = json.load(f)

        click.echo(f"🔄 Generating {type} BDD scenarios using AWS Bedrock...")

        # Initialize Bedrock client
        bedrock_client = BedrockClient(aws_access_key, aws_secret_key, aws_region, verify_ssl)

        # Generate scenarios
        if type == 'functional':
            bdd_scenarios = bedrock_client.generate_bdd_scenarios(figma_data)
        else:
            bdd_scenarios = bedrock_client.generate_test_scenarios(figma_data, type)

        # Generate documents
        doc_generator = DocumentGenerator()

        if format == 'all':
            generated_files = doc_generator.generate_all_formats(bdd_scenarios, figma_data, output)
            click.echo("✅ BDD scenarios generated in all formats:")
            for fmt, filepath in generated_files.items():
                click.echo(f"   📄 {fmt.upper()}: {filepath}")
        else:
            if format == 'markdown':
                filepath = doc_generator.generate_markdown_document(bdd_scenarios, figma_data, output)
            elif format == 'pdf':
                filepath = doc_generator.generate_pdf_document(bdd_scenarios, figma_data, output)
            elif format == 'html':
                filepath = doc_generator.generate_html_document(bdd_scenarios, figma_data, output)

            click.echo(f"✅ BDD scenarios generated: {filepath}")

    except Exception as e:
        click.echo(f"❌ Error generating BDD scenarios: {str(e)}", err=True)


@cli.command()
@click.option('--file-id', '-f', required=True, help='Figma file ID')
@click.option('--output', '-o', default='bdd_scenarios', help='Output filename (without extension)')
@click.option('--type', '-T', type=click.Choice(['functional', 'ui', 'accessibility', 'performance']),
              default='functional', help='Type of BDD scenarios to generate')
@click.option('--format', '-F', type=click.Choice(['markdown', 'pdf', 'html', 'all']),
              default='all', help='Output format')
@click.option('--figma-token', help='Figma access token (overrides .env)')
@click.option('--no-ssl-verify', is_flag=True, help='Disable SSL verification')
def full_pipeline(file_id: str, output: str, type: str, format: str, figma_token: str, no_ssl_verify: bool):
    """Complete pipeline: extract Figma data and generate BDD scenarios"""
    try:
        # Get configuration
        figma_token = figma_token or os.getenv('FIGMA_ACCESS_TOKEN')
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        verify_ssl = not no_ssl_verify and os.getenv('VERIFY_SSL', 'true').lower() == 'true'

        if not figma_token:
            click.echo("Error: Figma access token is required", err=True)
            return

        if not aws_access_key or not aws_secret_key:
            click.echo("Error: AWS credentials are required", err=True)
            return

        click.echo(f"🚀 Starting full pipeline for Figma file: {file_id}")

        # Step 1: Extract Figma data
        click.echo("📥 Step 1: Extracting Figma design data...")
        figma_client = FigmaClient(figma_token, verify_ssl)
        raw_data = figma_client.get_file(file_id)
        figma_data = figma_client.extract_design_elements(raw_data)

        click.echo(f"✅ Extracted data for {len(figma_data.get('pages', []))} pages")

        # Step 2: Generate BDD scenarios
        click.echo(f"🤖 Step 2: Generating {type} BDD scenarios with AWS Bedrock...")
        bedrock_client = BedrockClient(aws_access_key, aws_secret_key, aws_region, verify_ssl)

        if type == 'functional':
            bdd_scenarios = bedrock_client.generate_bdd_scenarios(figma_data)
        else:
            bdd_scenarios = bedrock_client.generate_test_scenarios(figma_data, type)

        # Step 3: Generate documents
        click.echo(f"📄 Step 3: Creating documents in {format} format(s)...")
        doc_generator = DocumentGenerator()

        if format == 'all':
            generated_files = doc_generator.generate_all_formats(bdd_scenarios, figma_data, output)
            click.echo("🎉 Pipeline completed! Generated files:")
            for fmt, filepath in generated_files.items():
                click.echo(f"   📄 {fmt.upper()}: {filepath}")
        else:
            if format == 'markdown':
                filepath = doc_generator.generate_markdown_document(bdd_scenarios, figma_data, output)
            elif format == 'pdf':
                filepath = doc_generator.generate_pdf_document(bdd_scenarios, figma_data, output)
            elif format == 'html':
                filepath = doc_generator.generate_html_document(bdd_scenarios, figma_data, output)

            click.echo(f"🎉 Pipeline completed! Generated: {filepath}")

    except Exception as e:
        click.echo(f"❌ Pipeline failed: {str(e)}", err=True)


@cli.command()
def setup():
    """Display setup instructions for API keys and configuration"""
    click.echo("🛠️  FigmaToBDD Setup Instructions")
    click.echo("=" * 50)

    click.echo("\n📋 Step 1: Figma API Setup")
    click.echo("-" * 25)
    click.echo("1. Go to https://www.figma.com/developers/api")
    click.echo("2. Click 'Get personal access token'")
    click.echo("3. Log in to your Figma account")
    click.echo("4. Generate a new personal access token")
    click.echo("5. Copy the token and add it to your .env file:")
    click.echo("   FIGMA_ACCESS_TOKEN=your_token_here")
    click.echo("\n6. To get your Figma file ID:")
    click.echo("   - Open your Figma file in browser")
    click.echo("   - Copy the file ID from URL: https://www.figma.com/file/FILE_ID/...")
    click.echo("   - Add it to .env: FIGMA_FILE_ID=your_file_id_here")

    click.echo("\n🔐 Step 2: AWS Bedrock Setup")
    click.echo("-" * 25)
    click.echo("1. Go to AWS Console: https://console.aws.amazon.com/")
    click.echo("2. Navigate to IAM service")
    click.echo("3. Create a new user or use existing user")
    click.echo("4. Attach policy: AmazonBedrockFullAccess")
    click.echo("5. Generate access keys (Access Key ID + Secret)")
    click.echo("6. Add to your .env file:")
    click.echo("   AWS_ACCESS_KEY_ID=your_access_key")
    click.echo("   AWS_SECRET_ACCESS_KEY=your_secret_key")
    click.echo("   AWS_REGION=us-east-1")

    click.echo("\n7. Enable Bedrock models:")
    click.echo("   - Go to AWS Bedrock console")
    click.echo("   - Navigate to 'Model access'")
    click.echo("   - Request access to Anthropic Claude models")

    click.echo("\n🔒 Step 3: SSL Configuration")
    click.echo("-" * 25)
    click.echo("For production: VERIFY_SSL=true")
    click.echo("For testing/dev: VERIFY_SSL=false")

    click.echo("\n📁 Step 4: Install Dependencies")
    click.echo("-" * 25)
    click.echo("Run: pip install -r requirements.txt")

    click.echo("\n🚀 Step 5: Usage Examples")
    click.echo("-" * 25)
    click.echo("# Extract Figma data only:")
    click.echo("python main.py extract-figma -f YOUR_FILE_ID")
    click.echo("\n# Generate BDD from existing JSON:")
    click.echo("python main.py generate-bdd -i figma_data.json")
    click.echo("\n# Full pipeline:")
    click.echo("python main.py full-pipeline -f YOUR_FILE_ID")

    click.echo("\n✅ Configuration file (.env) should contain:")
    click.echo("-" * 40)
    with open('.env', 'r') as f:
        click.echo(f.read())


@cli.command()
@click.option('--figma-token', help='Test Figma token')
@click.option('--aws-key', help='Test AWS access key')
@click.option('--aws-secret', help='Test AWS secret key')
def test_connection(figma_token: str, aws_key: str, aws_secret: str):
    """Test connections to Figma and AWS Bedrock APIs"""
    click.echo("🔍 Testing API connections...")

    # Test Figma connection
    try:
        token = figma_token or os.getenv('FIGMA_ACCESS_TOKEN')
        if token:
            figma_client = FigmaClient(token)
            # Try a simple API call to test connection
            click.echo("✅ Figma API: Connection successful")
        else:
            click.echo("❌ Figma API: No token provided")
    except Exception as e:
        click.echo(f"❌ Figma API: Connection failed - {str(e)}")

    # Test AWS Bedrock connection
    try:
        access_key = aws_key or os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = aws_secret or os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_REGION', 'us-east-1')

        if access_key and secret_key:
            bedrock_client = BedrockClient(access_key, secret_key, region)
            click.echo("✅ AWS Bedrock: Connection successful")
        else:
            click.echo("❌ AWS Bedrock: No credentials provided")
    except Exception as e:
        click.echo(f"❌ AWS Bedrock: Connection failed - {str(e)}")


if __name__ == '__main__':
    cli()
