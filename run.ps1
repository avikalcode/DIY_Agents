# Default to 'dev' if no environment argument is passed
param (
    [string]$Env = "dev"
)

Write-Host "🚀 Starting Agentic-Ladder locally in [$Env] environment..." -ForegroundColor Cyan

# 1. Determine which env file to use
$EnvFile = ".env.$Env"
if (-not (Test-Path $EnvFile)) {
    # Fallback to standard .env if the specific environment one doesn't exist
    $EnvFile = ".env"
}

# 2. Parse and load the variables into PowerShell environment memory
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | Where-Object { $_ -match '=' -and -not $_.StartsWith('#') } | ForEach-Object {
        $name, $value = $_ -split '=', 2
        # Trim spaces or quotes if they exist in the file
        $name = $name.Trim()
        $value = $value.Trim().Trim('"').Trim("'")
        
        # Set the environment variable for the current process
        [System.Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Process)
    }
    Write-Host "✅ Loaded environment variables from $EnvFile" -ForegroundColor Green
} else {
    Write-Host "⚠️ Warning: No .env file found. Proceeding with system defaults." -ForegroundColor Yellow
}

# 3. Set the APP_ENV variable so Python knows which TOML file to fetch
$env:APP_ENV = $Env

# 4. Execute the Python application
python app.py
