# invoice-extractor

Extract infomation out of invoice

Run the following commands to run the application

● build and run the Dockerfile

● export HF_API_TOKEN= put your hugging face token

● docker run -p 8501:8501 -e HF_API_TOKEN=$HF_API_TOKEN invoice-extractor

Generate a new API token with full permissions:

● Go to Hugging Face Tokens
● Click New token
● Select "Write" or "Read" (avoid "None")
● Copy the new token and replace it in your code.
