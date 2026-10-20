# Read-only wrapper. Python 3.9+; preserves the validator's exit status.
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$SkillRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
$validatorPath = Join-Path $PSScriptRoot 'validate-skill.py'
$pythonCommand = $null
$pythonPrefix = @()

# Probe interpreters because Windows may expose an unusable Store alias.
foreach ($candidate in @('python3', 'python', 'py')) {
    $command = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $command) { continue }
    $probePrefix = @()
    if ($candidate -eq 'py') { $probePrefix = @('-3') }
    try {
        & $command.Source @probePrefix -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $pythonCommand = $command.Source
            $pythonPrefix = $probePrefix
            break
        }
    } catch {
        # Try the next available interpreter; do not install anything.
    }
}

if ($null -eq $pythonCommand) {
    [Console]::Error.WriteLine('Python 3.9+ is required. No dependencies will be installed.')
    exit 1
}

$validatorArguments = @($validatorPath, $SkillRoot)
if ($Json) { $validatorArguments += '--json' }
& $pythonCommand @pythonPrefix @validatorArguments
exit $LASTEXITCODE
