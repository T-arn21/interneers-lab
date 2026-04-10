$ErrorActionPreference = "Stop"

function Run-Step {
    param (
        [string]$Label,
        [string]$Command
    )

    Write-Host ""
    Write-Host "==> $Label"
    Write-Host "    $Command"
    Invoke-Expression $Command
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Step failed: $Label"
        exit $LASTEXITCODE
    }
}

Write-Host "Running regression test suite..."

Run-Step -Label "Unit tests (service)" -Command "python manage.py test products.tests_service_unit"
Run-Step -Label "Integration API tests" -Command "python manage.py test products.tests_integration_api"
Run-Step -Label "Full products test suite" -Command "python manage.py test products"

Write-Host ""
Write-Host "Regression suite completed successfully."
