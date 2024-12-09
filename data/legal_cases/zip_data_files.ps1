

Write-Host "Producing zip files ..."
ant -f .\zip_data_files.xml

Write-Host "Directory listing after producing zip files ..."
dir

Write-Host "Listing contents of age_load_statments.zip ..."
jar tvf age_load_statments.zip

Write-Host "Listing contents of legal_cases.zip ..."
jar tvf legal_cases.zip

Write-Host "done"
