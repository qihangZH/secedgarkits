conda activate gpunlp3XI
#Get-Location

Set-Location -Path $PSScriptRoot
#python setup.py develop
#pip install .
pip install -e . --config-settings editable_mode=strict

conda activate nusra3X
#Get-Location

Set-Location -Path $PSScriptRoot
#python setup.py develop
#pip install .
pip install -e . --config-settings editable_mode=strict
