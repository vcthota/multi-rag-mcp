"""
API Governance Validator - Streamlit UI
Interactive web interface for validating API specifications via REST API
"""
import streamlit as st
import sys
import json
from pathlib import Path
import httpx
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="API Governance Validator",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Enhanced Design
st.markdown("""
<style>
    /* Main Layout */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1f77b4 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Alert Boxes */
    .success-box {
        padding: 1.5rem;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 6px solid #28a745;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .error-box {
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 6px solid #dc3545;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .warning-box {
        padding: 1.5rem;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 6px solid #ffc107;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .info-box {
        padding: 1.5rem;
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 6px solid #17a2b8;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Cards */
    .violation-card {
        padding: 1.5rem;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        margin: 1.5rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.2s;
    }
    
    .violation-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }
    
    /* Metrics */
    .metric-card {
        padding: 1.5rem;
        text-align: center;
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Badges */
    .badge-critical {
        background-color: #dc3545;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .badge-high {
        background-color: #fd7e14;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .badge-medium {
        background-color: #ffc107;
        color: #212529;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .badge-low {
        background-color: #28a745;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
    }
</style>
""", unsafe_allow_html=True)


# Sample API specs for quick testing
SAMPLE_SPECS = {
    "Bad API Spec (Multiple Violations)": {
        "openapi": "3.0.0",
        "info": {
            "title": "Orders API",
            "version": "1.0.0"
        },
        "paths": {
            "/createOrder": {
                "post": {
                    "summary": "Create order",
                    "responses": {
                        "200": {"description": "Success"}
                    }
                }
            },
            "/getUserDetails/{id}": {
                "get": {
                    "summary": "Get user",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "200": {"description": "Success"}
                    }
                }
            }
        }
    },
    "Good API Spec (Compliant)": {
        "openapi": "3.0.0",
        "info": {
            "title": "Orders API",
            "version": "1.0.0"
        },
        "paths": {
            "/api/v1/orders": {
                "get": {
                    "summary": "List orders",
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                        {"name": "size", "in": "query", "schema": {"type": "integer", "default": 20}}
                    ],
                    "responses": {
                        "200": {"description": "Success", "content": {"application/json": {"schema": {"type": "object"}}}},
                        "400": {"$ref": "#/components/responses/BadRequest"},
                        "401": {"$ref": "#/components/responses/Unauthorized"}
                    }
                },
                "post": {
                    "summary": "Create order",
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OrderCreate"}}}},
                    "responses": {
                        "201": {"description": "Created"},
                        "400": {"$ref": "#/components/responses/BadRequest"}
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "OrderCreate": {"type": "object", "required": ["amount"], "properties": {"amount": {"type": "number"}}},
                "Error": {"type": "object", "properties": {"code": {"type": "string"}, "message": {"type": "string"}, "traceId": {"type": "string"}}}
            },
            "responses": {
                "BadRequest": {"description": "Bad request", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                "Unauthorized": {"description": "Unauthorized", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
            },
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            }
        },
        "security": [{"bearerAuth": []}]
    }
}


def validate_api_spec(spec_content: str, spec_format: str = "json", api_url: str = "http://localhost:8000"):
    """Validate API specification via REST API call (synchronous)"""
    
    # Prepare the request
    url = f"{api_url}/api/v1/governance/validate"
    
    # Prepare the request payload matching the API's expected format
    payload = {
        "spec_content": spec_content,
        "spec_format": spec_format
    }
    
    # Make the API call synchronously
    try:
        response = httpx.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120.0
        )
        response.raise_for_status()
        result = response.json()
        
        return result
    except httpx.HTTPStatusError as e:
        error_detail = f"API Error {e.response.status_code}: {e.response.text}"
        st.error(error_detail)
        raise Exception(error_detail)
    except httpx.HTTPError as e:
        error_detail = f"Connection Error: {str(e)}"
        st.error(error_detail)
        raise Exception(error_detail)


