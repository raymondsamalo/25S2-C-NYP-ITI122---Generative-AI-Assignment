import ollama
from app.dependencies import customer_info_service,db, customer_residency_status_service, CONFIG
model = CONFIG.model.version
response = ollama.generate(model=model, prompt='Why is the sky blue?')
print(response['response'])


