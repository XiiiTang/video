@echo off
chcp 65001 > nul
cd /d "%~dp0"

:menu
echo 视频下载器
echo.
echo 1. 添加新的下载配置
echo 2. 全部下载
echo 3. 选择下载
echo 4. list all url
echo 5. exit
echo.

set /p choice=请选择操作 (1-5): 

if "%choice%"=="1" goto add_config
if "%choice%"=="2" goto download_all
if "%choice%"=="3" goto select_download
if "%choice%"=="4" goto list_configs
if "%choice%"=="5" goto exit_program
goto invalid_choice

:add_config
python download.py add
goto end

:download_all
python download.py download
if %errorlevel% equ 0 (
    echo.
    echo 下载完成，正在运行字幕合并...
    python merge_ass_srt.py
    if %errorlevel% equ 0 (
        echo 字幕合并完成！
    ) else (
        echo 字幕合并失败！
    )
) else (
    echo 下载失败！
)
goto end

:select_download
python download.py select
if %errorlevel% equ 0 (
    echo.
    echo 下载完成，正在运行字幕合并...
    python merge_ass_srt.py
    if %errorlevel% equ 0 (
        echo 字幕合并完成！
    ) else (
        echo 字幕合并失败！
    )
) else (
    echo 下载失败！
)
goto end

:list_configs
python download.py list
goto end

:exit_program
exit

:invalid_choice
echo 无效选择
goto end

:end
pause
goto menu
