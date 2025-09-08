# FigmaToBDD - Figma Design to BDD Scenarios Generator

A Python tool that extracts Figma design data via API and generates comprehensive BDD (Behavior Driven Development) test scenarios using AWS Bedrock AI services.

## 🚀 Features

- **Figma API Integration**: Extract design data from Figma files with dev seat access
- **AWS Bedrock Integration**: Generate intelligent BDD scenarios using Claude AI
- **Multiple Output Formats**: Generate documents in Markdown, HTML, PDF, and JSON formats
- **SSL Validation**: Configurable SSL certificate verification
- **Modular Commands**: Separate commands for extraction and generation
- **Multiple Scenario Types**: Functional, UI, Accessibility, and Performance testing scenarios

## 📋 Prerequisites

- Python 3.8 or higher
- Figma account with dev seat access
- AWS account with Bedrock access
- Internet connection for API calls

## 🛠️ Installation

1. **Clone or setup the project:**
```bash
cd /Users/ghanthan/PycharmProjects/FigmaToBdd
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
Copy the `.env` file and update with your credentials (see setup instructions below).

## 🔐 API Setup Instructions

### Step 1: Figma API Setup

1. **Get Figma Personal Access Token:**
   - Go to [Figma Developers](https://www.figma.com/developers/api)
   - Click "Get personal access token"
   - Log in to your Figma account
   - Generate a new personal access token
   - Copy the token

2. **Get Figma File ID:**
   - Open your Figma file in the browser
   - Copy the file ID from the URL: `https://www.figma.com/file/FILE_ID/...`
   - The FILE_ID is the long string after `/file/`

3. **Update .env file:**
```env
FIGMA_ACCESS_TOKEN=your_figma_token_here
FIGMA_FILE_ID=your_file_id_here
```

### Step 2: AWS Bedrock Setup

1. **Create AWS IAM User:**
   - Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
   - Create a new user or use existing user
   - Attach the policy: `AmazonBedrockFullAccess`

2. **Generate Access Keys:**
   - In IAM, go to Users → Your User → Security credentials
   - Create access key for CLI/API usage
   - Copy Access Key ID and Secret Access Key

3. **Enable Bedrock Models:**
   - Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
   - Navigate to "Model access"
   - Request access to Anthropic Claude models (claude-3-sonnet recommended)
   - Wait for approval (usually instant for Claude models)

4. **Update .env file:**
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

### Step 3: SSL Configuration

For production environments:
```env
VERIFY_SSL=true
```

For development/testing (if you encounter SSL issues):
```env
VERIFY_SSL=false
```

## 📖 Usage

### Quick Setup Check
```bash
python main.py setup
```

### Test API Connections
```bash
python main.py test-connection
```

### Command Options

#### 1. Extract Figma Data Only
```bash
# Extract design data and save as JSON
python main.py extract-figma -f YOUR_FIGMA_FILE_ID

# With custom output filename
python main.py extract-figma -f YOUR_FIGMA_FILE_ID -o my_design_data

# Override token from command line
python main.py extract-figma -f YOUR_FIGMA_FILE_ID -t YOUR_TOKEN
```

#### 2. Generate BDD from Existing JSON
```bash
# Generate functional BDD scenarios
python main.py generate-bdd -i figma_data.json

# Generate specific scenario types
python main.py generate-bdd -i figma_data.json --type ui
python main.py generate-bdd -i figma_data.json --type accessibility
python main.py generate-bdd -i figma_data.json --type performance

# Generate in specific format
python main.py generate-bdd -i figma_data.json --format pdf
python main.py generate-bdd -i figma_data.json --format html
python main.py generate-bdd -i figma_data.json --format all
```

#### 3. Full Pipeline (Recommended)
```bash
# Complete workflow: extract + generate
python main.py full-pipeline -f YOUR_FIGMA_FILE_ID

# With specific options
python main.py full-pipeline -f YOUR_FIGMA_FILE_ID --type functional --format all
```

### Command Parameters

