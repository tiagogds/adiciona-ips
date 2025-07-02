@echo off
REM Script para adicionar IP extra ou reverter interface para DHCP

REM Valores padrão
set "interface=Wi-Fi"
set "ip_extra=192.168.100.99"
set "mascara_extra=255.255.255.0"
set "modo=add"

REM Parse dos argumentos
:parse_args
if "%~1"=="" goto after_parse
if /I "%~1"=="/clean"   set "modo=clean"& shift & goto parse_args
if /I "%~1"=="-c"        set "modo=clean"& shift & goto parse_args
if /I "%~1"=="/iface"    set "interface=%~2"& shift & shift & goto parse_args
if /I "%~1"=="-i"        set "interface=%~2"& shift & shift & goto parse_args
if /I "%~1"=="/ip"       set "ip_extra=%~2"& shift & shift & goto parse_args
if /I "%~1"=="-ip"       set "ip_extra=%~2"& shift & shift & goto parse_args
if /I "%~1"=="/nm"       set "mascara_extra=%~2"& shift & shift & goto parse_args
if /I "%~1"=="-nm"       set "mascara_extra=%~2"& shift & shift & goto parse_args
shift
goto parse_args

goto main

'trecho de parsing dos argumentos adicionado'

:after_parse
REM Não usado, apenas para clareza

goto main

:main
if "%modo%"=="clean" (
    echo Removendo IPs extras da interface %interface%...
    setlocal enabledelayedexpansion
    for /f "tokens=2 delims=: " %%a in ('netsh interface ipv4 show addresses name="%interface%" ^| findstr /I /C:"Endere\u00e7o IP" /C:"IP Address"') do (
        set "ip_remover=%%a"
        echo Removendo IP %ip_remover%
        call :remove_ip
    )
    endlocal
    echo Reestabelecendo interface %interface% para DHCP...
    netsh int ipv4 set address name="%interface%" source=dhcp
    netsh int ipv4 set dnsservers name="%interface%" source=dhcp
    exit /b
)

:remove_ip
REM Remove IPs válidos, exceto 0.0.0.0, 127.0.0.1, 169.254.*.* e 255.255.255.255
if "%ip_remover%"=="0.0.0.0" goto :eof
if "%ip_remover%"=="127.0.0.1" goto :eof
if "%ip_remover:~0,7%"=="169.254" goto :eof
if "%ip_remover%"=="255.255.255.255" goto :eof
if "%ip_remover%"=="" goto :eof
    echo Removendo IP %ip_remover%
    netsh interface ipv4 delete address name="%interface%" addr=%ip_remover%
goto :eof

echo Ativando coexistência DHCP+IP estatico na interface %interface%
netsh interface ipv4 set interface name="%interface%" dhcpstaticipcoexistence=enabled

echo Adicionando IP extra %ip_extra%/%mascara_extra% na interface %interface%
netsh interface ipv4 add address name="%interface%" addr=%ip_extra% mask=%mascara_extra%
