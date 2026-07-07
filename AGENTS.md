# Versionado Semántico

Este proyecto sigue [SemVer 2.0.0](https://semver.org/lang/es/).

## Esquema

```
v<MAJOR>.<MINOR>.<PATCH>
```

- **MAJOR**: Cambios incompatibles en el API o ruptura de funcionalidad existente.
- **MINOR**: Nueva funcionalidad compatible hacia atrás (ej: nuevo formato, nueva característica).
- **PATCH**: Corrección de bugs, optimizaciones, mejoras internas sin nueva funcionalidad.

## Archivo de versión

La versión actual se define únicamente en `VERSION` (raíz del proyecto).  
Los scripts de empaquetado (`empaquetar_mac.sh`, `empaquetar_windows.bat`) leen de ahí.

## Al liberar una versión

```bash
git tag v<MAYOR>.<MENOR>.<PARCHE>
git push origin v<MAYOR>.<MENOR>.<PARCHE>
```

Esto dispara el CI/CD (GitHub Actions) que compila los ejecutables y crea el Release.

## Historial

| Tag   | Cambios |
|-------|---------|
| v1.0.0 | Versión inicial: conversión de imágenes, audio y video |
| v1.1.0 | Extracción de audio desde video + transcripción Vosk |
