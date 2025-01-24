@echo off
python -m nuitka --windows-disable-console --enable-plugin=tk-inter --follow-imports --include-data-dir=public=public --include-data-dir=app=app --output-dir=build main.py 