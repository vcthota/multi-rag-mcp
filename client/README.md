# API Governance Validator - Streamlit UI

Interactive web interface for validating API specifications against enterprise governance rules.

## Features

- 🔍 **Real-time Validation** - Validate OpenAPI/Swagger specs against governance rules from vector DB
- 📊 **Compliance Scoring** - Get detailed compliance scores and metrics
- 🎯 **Multiple Input Methods** - Manual input, file upload, or sample specs
- 📝 **Detailed Reports** - See violations with severity, recommendations, and examples
- 💾 **Export Results** - Download validation reports as JSON

## Installation

### 1. Install Streamlit

```bash
cd client
uv pip install -r requirements.txt
```

Or install directly:

```bash
uv pip install streamlit
```

### 2. Run the Application

**Option 1: Using the startup script (Recommended)**
```bash
cd client
./run.sh
```

**Option 2: Using command line with PYTHONPATH**
```bash
# From project root
cd /Users/venkatathota/AI-Courses/projects/multi-rag-mcp
PYTHONPATH=$PWD uv run streamlit run client/app.py
```

**Option 3: Set PYTHONPATH and run**
```bash
export PYTHONPATH=/path/to/multi-rag-mcp
cd client
uv run streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

**Note:** The PYTHONPATH must include the project root directory so that the `src` module can be imported.

## Usage

### Method 1: Manual Input
1. Select "📝 Manual Input" in the sidebar
2. Paste your OpenAPI/Swagger specification
3. Click "🚀 Validate API Specification"

### Method 2: Upload File
1. Select "📄 Upload File" in the sidebar
2. Upload your `.json` or `.yaml` API specification file
3. Click "🚀 Validate API Specification"

### Method 3: Sample Specs
1. Select "🎯 Sample Specs" in the sidebar
2. Choose from pre-loaded sample specifications
3. Click "🚀 Validate API Specification"

## Validation Results

The tool provides:

- **Compliance Score** - Overall percentage score
- **Rules Checked** - Number of governance rules evaluated
- **Violations Found** - Total number of violations
- **Status** - Pass/Fail indicator

For each violation, you'll see:
- **Severity Level** - Critical, High, Medium, or Low
- **Rule Violated** - Which governance rule was broken
- **Details** - Explanation of the violation
- **Recommendation** - How to fix the issue
- **Example** - Code example (when applicable)

## Governance Rules

The validator checks against enterprise governance standards including:

- ✅ URI naming conventions (nouns, plural, lowercase, hyphens)
- ✅ HTTP methods and status codes
- ✅ Request/response schema standards
- ✅ Error handling and error model format
- ✅ Security (authentication, authorization)
- ✅ API versioning approach
- ✅ Documentation completeness (OpenAPI standards)
- ✅ Pagination, filtering, sorting

## Screenshot Examples

### Valid API Specification
When your API spec passes all checks, you'll see:
- ✅ Green success message
- 100% compliance score
- No violations listed

### Invalid API Specification
When violations are found:
- ❌ Red error message
- Compliance score < 100%
- Detailed list of violations with recommendations

## Architecture

```
User Interface (Streamlit)
         ↓
API Governance Validator
         ↓
Vector Database (ChromaDB)
         ↓
Governance Rules (Retrieved)
         ↓
LLM Validation (GPT-4)
         ↓
Validation Report
```

## Troubleshooting

### Port Already in Use
If port 8501 is already in use:
```bash
streamlit run app.py --server.port 8502
```

### Module Not Found Errors
Make sure you're running from the project root and the parent directory is in the Python path:
```bash
cd /path/to/multi-rag-mcp/client
PYTHONPATH=.. streamlit run app.py
```

### Vector Database Not Found
Ensure you've run the ingestion pipeline first:
```bash
cd ..
uv run python run_ingestion.py
```

## Development

### Project Structure
```
client/
├── app.py              # Main Streamlit application
├── requirements.txt    # Client dependencies
└── README.md          # This file
```

### Customization

You can customize the UI by modifying `app.py`:

- **Colors and Styling** - Edit the CSS in the `st.markdown()` section
- **Sample Specs** - Add more examples to the `SAMPLE_SPECS` dictionary
- **Validation Logic** - Modify the `validate_api_spec()` function
- **Layout** - Adjust columns and containers in the `main()` function

## Support

For issues or questions:
1. Check the logs in the Streamlit terminal
2. Verify the backend API Governance service is working
3. Ensure ChromaDB has governance rules ingested

## License

See main project LICENSE file.
