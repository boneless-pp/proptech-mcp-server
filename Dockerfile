FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server
COPY proptech_mcp_server.py .

# Default: streamable HTTP transport for Railway deployment
ENV MCP_TRANSPORT=streamable_http
ENV MCP_PORT=8080

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/health')" || exit 1

CMD ["python", "proptech_mcp_server.py"]
