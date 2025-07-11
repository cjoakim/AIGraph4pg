# Wrangle the cases.sql file into a much smaller subset of both
# relational data and graph data.
#
# THIS SCRIPT IS FOR THE DEVELOPMENT OF AIGRAPH4PG, NOT FOR END-USERS.
# Chris Joakim, 3Cloud

$tmp_dir = ".\tmp\"
# Check if folder not exists, and create it
if (-not(Test-Path $tmp_dir -PathType Container)) {
    New-Item -path $tmp_dir -ItemType Directory
}

Write-Host "Deleting \tmp files ..."
Remove-Item .\tmp\*.*

Write-Host "Reformatting dev_wrangle_legal_cases.py ..."
black .\dev_wrangle_legal_cases.py

Write-Host "Step 1 ..."
python dev_wrangle_legal_cases.py step1_scan_sqlfile_for_citations /Users/chjoakim/Downloads/cases.sql

Write-Host "Step 2 ..."
python dev_wrangle_legal_cases.py step2_link_cases_from_seeds 10

Write-Host "Step 3 ..."
python dev_wrangle_legal_cases.py step3_extract_subset_from_sqlfile /Users/chjoakim/Downloads/cases.sql tmp/iteration_4.json

Write-Host "Step 4 ..."
python dev_wrangle_legal_cases.py step4_create_cypher_load_file legal_cases tmp/iteration_4.json

Write-Host "Step 5 ..."
python dev_wrangle_legal_cases.py step5_scan_cypher_load_file > tmp/step5_scan_cypher_load_file.txt

Write-Host "Step 6 ..."
python dev_wrangle_legal_cases.py step6_reformat_cases_sql_subset --novectorize

Write-Host "Step 7 ..."
python dev_wrangle_legal_cases.py step7_create_graph_csv_load_files tmp/iteration_4.json

Write-Host "Copying case_url_dict.json to data dir ..."
copy tmp\case_url_dict.json ..\data\legal_cases\case_url_dict.json

Write-Host "done"
