from langchain_google_genai import GoogleGenerativeAI


llm = GoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="YOUR_GOOGLE_API_KEY",
    temperature=0.7
)

response = llm.invoke("Explain the theory of relativity in simple terms.")
print(response)