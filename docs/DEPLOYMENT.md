# Deployment Notes

## Local deployment
Run `python app.py` and open `http://127.0.0.1:7860`.

## Hugging Face Spaces (Gradio)
1. Create a new Space and choose Gradio.
2. Upload `app.py`, `summarizer.py`, `url_extractor.py`, `utils.py`, and `requirements.txt`.
3. Confirm the Space runtime can install CPU PyTorch and download the model from Hugging Face.
4. Test with pasted text first, then with a public article URL.
5. Review memory and cold-start time; model loading may be slow on limited hardware.

## Security and operations
- Do not expose debugging tracebacks to users.
- Use rate limits and request limits before making the app public.
- The URL extractor includes basic URL checks, but they are not a complete SSRF defense. For public deployment, isolate URL fetching and restrict outbound traffic at the network/firewall level; consider a dedicated fetch service.
- Add monitoring and clear error handling.
- Respect website terms, copyright, and access controls. Do not bypass paywalls, logins, CAPTCHAs, or anti-bot protections.
- A free deployment may sleep, be slow, or run out of memory. Do not promise real-time performance without measuring it.
