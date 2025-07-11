# Generate artifacts - markdown docs, etc.
# THIS SCRIPT IS FOR THE DEVELOPMENT OF AIGRAPH4PG, NOT FOR END-USERS.
# Chris Joakim, 3Cloud

param ($deploy_generated='nodeploy')

$tmp_dir = ".\tmp\"
$docs_dir = "..\docs\"
$python_dir = "."

# Check if folder not exists, and create it
if (-not(Test-Path $tmp_dir -PathType Container)) {
    New-Item -path $tmp_dir -ItemType Directory
}

Write-Host "Deleting \tmp files ..."
Remove-Item .\tmp\*.*

python dev_main.py gen_all

if ($deploy_generated -eq 'deploy') {
    Write-Host "deploying generated files ..."
    Copy-Item .\tmp\*.md  $docs_dir
}

Write-Host "Reformatting python source code ..."
black *.py
black src 

Write-Host "done"
