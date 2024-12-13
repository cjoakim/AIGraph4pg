# Recreate the python virtual environment and reinstall libs on Windows.
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

Write-Host 'upgrading pip ...'
python -m pip install --upgrade pip 

Write-Host 'install pip-tools ...'
pip install --upgrade pip-tools

Write-Host 'pip-compile requirements.in ...'
pip-compile --output-file .\requirements.txt .\requirements.in

Write-Host 'pip install requirements.txt ...'
pip install -q -r .\requirements.txt

Write-Host 'activating virtual environment ...'
.\venv\Scripts\activate

Write-Host 'displaying python and pip versions ...'
python --version
pip --version

Write-Host 'pip list ...'
pip list


# Enable Long Paths in Windows
# See https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=powershell#enable-long-paths-in-windows-10-version-1607-and-later
# Win Key + X, then Windows Terminal (admin), the run the following PowerShell command:
# New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
