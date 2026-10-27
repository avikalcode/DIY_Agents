**Docker**
```bash
docker compose up --build
```

# Execute application
To run multi-environment setup directly on  Windows terminal using PowerShell without Docker, ii would need  two things:
<mark style="background-color: lightgreen;">
<br>    1. Set the environment variable (APP_ENV) in PowerShell syntax.
<br>    2. Read the local .env files, since PowerShell doesn't automatically load them like Docker Compose does.
</mark>  

## Phase 1: One-Time Local Environment Setup
```
# 1. Create a virtual environment named '.venv' in your project folder
python -m venv .venv

# 2. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 3. Install all project libraries (OpenAI, Pinecone, etc.)
pip install -r requirements.txt
```

## Phase 2: Running App 
### Manually (Per Environment)
```
POWERSHELL
-----------
# 1. Set the environment variable for your Python TOML loader
`$env:APP_ENV="dev"`

# 2. Manually set your secret keys for the current terminal session
`$env:OPENAI_API_KEY="sk-proj-your-dev-key-here"
$env:PINECONE_API_KEY="pcsk_your-dev-key-here"`

# 3. Start your app
`python app.py`

Verify
------
$env:APP_ENV
$env:OPENAI_API_KEY

Clear variable
---------------
$env:OPENAI_API_KEY=$null
```

### through script 
**Python script picks it up dynamically and pulls the correct TOML file out of the common/config/resource/ folder**

File named `run.ps1` in project's root folder. This script will automatically 

- read .env file,

- inject the keys

- set  target environment

- launch Python

```bash
chmod +x run.sh
• For Dev: ./run.sh or ./run.sh dev
• For Test: ./run.sh test
• For Prod: ./run.sh prod
```
** Troubleshoot **
If Windows blocks from running the script with an error saying `script execution is disabled on this system`, then  bypass the security policy for that session. Run it like this instead:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
/run.sh dev
```




# DOCKER
## Dockerfile
--Cloud Run, ECS, Kubernetes and similar platforms take the image built from the Dockerfile

-- run `docker compose up`, Docker automatically feeds the environment variable (APP_ENV) into the container from the outside.
```bash
python app.py (python -m app)          # run locally

docker build -t agentic-ladder:level0  .   # build the image 
                                       #(The Dot at the end): This is the Build Context. It tells  Docker to look in #current working directory for the files it needs to copy into the 
                                       #image, and where to find the text file named Dockerfile.

docker run --rm agentic-ladder:level0      # prints: Hello, World!
                                    # --rm (Remove automatically): A cleanup flag. It tells Docker to completely 
                                    #delete the container's internal file footprint from computer's memory as soon 
                                    # as the program finishes executing. This prevents old, dead container storage 
                                    # from cluttering up machine's hard drive.
docker run --rm 
            --env-file .env.dev 
            -e APP_ENV=dev 
            --entrypoint dk_entrypoint_cmd.sh
            agentic-ladder:level0

docker run --rm --entrypoint ls agentic-ladder:level0 -la /app
```

## docker-compose.yml
```bash
# Windows PowerShell Example
$env:APP_ENV="dev"
docker compose up -d --build

# Linux
APP_ENV=dev docker compose up -d --build
```