def get_corrected_spec(spec_content: str, violations: list, spec_format: str = "json", api_url: str = "http://localhost:8000"):
    """Get corrected API specification via REST API call (synchronous)"""
    
    url = f"{api_url}/api/v1/governance/correct"
    
    payload = {
        "spec_content": spec_content,
        "violations": violations,
        "spec_format": spec_format
    }
    
    try:
        response = httpx.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=180.0
        )
        response.raise_for_status()
        result = response.json()
        return result
    except httpx.HTTPStatusError as e:
        error_detail = f"API Error {e.response.status_code}: {e.response.text}"
        st.error(error_detail)
        raise Exception(error_detail)
    except httpx.HTTPError as e:
        error_detail = f"Connection Error: {str(e)}"
        st.error(error_detail)
        raise Exception(error_detail)


def display_severity_badge(severity: str):
    """Display colored severity badge"""
    colors = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    return f"{colors.get(severity.lower(), '⚪')} **{severity.upper()}**"


def main():
    # Header with enhanced design
    st.markdown('<div class="main-header">🔒 API Governance Validator</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">✨ Validate & Auto-Correct Your API Specifications Against Enterprise Standards</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API URL Configuration - read from environment variable with fallback
        default_api_url = os.environ.get("API_URL", "http://localhost:8000")
        api_url = st.text_input(
            "API Service URL",
            value=default_api_url,
            help="URL of the API Governance service"
        )
        
        # Check API connection
        try:
            import httpx
            response = httpx.get(f"{api_url}/health", timeout=2.0)
            if response.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.warning(f"⚠️ API returned {response.status_code}")
        except Exception as e:
            st.error(f"❌ API Not Connected")
            st.caption(f"Error: {str(e)[:50]}...")
        
        st.markdown("---")
        
        # Input method selection
        input_method = st.radio(
            "Select Input Method",
            ["📝 Manual Input", "📄 Upload File", "🎯 Sample Specs"]
        )
        
        st.markdown("---")
        
        # Format selection
        spec_format = st.selectbox(
            "API Spec Format",
            ["json", "yaml"],
            help="Select the format of your API specification"
        )
        
        st.markdown("---")
        
        # Information
        with st.expander("ℹ️ About This Tool", expanded=False):
            st.markdown("""
            **🎯 What This Tool Does:**
            
            Validates your API specifications against enterprise governance rules stored in a vector database and powered by AI.
            
            **📋 Validation Rules Include:**
            - ✅ URI naming conventions (nouns, plural, lowercase)
            - ✅ HTTP methods & status codes
            - ✅ Request/Response schemas
            - ✅ Error handling standards
            - ✅ Security requirements (OAuth, JWT)
            - ✅ API versioning
            - ✅ Documentation completeness
            - ✅ Pagination & filtering
            
            **🔧 Features:**
            - Real-time validation
            - Detailed violation reports
            - Severity-based prioritization
            - **Auto-correction suggestions**
            - Downloadable reports
            """)
        
        st.markdown("---")
        
        # Quick Tips
        with st.expander("💡 Quick Tips", expanded=False):
            st.markdown("""
            **For Best Results:**
            
            1. 📝 Use OpenAPI 3.0+ or Swagger 2.0 format
            2. ✅ Ensure JSON is properly formatted
            3. 📊 Include all endpoint details
            4. 🔐 Add security schemes
            5. 📚 Document request/response schemas
            
            **Sample Specs Available:**
            - Try "Bad API Spec" to see violations
            - Try "Good API Spec" to see compliance
            """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📥 Input API Specification")
        
        # Initialize spec_content from session state or None
        if 'spec_content' not in st.session_state:
            st.session_state.spec_content = None
        
        spec_content = None
        
        if input_method == "📝 Manual Input":
            spec_content = st.text_area(
                "Paste your API specification (OpenAPI/Swagger)",
                height=400,
                value=st.session_state.spec_content if st.session_state.spec_content else "",
                placeholder='{\n  "openapi": "3.0.0",\n  "info": {\n    "title": "My API",\n    "version": "1.0.0"\n  },\n  "paths": {}\n}',
                help="Paste your OpenAPI/Swagger specification in JSON or YAML format"
            )
            # Update session state
            if spec_content:
                st.session_state.spec_content = spec_content
        
        elif input_method == "📄 Upload File":
            uploaded_file = st.file_uploader(
                "Upload API specification file",
                type=["json", "yaml", "yml"],
                help="Upload your OpenAPI/Swagger specification file"
            )
            
            if uploaded_file:
                spec_content = uploaded_file.read().decode("utf-8")
                st.session_state.spec_content = spec_content
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                with st.expander("Preview uploaded content"):
                    st.code(spec_content[:500] + "..." if len(spec_content) > 500 else spec_content)
            elif st.session_state.spec_content:
                spec_content = st.session_state.spec_content
        
        elif input_method == "🎯 Sample Specs":
            sample_choice = st.selectbox(
                "Select a sample specification",
                list(SAMPLE_SPECS.keys())
            )
            
            spec_content = json.dumps(SAMPLE_SPECS[sample_choice], indent=2)
            st.session_state.spec_content = spec_content
            
            with st.expander("View sample specification", expanded=True):
                st.json(SAMPLE_SPECS[sample_choice])
        
        # Validate button with enhanced design
        st.markdown("---")
        
        if spec_content and spec_content.strip():
            validate_button = st.button(
                "🚀 Validate API Specification", 
                type="primary", 
                use_container_width=True,
                help="Click to validate your API spec against governance rules",
                key="validate_btn"
            )
            
            # IMMEDIATE VALIDATION - Run right here when button is clicked
            if validate_button:
                st.write("🔍 Button clicked! Starting validation...")
                st.write(f"📝 Spec length: {len(spec_content)} characters")
                st.write(f"🌐 API URL: {api_url}")
                
                with st.spinner("🔍 Validating..."):
                    try:
                        result = validate_api_spec(spec_content, spec_format, api_url)
                        st.session_state['validation_result'] = result
                        st.session_state['validation_complete'] = True
                        st.success("✅ Validation complete! Check results on the right →")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Validation failed: {str(e)}")
                        st.session_state['validation_complete'] = False
        else:
            st.warning("⚠️ Please provide an API specification to validate")
            validate_button = False
    
    with col2:
        st.header("📊 Validation Results")
        
        # Check if we have validation results in session state
        if 'validation_result' in st.session_state and st.session_state.get('validation_complete'):
            result = st.session_state['validation_result']
            
            # Display metrics
            st.markdown("### 📈 Validation Summary")
            
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                st.metric(
                    label="Compliance Score",
                    value=f"{result['compliance_score'] * 100:.1f}%",
                    delta=f"{(result['compliance_score'] - 1.0) * 100:.1f}%" if result['compliance_score'] < 1.0 else "Perfect!"
                )
            
            with metric_cols[1]:
                st.metric(
                    label="Rules Checked",
                    value=result['rules_checked']
                )
            
            with metric_cols[2]:
                st.metric(
                    label="Violations Found",
                    value=len(result['violations'])
                )
            
            with metric_cols[3]:
                st.metric(
                    label="Status",
                    value="✅ Valid" if result['valid'] else "❌ Invalid"
                )
            
            st.markdown("---")
            
            # Overall status
            if result['valid']:
                st.markdown(
                    '<div class="success-box">✅ <strong>Validation Passed!</strong> Your API specification is compliant with all governance rules.</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="error-box">❌ <strong>Validation Failed!</strong> Found {len(result["violations"])} violation(s) that need to be addressed.</div>',
                    unsafe_allow_html=True
                )
                st.markdown("""
                <div class="info-box">
                    <h3>👋 Welcome to API Governance Validator!</h3>
                    <p>Get started by following these steps:</p>
                    <ol>
                        <li>📝 <strong>Choose an input method</strong> from the left sidebar</li>
                        <li>✍️ <strong>Provide your API specification</strong> (OpenAPI/Swagger format)</li>
                        <li>🚀 <strong>Click "Validate"</strong> to check against governance rules</li>
                        <li>📊 <strong>Review results</strong> and get auto-correction suggestions</li>
                    </ol>
                    <hr>
                    <p><strong>💡 Pro Tip:</strong> Start with the sample specs to see how it works!</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show features
                st.markdown("### ✨ Key Features")
                feature_col1, feature_col2 = st.columns(2)
                
                with feature_col1:
                    st.markdown("""
                    **🔍 Real-Time Validation**
                    - Instant feedback on your API design
                    - AI-powered analysis
                    - 20+ governance rules checked
                    
                    **📊 Detailed Reports**
                    - Compliance scoring
                    - Severity-based prioritization
                    - Actionable recommendations
                    """)
                
                with feature_col2:
                    st.markdown("""
                    **🔧 Auto-Correction**
                    - AI-generated fixes
                    - Download corrected specs
                    - Re-validate after fixes
                    
                    **💾 Export Options**
                    - JSON validation reports
                    - Text-based summaries
                    - Corrected specifications
                    """)
        else:
            # Show validation results from session state if available
            if 'validation_result' in st.session_state and st.session_state.get('validation_complete'):
                result = st.session_state['validation_result']
                
                with st.container():
                    # Display metrics
                    st.markdown("### 📈 Validation Summary")
                    
                    metric_cols = st.columns(4)
                    
                    with metric_cols[0]:
                        st.metric(
                            label="Compliance Score",
                            value=f"{result['compliance_score'] * 100:.1f}%",
                            delta=f"{(result['compliance_score'] - 1.0) * 100:.1f}%" if result['compliance_score'] < 1.0 else "Perfect!"
                        )
                    
                    with metric_cols[1]:
                        st.metric(
                            label="Rules Checked",
                            value=result['rules_checked']
                        )
                    
                    with metric_cols[2]:
                        st.metric(
                            label="Violations Found",
                            value=len(result['violations'])
                        )
                    
                    with metric_cols[3]:
                        st.metric(
                            label="Status",
                            value="✅ Valid" if result['valid'] else "❌ Invalid"
                        )
                    
                    st.markdown("---")
                    
                    # Overall status
                    if result['valid']:
                        st.markdown(
                            '<div class="success-box">✅ <strong>Validation Passed!</strong> Your API specification is compliant with all governance rules.</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="error-box">❌ <strong>Validation Failed!</strong> Found {len(result["violations"])} violation(s) that need to be addressed.</div>',
                            unsafe_allow_html=True
                        )
                    
                    # Violations details
                    if result['violations']:
                        st.markdown("### 🔍 Violations Details")
                        
                        # Group violations by severity
                        severity_counts = {}
                        for v in result['violations']:
                            sev = v.get('severity', 'medium').lower()
                            severity_counts[sev] = severity_counts.get(sev, 0) + 1
                        
                        # Display severity breakdown
                        if severity_counts:
                            st.markdown("**Breakdown by Severity:**")
                            severity_cols = st.columns(4)
                            severities = ['critical', 'high', 'medium', 'low']
                            for i, sev in enumerate(severities):
                                if sev in severity_counts:
                                    with severity_cols[i]:
                                        st.metric(sev.capitalize(), severity_counts[sev])
                        
                        st.markdown("---")
                        
                        # Display each violation
                        for i, violation in enumerate(result['violations'], 1):
                            with st.expander(f"**Violation #{i}** - {violation.get('rule', 'Unknown Rule')}", expanded=i <= 3):
                                col_a, col_b = st.columns([1, 3])
                                
                                with col_a:
                                    st.markdown("**Severity**")
                                    st.markdown(display_severity_badge(violation.get('severity', 'medium')))
                                
                                with col_b:
                                    st.markdown("**Rule Violated**")
                                    st.info(violation.get('rule', 'N/A'))
                                
                                st.markdown("**Details**")
                                st.warning(violation.get('details', 'No details available'))
                                
                                st.markdown("**Recommendation**")
                                st.success(violation.get('recommendation', 'No recommendation available'))
                                
                                if violation.get('examples'):
                                    st.markdown("**Example Fix**")
                                    st.code(violation['examples'], language='json')
                    else:
                        st.balloons()
                        st.success("🎉 No violations found! Your API specification follows all governance rules.")
                    
                    # Auto-Correction Section
                    if result['violations']:
                        st.markdown("---")
                        st.markdown("### � Auto-Correction")
                        
                        st.info("💡 **Want to fix these violations automatically?** Click the button below to get an AI-corrected version of your API specification!")
                        
                        col_correct1, col_correct2, col_correct3 = st.columns([2, 1, 2])
                        
                        with col_correct2:
                            correct_button = st.button("🚀 Auto-Correct API Spec", type="primary", use_container_width=True)
                        
                        if correct_button:
                            with st.spinner("🔧 Generating corrected API specification..."):
                                try:
                                    corrected = get_corrected_spec(
                                        spec_content, 
                                        result['violations'],
                                        spec_format,
                                        api_url
                                    )
                                    
                                    st.success("✅ Corrected API specification generated successfully!")
                                    
                                    # Display corrected spec
                                    st.markdown("#### 📝 Corrected API Specification")
                                    
                                    corrected_spec = corrected.get('corrected_spec', '')
                                    changes_made = corrected.get('changes', [])
                                    violations_fixed = corrected.get('violations_fixed', 0)
                                    
                                    # Show summary metrics
                                    col_m1, col_m2 = st.columns(2)
                                    with col_m1:
                                        st.metric("Violations Fixed", violations_fixed)
                                    with col_m2:
                                        st.metric("Changes Applied", len(changes_made))
                                    
                                    # Show changes summary
                                    if changes_made:
                                        with st.expander("🔍 View Changes Made", expanded=True):
                                            for i, change in enumerate(changes_made, 1):
                                                # Handle both dict and string formats
                                                if isinstance(change, dict):
                                                    violation = change.get('violation', 'N/A')
                                                    change_desc = change.get('change', 'N/A')
                                                    location = change.get('location', 'N/A')
                                                    st.markdown(f"**{i}. {violation}**")
                                                    st.markdown(f"   - Change: {change_desc}")
                                                    st.markdown(f"   - Location: `{location}`")
                                                else:
                                                    st.markdown(f"**{i}. {change}**")
                                    
                                    # Display the corrected spec
                                    st.code(corrected_spec, language=spec_format)
                                    
                                    # Download corrected spec
                                    st.download_button(
                                        label="📥 Download Corrected API Specification",
                                        data=corrected_spec,
                                        file_name=f"corrected_api_spec.{spec_format}",
                                        mime="application/json" if spec_format == "json" else "text/yaml",
                                        type="primary"
                                    )
                                    
                                    # Option to re-validate
                                    st.info("💡 **Tip:** You can copy the corrected specification above and re-validate it to verify all issues are fixed!")
                                    
                                except Exception as e:
                                    st.error(f"❌ Failed to generate corrected specification: {str(e)}")
                    
                    # Download results
                    st.markdown("---")
                    st.markdown("### 💾 Export Validation Report")
                    
                    col_download1, col_download2 = st.columns(2)
                    
                    with col_download1:
                        result_json = json.dumps(result, indent=2)
                        st.download_button(
                            label="📥 Download Report (JSON)",
                            data=result_json,
                            file_name="api_validation_report.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                    with col_download2:
                        # Create a formatted text report
                        report_text = f"""API Governance Validation Report
=====================================

Specification: {result.get('request_id', 'N/A')}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Status: {'✅ PASSED' if result['valid'] else '❌ FAILED'}
Compliance Score: {result['compliance_score']:.1f}%
Rules Checked: {result['rules_checked']}
Violations Found: {len(result['violations'])}

VIOLATIONS
----------
"""
                        for i, v in enumerate(result['violations'], 1):
                            report_text += f"""
{i}. {v.get('rule', 'Unknown')}
   Severity: {v.get('severity', 'medium').upper()}
   Details: {v.get('details', 'N/A')}
   Recommendation: {v.get('recommendation', 'N/A')}
   ---
"""
                        
                        st.download_button(
                            label="📄 Download Report (TXT)",
                            data=report_text,
                            file_name="api_validation_report.txt",
                            mime="text/plain",
                            use_container_width=True
                        )


if __name__ == "__main__":
    main()
