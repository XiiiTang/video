@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo 初始化 conda 环境...
:: 设置 conda 路径
set "CONDA_PATH=E:\anaconda3"
set "PATH=%CONDA_PATH%;%CONDA_PATH%\Scripts;%CONDA_PATH%\Library\bin;%PATH%"

:: 初始化 conda
call "%CONDA_PATH%\Scripts\activate.bat" "%CONDA_PATH%"

echo 使用 video conda 环境运行...

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
call conda activate video
python download.py add
goto end

:download_all
call conda activate video
python download.py download
if %errorlevel% equ 0 (
    echo.
    echo 下载完成，正在运行批量转换...
    python batch_convert.py
    if %errorlevel% equ 0 (
        echo 批量转换完成，正在运行字幕合并...
        python merge_ass_srt.py
        if %errorlevel% equ 0 (
            echo 字幕合并完成！
        ) else (
            echo 字幕合并失败！
        )
    ) else (
        echo 批量转换失败！
    )
) else (
    echo 下载失败！
)
goto end

:select_download
call conda activate video
python download.py select
if %errorlevel% equ 0 (
    echo.
    echo 下载完成，正在运行批量转换...
    python batch_convert.py
    if %errorlevel% equ 0 (
        echo 批量转换完成，正在运行字幕合并...
        python merge_ass_srt.py
        if %errorlevel% equ 0 (
            echo 字幕合并完成！
        ) else (
            echo 字幕合并失败！
        )
    ) else (
        echo 批量转换失败！
    )
) else (
    echo 下载失败！
)
goto end

:list_configs
call conda activate video
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
