
# Recreate the python virtual environment and reinstall libs on Windows 11
# using a "modern" python toolchain which includes uv and pyproject.toml
# rather than pip and requirements.in.
# Chris Joakim, 2025

Write-Host "Pruning files..."
$locations = ".\.venv\", ".\.coverage", ".\.pytest_cache", "htmlcov", "out", "tmp"
foreach ($loc in $locations) {
    if (Test-Path $loc) {
        Write-Host "deleting $loc"
        del $loc -Force -Recurse
    }
}

mkdir out
mkdir tmp 

Write-Host "Creating a new virtual environment in .venv..."
uv venv

Write-Host "Activating the virtual environment..."
.\.venv\Scripts\activate

Write-Host "Installing libraries..."
uv pip install --editable .

Write-Host "Creating a tmp\requirements.txt file..."
uv pip compile pyproject.toml -o tmp\requirements.txt

Write-Host "Displaying uv tree..."
uv tree
