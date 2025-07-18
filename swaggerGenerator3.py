import streamlit as st
import requests
import json
st.set_page_config(page_title="API → Swagger (Gemini 2.5 Flash)", layout="wide")
st.title("API Code → Swagger GenAI (Gemini 2.5 Flash)")
st.markdown("🧪 If you see this, the file is updated correctly.")

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
    st.subheader("📄 Generated Swagger/OpenAPI YAML")
    swagger_output = st.empty()

# Generate Button
if st.button("🚀 Generate Swagger", type="primary"):
    # Input validation
    if not api_key.strip():
        st.error("❌ Please provide your Gemini API key!")
    elif not api_code.strip():
        st.error("❌ Please paste some API code before submitting!")
    else:
        with st.spinner("🔄 Generating Swagger docs with Gemini 2.5 Flash..."):
            try:
                # Construct the prompt
                prompt = f"""
Convert the following API code to a complete, valid Swagger (OpenAPI 3.0) YAML specification. 
Include all necessary components such as:
- OpenAPI version declaration
- Info section with title, description, version
- Server configuration
- Paths with HTTP methods
- Request/response schemas
- Parameters and their types
- Error responses
- Security definitions if applicable

Return ONLY the YAML content without any additional text or explanations.

API Code:
{api_code}
"""

                # Make API request to Gemini (corrected endpoint)
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
                    headers={
                        "Content-Type": "application/json"
                    },
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {
                                        "text": prompt
                                    }
                                ]
                            }
                        ]
                    },
                    timeout=60
                )

                # Handle API response
                if response.status_code == 200:
                    result = response.json()
                    swagger_yaml = result["candidates"][0]["content"]["parts"][0]["text"].strip()

                    # Remove markdown-style code block markers if present
                    if swagger_yaml.startswith("```yaml"):
                        swagger_yaml = swagger_yaml[7:]
                    if swagger_yaml.startswith("```"):
                        swagger_yaml = swagger_yaml[3:]
                    if swagger_yaml.endswith("```"):
                        swagger_yaml = swagger_yaml[:-3]

                    swagger_output.code(swagger_yaml, language="yaml")
                    st.success("✅ Swagger documentation generated successfully!")

                elif response.status_code == 401:
                    st.error("❌ Invalid API key! Please check your Gemini API key.")
                    st.info("💡 Get your API key from: https://aistudio.google.com/")

                elif response.status_code == 429:
                    st.error("❌ Rate limit exceeded! Please wait a moment and try again.")

                elif response.status_code == 400:
                    st.error("❌ Bad request! Please check your API code format.")
                    try:
                        error_details = response.json()
                        st.json(error_details)
                    except:
                        st.text(response.text)
                elif response.status_code == 503:
                    st.error("🚧 Gemini model is currently overloaded. Please wait a few moments and try again.")
                    st.info("This is a temporary issue from Google's side — try again in 1–2 minutes.")
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    st.text(response.text)

            except requests.Timeout:
                st.error("❌ Request timed out! The API is taking too long to respond. Please try again.")

            except requests.ConnectionError:
                st.error("❌ Connection error! Please check your internet connection and try again.")

            except requests.RequestException as e:
                st.error(f"❌ Network error: {str(e)}")

            except KeyError:
                st.error("❌ Unexpected response format from Gemini API")
                try:
                    st.json(response.json())
                except:
                    st.text("Could not parse response")

            except Exception as ex:
                st.error(f"❌ Unexpected error occurred: {str(ex)}")
                st.info("💡 Please check your API code format and try again.")

# Sidebar with instructions and tips
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    **How to use:**
    1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/)
    2. Enter your API key in the input field above
    3. Paste your API code in the left panel
    4. Click "Generate Swagger" to create documentation
    5. Copy the generated YAML from the right panel
    
    **Supported API frameworks:**
    - Flask (Python)
    - FastAPI (Python)
    - Express.js (Node.js)
    - Spring Boot (Java)
    - ASP.NET Core (C#)
    - Ruby on Rails
    - And more...
    
    **Tips:**
    - Include route definitions, parameters, and response models
    - The more detailed your code, the better the documentation
    - Review the generated YAML before using in production
    """)

    st.header("🔧 Troubleshooting")
    st.markdown("""
    **Common issues:**
    - **Invalid API key**: Check your key from AI Studio
    - **Rate limit**: Wait a moment and try again
    - **Timeout**: Try with smaller code snippets
    - **Bad format**: Ensure your API code is complete
    """)

    st.header("🆘 Support")
    st.markdown("""
    If you encounter issues:
    1. Check your API key is valid
    2. Ensure your code is properly formatted
    3. Try with a simpler API example first
    4. Check the error messages for specific guidance
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Built with ❤️ using Streamlit and Google Gemini 2.5 Flash</p>
</div>
""", unsafe_allow_html=True)
