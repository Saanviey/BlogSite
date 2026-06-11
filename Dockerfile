#build stage -language and runtime
FROM python:3.12-slim

#make a working directory for your app
WORKDIR /app

#copy needed dependencies and run 
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code and install project
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*"]


# ## Build and Push to Artifact Registry
# gcloud builds submit \
#     --tag us-east4-docker.pkg.dev/YOUR_PROJECT_ID/fastapi-repo/fastapi-app



# ## Deploy to Cloud Run
# gcloud run deploy fastapi-service \
#     --image us-east4-docker.pkg.dev/YOUR_PROJECT_ID/fastapi-repo/fastapi-app \
#     --region us-east4 \
#     --allow-unauthenticated



