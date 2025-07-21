import streamlit as st
import requests
import json
import yaml
from openapi_spec_validator import validate_spec
from datetime import datetime

st.set_page_config(page_title="API → Swagger (Gemini 2.5 Flash)", layout="wide")
st.title("API Code → Swagger GenAI (Gemini 2.5 Flash)")

# API Key Input Section
st.subheader("🔑 API Configuration")
api_key = st.text_input(
    "Enter your Gemini API Key", 
    type="password", 
    placeholder="Enter your Gemini API key here...",
    help="Get your API key from Google AI Studio: https://aistudio.google.com/"
)

# Show API key status
if api_key:
    st.success("✅ API Key provided")
else:
    st.warning("⚠️ Please provide your Gemini API key to continue")

st.divider()

# Output Format Selection
st.markdown("### 📦 Output Format")
output_format = st.radio(
    "Choose your preferred output format:",
    ["YAML", "JSON"],
    index=0,
    horizontal=True
)

# Main Layout - Split into two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Paste your API code")
    api_code = st.text_area(
        "Code Area", 
        height=400, 
        placeholder="Paste your API code here (Flask, FastAPI, Express.js, etc.)..."
    )

with col2:
    st.subheader(f"📄 Generated Swagger/OpenAPI ({output_format})")
    swagger_output = st.empty()

# Prompt Detail Level
st.markdown("### 🧠 Documentation Detail Level")
doc_detail_level = st.radio(
    "Choose the level of documentation detail:",
    ["Minimal", "Standard", "Detailed"],
    index=1
)

# Generate Button
if st.button("🚀 Generate Swagger", type="primary"):
    if not api_key.strip():
        st.error("❌ Please provide your Gemini API key!")
    elif not api_code.strip():
        st.error("❌ Please paste some API code before submitting!")
    else:
        with st.spinner("🔄 Generating Swagger docs with Gemini 2.5 Flash..."):
            try:
                detail_instructions = {
                    "Minimal": "Generate a minimal Swagger OpenAPI 3.0 specification.",
                    "Standard": "Generate a standard OpenAPI 3.0 Swagger spec with info, paths, schemas, and examples.",
                    "Detailed": "Generate a complete OpenAPI 3.0 Swagger spec with reusable schemas, error responses, and advanced documentation."
                }

                format_instruction = f"Return ONLY valid Swagger/OpenAPI 3.0 in {output_format.upper()} format. No markdown, no explanation."
                prompt = f"""
{detail_instructions[doc_detail_level]}

{format_instruction}

API Code below:
{api_code}
"""

                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {
                                "parts": [{"text": prompt}]
                            }
                        ]
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    raw_output = result["candidates"][0]["content"]["parts"][0]["text"].strip()

                    # Strip code block markers
                    for marker in ["```yaml", "```json", "```"]:
                        if raw_output.startswith(marker):
                            raw_output = raw_output[len(marker):].strip()
                        if raw_output.endswith("```"):
                            raw_output = raw_output[:-3].strip()

                    try:
                        if output_format == "YAML":
                            spec_dict = yaml.safe_load(raw_output)
                            validate_spec(spec_dict)
                            display_data = raw_output
                            mime_type = "text/yaml"
                            file_ext = "yaml"
                        else:
                            spec_dict = json.loads(raw_output)
                            validate_spec(spec_dict)
                            display_data = json.dumps(spec_dict, indent=2)
                            mime_type = "application/json"
                            file_ext = "json"

                        swagger_output.code(display_data, language=output_format.lower())
                        st.success(f"✅ Valid {output_format} Swagger documentation generated!")

                        st.download_button(
                            label=f"📥 Download Swagger {output_format}",
                            data=display_data,
                            file_name=f"swagger.{file_ext}",
                            mime=mime_type
                        )

                        with st.expander("📘 How to Use This Swagger File"):
                            st.markdown("""
- Upload to [editor.swagger.io](https://editor.swagger.io)
- Import into Postman or Insomnia
- Host using [Swagger UI](https://swagger.io/tools/swagger-ui/)
- Render in ReDoc: https://redocly.github.io/redoc/
""")

                    except Exception as ve:
                        st.error(f"⚠️ {output_format} generated but failed validation: {ve}")
                        swagger_output.code(raw_output, language=output_format.lower())

                elif response.status_code == 503:
                    st.error("🚧 Gemini model is currently overloaded. Please try again shortly.")
                elif response.status_code == 401:
                    st.error("❌ Invalid API key! Please check your Gemini API key.")
                elif response.status_code == 429:
                    st.error("❌ Rate limit exceeded. Please wait and try again.")
                else:
                    st.error(f"❌ Unexpected API error: {response.status_code}")
                    st.text(response.text)

            except requests.Timeout:
                st.error("❌ Request timed out! Try again in a few seconds.")
            except Exception as ex:
                st.error(f"❌ An unexpected error occurred: {str(ex)}")

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
**How to use:**
1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Enter your key, paste API code, and choose output format
3. Click 'Generate Swagger'
4. Download or copy the result

**Tips:**
- Use full code for best results
- YAML is ideal for editing
- JSON is good for tooling
""")

    st.header("🛠 Troubleshooting")
    st.markdown("""
- ❌ 503: Model busy — try again after 30s
- ❌ 401: Invalid API key
- ❌ 429: Too many requests — retry later
""")

# Footer
st.divider()
st.markdown(f"<div style='text-align: center; color: gray;'>Built with ❤️ at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

