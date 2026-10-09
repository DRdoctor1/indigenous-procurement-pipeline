@echo off
set PYTHONIOENCODING=utf-8
cd /d "D:\indigenous_market_pipeline"
python tender_auditor.py >> pipeline_execution.log 2>&1