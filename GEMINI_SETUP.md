# Gemini AI Analysis — ExtractIQ

The existing PDF extraction and document search work without a Gemini key. Gemini is an optional **opt-in** feature on the **Review** tab of the standalone Streamlit deployment.

## Configure

1. Create a Gemini API key through [Google AI Studio](https://aistudio.google.com/apikey). Verify pricing and quotas for your account before use.
2. Open your Streamlit Community Cloud application settings and select **Secrets**.
3. Add this TOML entry, replacing the placeholder with your actual key (never commit keys to GitHub):

   ```toml
   GEMINI_API_KEY = "YOUR_PRIVATE_KEY_HERE"
   ```

4. Save and reboot/redeploy the application if required.
5. Upload a **synthetic or public text-based PDF**, go to **Review**, check the opt-in consent and choose **Summary** or **Structured extraction**, then click **Analyze with Gemini**.

For local use you can export GEMINI_API_KEY as an environment variable, or use an ignored `.streamlit/secrets.toml` file.

## Implementation and safety

- `frontend/gemini_features.py` calls Google's current `google-genai` Python SDK using `gemini-2.5-flash`.
- Only a user click after a consent checkbox sends document text to the model.
- Document instructions are treated as untrusted source text; the prompt requests grounded answers and marks missing fields.
- Only the **first 16,000 extracted characters** are analyzed; a warning appears if truncated.
- Structured mode expects valid JSON and rejects invalid JSON.
- The result is advisory: users must verify outputs against the source document.
- No Gemini API key means this feature is disabled; classic extraction, search and dashboard remain usable.
- Avoid sensitive, confidential, medical patient, or regulated data unless a separately reviewed compliant arrangement exists.
- The feature currently works only in embedded (standalone) Streamlit mode, not a separate FastAPI-only deployment.
- An LLM provider outage may produce an error; it does not affect the existing extraction results.

## Testing

Run: `python -m pytest tests/test_gemini_features.py -q`

The tests mock the Gemini client and need no key. They cover prompt grounding, input validation, response parsing and failure handling. **These tests do not measure model accuracy or prove resistance to prompt injection.** Conduct real evaluation on publicly shareable annotated documents separately.
