# GIT
## Part1
```
git init -b main
git config user.name "Your Name"
git config user.email "you@example.com"

git add .
git status            # check: no .env, no logs/, no __pycache__ in the list
git commit -m "Level 0: HelloAgent class with Setting Logger, audit and Docker support"

git remote add origin <your-repo-url>
git push -u origin main

git tag -a agent-1 -m "Agent 1: hello world with config and logging"
git push origin agent-1
```
## Part 2: for each new agent (Agent 2 now)
**1. Start from an up-to-date main, on a new branch**
```bash
git switch main
git pull
git switch -c agent-2-llm
```
**2. Build Agent 2 and test it locally.**

**3.Check it in Docker before committing**
If it works here, it will work in the cloud. The --build matters, because without it compose may reuse the old image.
```bash
docker compose up --build
```

**4. Commit in small steps**
Several small commits are better than one big one, for example “add package”, “add agent class”, “wire into app.py”, “add tests”.
```bash
git status                     # again: no .env
git add agents/agent_2_llm requirements.txt .env.example app.py
git commit -m "Agent 2: add LLM agent that calls the model"
```
**5. Push the branch and merge it**
```bash
git push -u origin agent-2-llm
```

Then open a Pull Request on GitHub and merge it, even though you work alone. You get a clear record, and CI runs on the PR if you keep the workflow. Or merge locally:
```bash
git switch main
git merge agent-2-llm
git push
```
**6. Tag the milestone**
```bash
git switch main
git pull
git tag -a agent-2 -m "Agent 2: first LLM call"
git push origin agent-2
```

**7. Clean up**
```bash
git branch -d agent-2-llm
git push origin --delete agent-2-llm
```

** Going back to an earlier agent **
```bash
git checkout agent-1                 # look around (read-only "detached" state)
git switch -c experiment agent-1     # or start new work from that point
git switch main                      # return to the latest
```

**remove from git local if unwanted file got in before pushing / commiting to remote (origin)**
```
git status
git rm --cached <filename> # use * if want to remove all
git status 
```
**add specific file to local**
```
**git add <file1> <file1>
```
# Enviornments
## config.toml parameters change per environment
Split config into environment-specific files:

• **config.dev.toml**

• **config.test.toml**

• **config.prod.toml**

## Make (makefile) / Shell script (bash)
### make
• To start dev: **make dev**


• To start prod: **make prod**


• To stop everything: **make stop**
## How does the container get environment variables
**Method A: Passing the entire .env file at runtime (Best Practice)**
```
docker run --rm --env-file .env.dev agentic-ladder:level0
```
**Method B: Passing a single variable explicitly**
```
docker run --rm -e APP_ENV=dev -e OPEN_AI_Key=abcd1234 agentic-ladder:level0
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

#--entrypoint ls: This is the override engine. It tells Docker to completely ignore the CMD ["python", "app.py"] instruction written at the bottom of your Dockerfile. Instead of booting up Python, it commands the container to open the standard Linux file listing tool (ls).

# • -la /app: These are the specific parameter instructions passed directly to the ls command:
#  -l: Long format (shows file sizes, permissions, owners, and modification dates).
#  -a: All files (shows hidden configuration objects like your __init__.py files).
#  /app: Tells the tool to target your WORKDIR folder.

# 1. Find the CONTAINER ID of your running app
docker ps
# 2. Inspect its environment settings directly
docker inspect <container_id_or_name> --format='{{range .Config.Env}}{{println .}}{{end}}'

```
### 1. Delete a File Inside a Running Container (Quick / Temporary Fix)
```
docker ps
docker exec -it <container_id_or_name> rm /app/path/to/file.txt
```
### 2. Delete a File Permanently in Your Image (Best Practice). Rebuild your image so the file is never included in the final layers
```
RUN rm /app/unwanted_file.txt
docker build -t hello-agent:level0 .
```
## docker-compose.yml
- loads .env and mounts ./logs to read logs on host machine
- Compose won’t be what runs in the cloud, since Cloud Run, ECS, Kubernetes and similar platforms take the image built from the Dockerfile
```bash
# Windows PowerShell Example
$env:APP_ENV="dev"
docker compose up -d --build

# Linux
APP_ENV=dev docker compose up -d --build
```

• **up**: Tells Docker to create, configure, and start the containers.


• **-d**: (Detached mode): Runs the containers in the background, freeing up your terminal window.


• **--build**: Tells Docker to check your Dockerfile for changes and rebuild the Python image. Always use this flag if you edit your Python code or update requirements.txt.


`docker compose logs -f` To view live container logs

`docker compose down` To stop the running application

`docker compose down -v` To stop the application AND delete the container logs volume data to start completely fresh: