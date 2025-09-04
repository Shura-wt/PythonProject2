# PowerShell helper to run Docker Compose, compatible with Compose v2 (docker compose) and v1 (docker-compose)
# - Mirrors compose.sh behavior on Windows
# - For docker-compose v1, sets DOCKER_API_VERSION=1.41 to avoid KeyError: 'ContainerConfig' with recent Docker Engine

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

$ErrorActionPreference = 'Stop'

function Has-DockerComposeV2 {
    try {
        $null = & docker compose version 2>$null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

function Has-DockerComposeV1 {
    try {
        $null = Get-Command docker-compose -ErrorAction Stop
        return $true
    } catch { return $false }
}

if (Has-DockerComposeV2) {
    & docker compose @ComposeArgs
    exit $LASTEXITCODE
}
elseif (Has-DockerComposeV1) {
    # Workaround for docker-compose v1 with newer Docker Engine APIs
    $env:DOCKER_API_VERSION = '1.41'
    & docker-compose @ComposeArgs
    exit $LASTEXITCODE
}
else {
    Write-Error "Neither 'docker compose' (v2) nor 'docker-compose' (v1) is available in PATH. Please install Docker Compose."
    exit 1
}
