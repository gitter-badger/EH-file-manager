python -c "import ehfilemanager; print ehfilemanager.__version__" > tmpFile 
set /p VERSION= < tmpFile 
del tmpFile 
echo VERSION=%VERSION%

RMDIR /S /Q build
RMDIR /S /Q dist

pyinstaller -F -w -n ehfilemanager ehfilemanager/__main__.py
pyinstaller -F -n ehfilemanager_cli ehfilemanager/__main__.py

copy .\README.* .\dist\
copy .\INSTALL.* .\dist\
copy .\LICENSE.* .\dist\
git archive --format zip --output .\dist\ehfilemanager_%VERSION%_source.zip master
python build_win_compress.py %VERSION% %PROCESSOR_ARCHITECTURE%
