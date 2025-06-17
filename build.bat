@echo off
TITLE YouTube Downloader Pro - Kurulum Sihirbazi

REM --- Betigin Kendi Klasorune Gec ---
cd /d "%~dp0"

ECHO.
ECHO  =================================================================
ECHO           YOUTUBE DOWNLOADER PRO - KURULUM SIHIRBAZI
ECHO  =================================================================
ECHO.
ECHO  Bu sihirbaz, programi bilgisayariniza kurmak icin gerekli
ECHO  tum bilesenleri otomatik olarak indirecek ve yapilandiracaktir.
ECHO.
ECHO  Islem internet baglantiniza ve bilgisayar hizina gore
ECHO  birkac dakika surebilir. Lutfen sabirla bekleyin.
ECHO
ECHO  Bu uyguluma rasitcanbulat tarafindan gelistirilmistir.
ECHO.
pause
CLS

:INSTALL_DEPENDENCIES
ECHO  [1/4] Gerekli Python kutuphaneleri kuruluyor...
ECHO  -----------------------------------------------------------------
python -m pip install --upgrade yt-dlp requests Pillow sv-ttk pyinstaller > nul 2>&1
IF %errorlevel% NEQ 0 ( ECHO  [HATA] Python kutuphaneleri kurulurken bir sorun olustu. & pause & exit /b )
ECHO  Python kutuphaneleri basariyla kuruldu.
ECHO.
timeout /t 1 /nobreak >nul

:INSTALL_FFMPEG
ECHO  [2/4] Video isleme araclari (FFmpeg) kontrol ediliyor...
ECHO  -----------------------------------------------------------------
IF NOT EXIST "ffmpeg.exe" (
    ECHO  FFmpeg bulunamadi, indiriliyor... (Bu islem biraz surebilir)
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"
    IF %errorlevel% NEQ 0 ( ECHO  [HATA] FFmpeg indirilemedi. & pause & exit /b )

    ECHO  Arsiv aciliyor...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"
    IF %errorlevel% NEQ 0 ( ECHO  [HATA] Arsiv acilamadi. & pause & exit /b )

    move "ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" "."
    move "ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe" "."
    rmdir /s /q "ffmpeg-master-latest-win64-gpl"
    del "ffmpeg.zip"
) ELSE (
    ECHO  FFmpeg zaten kurulu.
)
ECHO  Video isleme araclari hazir.
ECHO.
timeout /t 1 /nobreak >nul

:BUILD_EXE
ECHO  [3/4] Program dosyasi (.exe) olusturuluyor...
ECHO  -----------------------------------------------------------------
ECHO  Bu adim en uzun suren kisimdir. Lutfen bekleyin.
SET "ICON_ARG="
IF EXIST "icon.ico" ( SET "ICON_ARG=--icon="icon.ico"" )

python -m PyInstaller --name "YouTube Downloader Pro" --onefile --windowed --clean %ICON_ARG% --add-data "ffmpeg.exe;." --add-data "ffprobe.exe;." "youtube_downloader_gui.py" > build_log.txt 2>&1
IF %errorlevel% NEQ 0 (
    ECHO.
    ECHO  [HATA] EXE OLUSTURMA BASARISIZ OLDU.
    ECHO  Detaylar icin 'build_log.txt' dosyasini kontrol edin.
    pause
    exit /b
)
ECHO  Program dosyasi basariyla olusturuldu.
ECHO.
timeout /t 1 /nobreak >nul

:DEPLOY_AND_CLEAN
ECHO  [4/4] Program Masaustune tasiniyor ve temizlik yapiliyor...
ECHO  -----------------------------------------------------------------
REM Olusturulan .exe dosyasini Masaustu'ne tasi
move "dist\YouTube Downloader Pro.exe" "%USERPROFILE%\Desktop\" > nul 2>&1
IF %errorlevel% NEQ 0 (
    ECHO  [UYARI] Program masaustune tasinamadi.
    ECHO  Lutfen 'dist' klasorunden manuel olarak alin.
) ELSE (
    ECHO  Program basariyla Masaustu'ne tasindi.
)

REM Kurulum sonrasi olusan gereksiz dosyalari temizle
rmdir /s /q "dist"
rmdir /s /q "build"
del "YouTube Downloader Pro.spec"
del "build_log.txt"
ECHO  Gecici kurulum dosyalari temizlendi.
ECHO.
timeout /t 2 /nobreak >nul

:FINISH
CLS
ECHO.
ECHO  =================================================================
ECHO                      KURULUM TAMAMLANDI!
ECHO  =================================================================
ECHO.
ECHO  'YouTube Downloader Pro.exe' programi basariyla
ECHO  Masaustu'nuze kaydedildi.
ECHO.
ECHO  Artik bu pencereyi kapatabilirsiniz. Iyi eğlenceler!
ECHO.
pause
