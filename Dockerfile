FROM python:3.12-slim

# Create a Working Folder named /app inside the container and moves into it. 
# Every command that follows (like copying files or running scripts) will h
WORKDIR /app

# Print output immediately (no buffering), useful for container logs#
# This sets an environment variable that forces Python to print its terminal outputs immediately rather than buffering them. This is crucial for Docker because it ensures you can see your application's print statements and logs in real-time using -- 'docker logs'.
ENV PYTHONUNBUFFERED=1 

# 1. Install dependencies first (for faster caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the rest of your application files
# Copies the entire 'common' folder tree, including config/setting/
# COPY . .
COPY common/ common/
COPY agents/ agents/
COPY web_services/ web_services/
COPY app.py .
COPY dk_entrypoint_cmd.sh .
RUN chmod +x dk_entrypoint_cmd.sh

# This sets the default entrypoint
ENTRYPOINT ["./dk_entrypoint_cmd.sh"]

# 3. Start the app genericly
CMD ["python", "app.py"]