| Parameter | Description | Options |
|-----------|-------------|---------|
| `-f, --file-id` | Figma file ID | Required for extraction |
| `-i, --input` | Input JSON file | Required for generation |
| `-o, --output` | Output filename | Default: varies by command |
| `-T, --type` | Scenario type | functional, ui, accessibility, performance |
| `-F, --format` | Output format | markdown, pdf, html, all |
| `-t, --token` | Figma token override | Overrides .env setting |
| `--no-ssl-verify` | Disable SSL verification | Flag for SSL issues |

## 📁 Project Structure

```
FigmaToBdd/
├── main.py                 # CLI application entry point
├── figma_client.py         # Figma API client
├── bedrock_client.py       # AWS Bedrock client
├── document_generator.py   # Document generation utilities
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── output/                 # Generated documents (created automatically)
└── README.md              # This file
```

## 📄 Output Files

The tool generates the following types of files:

### JSON Files
- `figma_design_data.json` - Raw extracted Figma data
- `{filename}_data.json` - Processed design data

### Document Files
- `{filename}.md` - Markdown format with BDD scenarios
- `{filename}.html` - HTML document with styling
- `{filename}.pdf` - PDF document for sharing/printing

### Example Output Structure
```
output/
├── figma_design_data.json
├── bdd_scenarios.md
├── bdd_scenarios.html
├── bdd_scenarios.pdf
└── bdd_scenarios_data.json
```

## 🎯 BDD Scenario Types

### Functional Testing
- Business logic validation
- User workflow testing
- Data flow scenarios
- Integration testing

### UI Testing
- Element visibility and positioning
- Responsive design behavior
- Visual consistency checks
- Interaction feedback

### Accessibility Testing
- WCAG 2.1 compliance
- Keyboard navigation
- Screen reader compatibility
- Color contrast validation

### Performance Testing
- Page load time scenarios
- Resource optimization
- API response times
- Mobile performance

## 🔍 Troubleshooting

### Common Issues

1. **SSL Certificate Errors:**
   ```bash
   # Use --no-ssl-verify flag or set VERIFY_SSL=false in .env
   python main.py extract-figma -f YOUR_FILE_ID --no-ssl-verify
   ```

2. **Figma API Token Issues:**
   - Verify token is valid and has not expired
   - Ensure you have access to the Figma file
   - Check if the file ID is correct

3. **AWS Bedrock Access:**
   - Verify IAM permissions include BedrockFullAccess
   - Ensure Claude models are enabled in your AWS region
   - Check AWS credentials are valid

4. **Missing Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Error Messages

| Error | Solution |
|-------|----------|
| "Figma access token is required" | Set FIGMA_ACCESS_TOKEN in .env |
| "AWS credentials are required" | Set AWS keys in .env |
| "Failed to fetch Figma file" | Check file ID and token |
| "Bedrock API error" | Verify AWS permissions and model access |

## 🔧 Development

### Adding New Features

1. **New Scenario Types:** Extend `BedrockClient.generate_test_scenarios()`
2. **New Output Formats:** Add methods to `DocumentGenerator`
3. **New Figma Elements:** Extend `FigmaClient._process_element()`

### Testing

```bash
# Test individual components
python -c "from figma_client import FigmaClient; print('Figma client imported successfully')"
python -c "from bedrock_client import BedrockClient; print('Bedrock client imported successfully')"
python -c "from document_generator import DocumentGenerator; print('Document generator imported successfully')"
```

## 📝 Example Workflow

1. **Prepare your Figma file** with clear naming and organization
2. **Set up API credentials** following the setup instructions
3. **Extract design data:**
   ```bash
   python main.py extract-figma -f YOUR_FILE_ID -o my_app_design
   ```
4. **Review the extracted JSON** to ensure all elements are captured
5. **Generate BDD scenarios:**
   ```bash
   python main.py generate-bdd -i my_app_design.json --type functional --format all
   ```
6. **Review generated documents** and customize as needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify API credentials and permissions
4. Test with a simple Figma file first

---

**Happy Testing!** 🎉
