# PowerShell script to set the necessary AIG4PG_ environment variables,
# Edit ALL of these generated values per your actual deployments.

Write-Host "Setting AIG4PG environment variables ..."

Write-Host 'setting AIG4PG_LLM_CONTEXT_MAX_NTOKENS'
[Environment]::SetEnvironmentVariable("AIG4PG_LLM_CONTEXT_MAX_NTOKENS", "0", "User")

Write-Host 'setting AIG4PG_LOG_LEVEL'
[Environment]::SetEnvironmentVariable("AIG4PG_LOG_LEVEL", "info", "User")

Write-Host 'setting AIG4PG_OPENAI_COMPLETIONS_DEP'
[Environment]::SetEnvironmentVariable("AIG4PG_OPENAI_COMPLETIONS_DEP", "gpt4", "User")

Write-Host 'setting AIG4PG_OPENAI_EMBEDDINGS_DEP'
[Environment]::SetEnvironmentVariable("AIG4PG_OPENAI_EMBEDDINGS_DEP", "embeddings", "User")

Write-Host 'setting AIG4PG_OPENAI_KEY'
[Environment]::SetEnvironmentVariable("AIG4PG_OPENAI_KEY", "", "User")

Write-Host 'setting AIG4PG_OPENAI_URL'
[Environment]::SetEnvironmentVariable("AIG4PG_OPENAI_URL", "", "User")

Write-Host 'setting AIG4PG_PG_AGE_GRAPH_NAME'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_AGE_GRAPH_NAME", "legal_cases", "User")

Write-Host 'setting AIG4PG_PG_FLEX_DB'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_DB", "", "User")

Write-Host 'setting AIG4PG_PG_FLEX_PASS'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_PASS", "", "User")

Write-Host 'setting AIG4PG_PG_FLEX_PORT'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_PORT", "5432", "User")

Write-Host 'setting AIG4PG_PG_FLEX_SERVER'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_SERVER", "", "User")

Write-Host 'setting AIG4PG_PG_FLEX_USER'
[Environment]::SetEnvironmentVariable("AIG4PG_PG_FLEX_USER", "", "User")

Write-Host 'setting LOCAL_PG_PASS'
[Environment]::SetEnvironmentVariable("LOCAL_PG_PASS", "", "User")

Write-Host "done"
