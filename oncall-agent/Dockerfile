FROM python:3.12-slim
WORKDIR /app
COPY agent.py .
RUN pip install fastapi uvicorn
EXPOSE 8090
CMD ["python","agent.py"]
