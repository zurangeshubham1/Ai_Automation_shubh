# 🤖 AI Test Automation Agent

An intelligent automation testing agent that converts plain English or CSV data into Python Behave/Selenium code automatically. No more writing repetitive test code!

## ✨ Features

- **Natural Language Processing**: Write tests in plain English
- **CSV Support**: Define tests using simple CSV format
- **Automatic Code Generation**: Converts your input to Behave/Selenium code
- **Screenshot Capture**: Automatic screenshots on test steps and failures
- **Beautiful Reports**: HTML and JSON reports with detailed results
- **One-Click Execution**: Run tests with a single command
- **AI-Powered**: Uses OpenAI API for intelligent test parsing (optional)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd "AI Agent"

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
copy env_example.txt .env
# Edit .env file with your settings
```

### 2. Basic Usage

#### Interactive Mode
```bash
python ai_agent.py interactive
```

#### Quick Test from Description
```bash
python ai_agent.py quick "Login with user test_user and check welcome message"
```

#### Create Sample Test
```bash
python ai_agent.py sample
```

#### Run All Tests
```bash
python ai_agent.py run-all
```

## 📝 How It Works

### Method 1: CSV Format

Create a CSV file with your test steps:

```csv
Step,Action,Target,Data,Description
1,Open URL,https://example.com,,Navigate to the website
2,Type,#username,test_user,Enter username
3,Type,#password,myPassword123,Enter password
4,Click,#loginButton,,Click login button
5,Verify,text=Welcome,,Verify welcome message appears
```

### Method 2: Natural Language

Just describe what you want to test:

```
"Login with user test_user and check welcome message"
"Navigate to https://example.com, fill in the contact form, and submit it"
"Click on the shopping cart and verify items are displayed"
```

## 🎯 Supported Actions

| Action | Description | Example |
|--------|-------------|---------|
| `Open URL` | Navigate to a website | `https://example.com` |
| `Type` | Enter text in a field | `#username`, `test_user` |
| `Click` | Click on an element | `#loginButton` |
| `Verify` | Check if text/element exists | `text=Welcome` |
| `Wait` | Pause execution | `5` (seconds) |
| `Select` | Choose from dropdown | `#country`, `United States` |
| `Hover` | Mouse over element | `#menu` |
| `Scroll` | Scroll to element | `#footer` |
| `Clear` | Clear text field | `#searchBox` |

## 🎨 Element Selectors

The agent supports various selector types:

- **ID**: `#username`
- **Class**: `.btn-primary`
- **XPath**: `xpath=//button[@id='submit']`
- **CSS**: `css=.form-group input`
- **Text**: `text=Login`
- **Name**: `name=email`

## 📊 Reports

After test execution, you'll get:

- **HTML Report**: Beautiful, interactive report with screenshots
- **JSON Report**: Machine-readable test results
- **Screenshots**: Captured at each step and on failures
- **Console Logs**: Detailed execution logs

## ⚙️ Configuration

Edit the `.env` file to customize:

```env
# Browser Configuration
BROWSER=chrome
HEADLESS=false
WINDOW_SIZE=1920,1080

# Test Configuration
IMPLICIT_WAIT=10
EXPLICIT_WAIT=20
SCREENSHOT_ON_FAILURE=true

# AI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here
AI_MODEL=gpt-3.5-turbo
```

## 📁 Project Structure

```
AI Agent/
├── ai_agent.py              # Main orchestrator
├── csv_parser.py            # CSV test data parser
├── nlp_processor.py         # Natural language processor
├── code_generator.py        # Behave/Selenium code generator
├── test_executor.py         # Test execution engine
├── report_generator.py      # Report generation
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── features/               # Generated feature files
├── features/steps/         # Generated step definitions
├── reports/                # Test reports
└── screenshots/            # Test screenshots
```

## 🔧 Advanced Usage

### Custom Test Creation

```python
from ai_agent import AIAgent

agent = AIAgent()

# From CSV
test_info = agent.create_test_from_csv('my_test.csv', 'login_test')

# From natural language
test_info = agent.create_test_from_text(
    "Login with admin user and verify dashboard", 
    "admin_login_test"
)

# Run the test
result = agent.run_test('login_test')
```

### Batch Processing

```python
# Run all tests and get comprehensive report
results = agent.run_all_tests()
print(f"Success rate: {results['summary']['success_rate']}%")
```

## 🐛 Troubleshooting

### Common Issues

1. **Chrome not found**: Install Chrome browser
2. **Permission errors**: Run with appropriate permissions
3. **Import errors**: Ensure all dependencies are installed
4. **Test failures**: Check element selectors and website availability

### Debug Mode

Set `HEADLESS=false` in `.env` to see browser actions in real-time.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example files
3. Create an issue with detailed information

---

**Happy Testing! 🎉**

*No more repetitive test code - let AI do the heavy lifting!*
