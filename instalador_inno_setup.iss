[Setup]
; Nombre de la aplicación
AppName=Conversor Multimedia Pro
AppVersion=1.0
AppPublisher=Cesar David Oliveros Barajas
AppPublisherURL=https://github.com/CesarDavidOliverosBarajas/Conversor-de-formato-archivos-multimedia
AppSupportURL=https://github.com/CesarDavidOliverosBarajas/Conversor-de-formato-archivos-multimedia/issues
; El nombre del instalador ejecutable final
OutputBaseFilename=Instalador_Conversor_Multimedia_Pro
; Carpeta de salida donde Inno Setup dejará el instalador
OutputDir=dist
; Carpeta predeterminada donde se instalará en Windows ("Program Files" típicamente)
DefaultDirName={autopf}\Conversor Multimedia Pro
; Permite usar la app sin ser administrador
PrivilegesRequired=lowest
; Evitar que pregunte crear carpeta en Program Files
DirExistsWarning=no
; Ícono para el instalador y panel de control
SetupIconFile=app.ico
UninstallDisplayIcon={app}\Conversor_Multimedia_Pro.exe

[Files]
; Tomar el EXE compilado (que ya contiene FFmpeg dentro) y copiarlo
Source: "dist\Conversor_Multimedia_Pro.exe"; DestDir: "{app}"; Flags: ignoreversion
; (Opcional) Si quieres copiar también el icono en la carpeta de instalación
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Crear acceso directo en el Menú Inicio
Name: "{autoprograms}\Conversor Multimedia Pro"; Filename: "{app}\Conversor_Multimedia_Pro.exe"; IconFilename: "{app}\app.ico"
; Crear acceso directo en el Escritorio
Name: "{autodesktop}\Conversor Multimedia Pro"; Filename: "{app}\Conversor_Multimedia_Pro.exe"; IconFilename: "{app}\app.ico"

[Run]
; Permitir a los usuarios iniciar la app al finalizar de instalar
Filename: "{app}\Conversor_Multimedia_Pro.exe"; Description: "Ejecutar Conversor Multimedia Pro"; Flags: nowait postinstall skipifsilent
