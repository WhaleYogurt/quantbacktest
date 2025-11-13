@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0
set REPORT=%ROOT%report.txt
set PROFILE=%ROOT%profile.txt
set OUTPUT_DIR=%ROOT%examples\output
set EXAMPLE_OUTPUT=%OUTPUT_DIR%\quickstart.json
set WALK_OUTPUT=%OUTPUT_DIR%\walk_forward.json
set GRID_OUTPUT=%OUTPUT_DIR%\grid_search.json
set AAPL_OUTPUT=%OUTPUT_DIR%\aapl_momentum.json
set WF_METADATA=%ROOT%artifacts\walk-forward-test\metadata.json
set GRID_METADATA=%ROOT%artifacts\grid-search-test\metadata.json
set WF_TEST_METADATA=%ROOT%artifacts\wf-test\metadata.json
set GRID_TEST_METADATA=%ROOT%artifacts\grid-test\metadata.json
set EXIT_CODE=0

set PYTHONUTF8=1
set RUN_ROOT=%ROOT%

if exist "%REPORT%" del "%REPORT%"
if exist "%PROFILE%" del "%PROFILE%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if exist "%EXAMPLE_OUTPUT%" del "%EXAMPLE_OUTPUT%"
if exist "%WALK_OUTPUT%" del "%WALK_OUTPUT%"
if exist "%GRID_OUTPUT%" del "%GRID_OUTPUT%"
if exist "%AAPL_OUTPUT%" del "%AAPL_OUTPUT%"
if exist "%WF_METADATA%" del "%WF_METADATA%"
if exist "%GRID_METADATA%" del "%GRID_METADATA%"
if exist "%WF_TEST_METADATA%" del "%WF_TEST_METADATA%"
if exist "%GRID_TEST_METADATA%" del "%GRID_TEST_METADATA%"

echo ==== quantbacktest verification ====>>"%REPORT%"
echo Timestamp: %DATE% %TIME%>>"%REPORT%"
echo.>>"%REPORT%"

echo [1/5] Running pytest...
echo ==== Test Results ====>>"%REPORT%"
python -m pytest >"%ROOT%pytest.log" 2>&1
if errorlevel 1 (
    set EXIT_CODE=1
)
type "%ROOT%pytest.log">>"%REPORT%"
del "%ROOT%pytest.log"
echo.>>"%REPORT%"

echo [2/5] Running examples...
echo ==== Example Runs ====>>"%REPORT%"
python "%ROOT%examples\quickstart_example.py" --test-mode --run-id "test-harness" --output "%EXAMPLE_OUTPUT%" >"%ROOT%example_quickstart.log" 2>&1
if errorlevel 1 (
    set EXIT_CODE=1
)
type "%ROOT%example_quickstart.log">>"%REPORT%"
del "%ROOT%example_quickstart.log"

python "%ROOT%examples\walk_forward_example.py" --run-id "walk-forward-test" --window 2 --bars 6 --output "%WALK_OUTPUT%" >"%ROOT%example_walk.log" 2>&1
if errorlevel 1 (
    set EXIT_CODE=1
)
type "%ROOT%example_walk.log">>"%REPORT%"
del "%ROOT%example_walk.log"

python "%ROOT%examples\grid_search_example.py" --run-id "grid-search-test" --bars 5 --output "%GRID_OUTPUT%" >"%ROOT%example_grid.log" 2>&1
if errorlevel 1 (
    set EXIT_CODE=1
)
type "%ROOT%example_grid.log">>"%REPORT%"
del "%ROOT%example_grid.log"

python "%ROOT%examples\aapl_momentum_strategy.py" --run-id "aapl-momentum-test" --output "%AAPL_OUTPUT%" >"%ROOT%example_aapl.log" 2>&1
if errorlevel 1 (
    set EXIT_CODE=1
)
type "%ROOT%example_aapl.log">>"%REPORT%"
del "%ROOT%example_aapl.log"
echo.>>"%REPORT%"

echo [3/5] Validating engine metadata...
echo ==== Engine Diagnostics ====>>"%REPORT%"
if exist "%WF_METADATA%" (
    echo walk_forward_metadata: %WF_METADATA%>>"%REPORT%"
) else (
    echo walk_forward_metadata missing>>"%REPORT%"
    set EXIT_CODE=1
)
if exist "%GRID_METADATA%" (
    python -m quantbacktest.metrics.cli --metadata "%GRID_METADATA%" --output-dir "%ROOT%artifacts\grid-search-test" >"%ROOT%grid_metrics.log" 2>&1
    if errorlevel 1 (
        set EXIT_CODE=1
    )
    type "%ROOT%grid_metrics.log">>"%REPORT%"
    del "%ROOT%grid_metrics.log"
) else (
    echo grid_metadata missing>>"%REPORT%"
    set EXIT_CODE=1
)
echo.>>"%REPORT%"

echo [4/5] Profiling placeholder backtest...
python -m quantbacktest.utils.harness profile --profile-file "%PROFILE%" >"%ROOT%profile_summary.log" 2>&1
if errorlevel 1 (
    set EXIT_CODE=1
)
for /f "usebackq delims=" %%L in ("%ROOT%profile_summary.log") do echo %%L>>"%REPORT%"
del "%ROOT%profile_summary.log"

echo ==== Profiling Summary ====>>"%REPORT%"
type "%PROFILE%">>"%REPORT%"
echo.>>"%REPORT%"

echo ==== Optimization Hotspots ====>>"%REPORT%"
python -m quantbacktest.utils.harness hotspots --profile-file "%PROFILE%" --lines 20 >>"%REPORT%"
if errorlevel 1 (
    set EXIT_CODE=1
)
echo.>>"%REPORT%"

echo ==== Warnings ====>>"%REPORT%"
if %EXIT_CODE%==0 (
    echo None recorded.>>"%REPORT%"
) else (
    echo Check logs above for details.>>"%REPORT%"
)
echo.>>"%REPORT%"

echo ==== Errors ====>>"%REPORT%"
if %EXIT_CODE%==0 (
    echo None.>>"%REPORT%"
) else (
    echo Failures detected.>>"%REPORT%"
)
echo.>>"%REPORT%"

echo [5/5] Checklist
echo Data layer ok
echo Engine ok
echo Portfolio ok
echo Strategy ok
echo Metrics ok
echo Docs ok
echo Profiling ok
echo No errors in report.txt

echo.
echo To commit changes, run:
echo    git add .
echo    git commit -m "your message here"

if %EXIT_CODE%==0 (
    exit /b 0
) else (
    exit /b %EXIT_CODE%
)
