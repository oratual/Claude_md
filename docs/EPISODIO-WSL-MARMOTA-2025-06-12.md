# 📖 EPISODIO: "El Día de la Marmota de WSL" - 12/06/2025

## 🎬 Resumen Ejecutivo

Lo que empezó como una simple lectura de CLAUDE.md se convirtió en una odisea de 2 horas resolviendo la inestabilidad crónica de WSL2. El sistema se congelaba cada 30 minutos, corrompiendo Claude Desktop en el proceso. La causa raíz: configuración extremadamente restrictiva (4GB RAM) + WSLg inestable.

## 📊 Diagnóstico Inicial

### Síntomas Presentados:
1. WSL se congelaba repetidamente (~cada 30 min)
2. Claude Desktop se corrompía cuando WSL fallaba
3. Comandos tardaban en responder o daban timeout
4. Scripts de voz dejaban de funcionar
5. Error recurrente ID -1610612736 en logs de Windows

### Hallazgos del Análisis:
- **Xorg crasheando constantemente** con señal SIGABRT
- **PulseAudio en bucle infinito** de reinicios
- **Servicios gráficos fallidos**: lightdm, xrdp, xrdp-sesman
- **Memoria insuficiente**: Solo 4GB asignados a WSL
- **Journal corrupto** del usuario

## 🔍 Descubrimientos Críticos

### 1. El Incidente del c2w
Durante el diagnóstico, el usuario ejecutó `c2w` que sobrescribió la versión Windows de DiskDominator con la versión Linux. Pánico justificado: "días de trabajo" en riesgo.

**Acción de emergencia**:
- Backup inmediato a `H:\Backup\WSL\2025-06-12\DiskDominator-Windows-EMERGENCY-BACKUP` (472MB)
- Exclusión de DiskDominator en `projects.conf` para prevenir futuras sobreescrituras

### 2. Recursos del Sistema Subutilizados
El usuario tiene un **Ryzen 9 5900X (24 threads) + 64GB RAM** pero WSL estaba configurado con:
- Solo 4GB de RAM (6.25% del total)
- Solo 2 procesadores (8.3% del total)

### 3. WSLg Como Fuente de Inestabilidad
Los logs mostraban crashes continuos de Xorg con múltiples PIDs fallando simultáneamente. WSLg (el subsistema gráfico) era la principal fuente de inestabilidad.

## 🛠️ Soluciones Implementadas

### 1. Configuración Optimizada (.wslconfig)
```ini
[wsl2]
memory=48GB             # De 4GB → 48GB (75% del total)
processors=20           # De 2 → 20 threads
swap=0                  # Eliminado - innecesario con 48GB
guiApplications=false   # WSLg DESHABILITADO
networkingMode=mirrored
dnsTunneling=true
firewall=true

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
```

### 2. Servicios Problemáticos Enmascarados
```bash
sudo systemctl mask lightdm.service xrdp.service xrdp-sesman.service
sudo systemctl reset-failed
```

### 3. Monitor de Salud Creado
Script `wsl-claude-monitor.sh` que detecta:
- Timeouts en comandos básicos
- Estado de memoria y procesos
- Genera reportes automáticos de crashes

## 📈 Resultados

### Antes:
- Estado: `degraded`
- RAM disponible: 3.8GB
- Crashes cada ~30 minutos
- Timeouts constantes

### Después:
- Estado: `running` ✅
- RAM disponible: 45GB de 47GB
- Tiempo de respuesta: **3ms**
- Sin crashes detectados
- Carga del sistema: 0.08

## 🎓 Lecciones Aprendidas

1. **WSL2 necesita recursos generosos**: Con 64GB de RAM, asignar 4GB era absurdamente restrictivo
2. **WSLg puede ser más problema que solución**: Si no necesitas GUI Linux, mejor deshabilitarlo
3. **El monitoreo proactivo es esencial**: El script detectó patrones antes del colapso total
4. **Los errores de configuración se propagan**: Una mala config puede corromper aplicaciones dependientes
5. **Context matters**: Conocer el hardware disponible habría evitado horas de debugging

## 🚨 Incidentes Durante la Resolución

### Problemas con Archivos .bat
Los scripts batch generados tenían caracteres Unicode que Windows no interpretaba:
- `"rificar"` en lugar de `Verificar`
- Tokens inesperados por caracteres especiales
- Solución: Migrar todo a PowerShell sin caracteres especiales

### Confusión en Menús de Backup
El usuario reportó menús confusos que no diferenciaban entre backups del sistema y proyectos. Se rediseñó con secciones claras.

## 📝 Documentación Generada

1. `/home/lauta/glados/wsl-diagnostico-inestabilidad.md` - Análisis inicial
2. `/home/lauta/glados/wsl-plan-emergencia.md` - Plan de acción y soluciones
3. `/home/lauta/glados/wsl-repairing/` - Scripts de backup/restauración
4. `/home/lauta/glados/scripts/wsl-claude-monitor.sh` - Monitor de salud
5. Este documento - Resumen del episodio

## 🔮 Recomendaciones Futuras

1. **Actualizar WSL**: La versión 2.5.7.0 es antigua, considerar actualización
2. **Backup automático diario**: Implementar con los scripts creados
3. **Reinicio preventivo**: Si WSL lleva >24h activo, reiniciar preventivamente
4. **Monitoreo continuo**: Mantener el monitor corriendo en background

## 💡 Conclusión

Lo que parecía un simple problema de configuración resultó ser una combinación de:
- Recursos extremadamente limitados para las necesidades reales
- Subsistema gráfico inestable causando fallos en cascada
- Falta de visibilidad sobre el estado real del sistema

La solución fue directa una vez identificada: dar a WSL los recursos que necesita y deshabilitar componentes problemáticos. De un sistema que se congelaba cada 30 minutos a uno que responde en 3 milisegundos.

**El día de la marmota ha terminado.** 🎉

---
*Duración del incidente: ~2 horas*  
*Archivos afectados: 15+*  
*Scripts creados: 8*  
*Configuraciones modificadas: 3*  
*Estado final: RESUELTO ✅*