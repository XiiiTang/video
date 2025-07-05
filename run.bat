@echo off
chcp 65001 > nul
cd /d "%~dp0"

:menu
echo 视频下载器
echo.
echo 1. 添加新的下载配置
echo 2. 开始下载
echo 3. exit
echo.

set /p choice=请选择操作 (1-3): 

if "%choice%"=="1" goto add_config
if "%choice%"=="2" goto download
if "%choice%"=="3" goto exit_program
goto invalid_choice

:add_config
python download.py add
goto end

:download
python download.py download
goto end

:exit_program
exit

:invalid_choice
echo 无效选择
goto end

:end
pause
goto menu
