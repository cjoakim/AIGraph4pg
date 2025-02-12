# Create a minimal python virtual environment for the purpose of running mkdocs.
# THIS SCRIPT IS FOR THE DEVELOPMENT OF AIGRAPH4PG, NOT FOR END-USERS.
# Chris Joakim, Microsoft

$dirs = ".\venv\", ".\pyvenv.cfg"
foreach ($d in $dirs) {
    if (Test-Path $d) {
        Write-Host "deleting $d"
        del $d -Force -Recurse
    } 
}

Write-Host 'creating new venv ...'
python -m venv .\venv\

Write-Host 'activating new venv ...'
.\venv\Scripts\Activate.ps1

Write-Host 'pip install mkdocs ...'
# https://pypi.org/project/mkdocs-material/
pip install mkdocs-material
pip install mkdocs-material[imaging]

pip list

# Next steps:
# mkdocs build
# mkdocs server
# mkdocs gh-deploy
