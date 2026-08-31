from app.extraction import client, MODEL


response = client.models.generate_content(
    model=MODEL,
    contents="Return only this exact text: Gemini connection test successful."
)

print(response.text)