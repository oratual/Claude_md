# 📋 Batman Enhanced - Plantillas de Tareas

Este documento contiene plantillas de tareas listas para usar. Copia y modifica según tus necesidades.

## 📖 Índice de Plantillas

1. [Mantenimiento del Sistema](#mantenimiento-del-sistema)
2. [Seguridad](#seguridad)
3. [Análisis con Claude](#análisis-con-claude)
4. [Desarrollo](#desarrollo)
5. [Base de Datos](#base-de-datos)
6. [Monitoreo](#monitoreo)
7. [Respaldos](#respaldos)
8. [Optimización](#optimización)

---

## 🔧 Mantenimiento del Sistema

### Limpieza General
```yaml
tasks:
  - id: "system_cleanup"
    title: "Limpieza general del sistema"
    description: "Elimina archivos temporales y libera espacio"
    type: "maintenance"
    priority: 3
    schedule: "0 3 * * *"  # Diario a las 3 AM
    enabled: true
    command: |
      #!/bin/bash
      set -e
      
      echo "🧹 Iniciando limpieza del sistema..."
      
      # Limpiar temporales antiguos
      find /tmp -type f -atime +7 -delete 2>/dev/null || true
      find /var/tmp -type f -atime +7 -delete 2>/dev/null || true
      
      # Limpiar cache de package managers
      apt-get clean 2>/dev/null || true
      
      # Limpiar logs rotados
      find /var/log -name "*.gz" -mtime +30 -delete 2>/dev/null || true
      
      # Reportar espacio liberado
      df -h /
    timeout: 600
    retry_count: 1
```

### Rotación de Logs
```yaml
tasks:
  - id: "rotate_logs"
    title: "Rotación y compresión de logs"
    description: "Rota logs grandes y comprime antiguos"
    type: "maintenance"
    priority: 3
    schedule: "0 2 * * 0"  # Domingos a las 2 AM
    enabled: true
    command: |
      #!/bin/bash
      
      # Rotar logs grandes
      for log in /var/log/*.log; do
        if [ -f "$log" ] && [ $(stat -c%s "$log") -gt 104857600 ]; then
          echo "Rotando $log (>100MB)"
          mv "$log" "${log}.$(date +%Y%m%d)"
          touch "$log"
        fi
      done
      
      # Comprimir logs antiguos
      find /var/log -name "*.log.*" -mtime +7 ! -name "*.gz" -exec gzip {} \;
    timeout: 900
```

### Limpieza de Docker
```yaml
tasks:
  - id: "docker_cleanup"
    title: "Limpieza de recursos Docker"
    description: "Elimina imágenes y contenedores no utilizados"
    type: "maintenance"
    priority: 3
    schedule: "0 4 * * 1"  # Lunes a las 4 AM
    enabled: true
    command: |
      #!/bin/bash
      
      # Verificar si Docker está instalado
      if ! command -v docker &> /dev/null; then
        echo "Docker no está instalado"
        exit 0
      fi
      
      echo "🐳 Limpiando Docker..."
      
      # Eliminar contenedores detenidos
      docker container prune -f
      
      # Eliminar imágenes no utilizadas
      docker image prune -a -f
      
      # Eliminar volúmenes no utilizados
      docker volume prune -f
      
      # Eliminar redes no utilizadas
      docker network prune -f
      
      # Mostrar espacio liberado
      docker system df
    conditions:
      min_disk_space_gb: 20
```

---

## 🔒 Seguridad

### Auditoría de Seguridad Completa
```yaml
tasks:
  - id: "security_audit_full"
    title: "Auditoría de seguridad completa"
    description: "Verifica permisos, puertos, usuarios y más"
    type: "security"
    priority: 2
    schedule: "0 1 * * *"  # Diario a la 1 AM
    enabled: true
    command: |
      #!/bin/bash
      
      echo "🔒 AUDITORÍA DE SEGURIDAD - $(date)"
      echo "========================================"
      
      # 1. Verificar archivos SUID/SGID
      echo -e "\n[1] Archivos SUID/SGID:"
      find / -type f \( -perm -4000 -o -perm -2000 \) -exec ls -l {} \; 2>/dev/null | head -20
      
      # 2. Verificar permisos SSH
      echo -e "\n[2] Configuración SSH:"
      grep -E "^(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)" /etc/ssh/sshd_config
      
      # 3. Usuarios sin contraseña
      echo -e "\n[3] Usuarios sin contraseña:"
      awk -F: '($2 == "" ) { print $1 }' /etc/shadow
      
      # 4. Puertos abiertos
      echo -e "\n[4] Puertos escuchando:"
      ss -tuln | grep LISTEN
      
      # 5. Procesos ejecutándose como root
      echo -e "\n[5] Procesos de root (top 10):"
      ps aux | grep ^root | sort -k3 -nr | head -10
      
      # 6. Archivos modificados recientemente en /etc
      echo -e "\n[6] Archivos modificados en /etc (últimas 24h):"
      find /etc -type f -mtime -1 2>/dev/null
      
      # 7. Conexiones establecidas
      echo -e "\n[7] Conexiones activas:"
      ss -tun state established
    timeout: 300
    on_failure:
      - create_github_issue: true
        issue_title: "⚠️ Auditoría de seguridad falló"
```

### Verificación de Integridad
```yaml
tasks:
  - id: "integrity_check"
    title: "Verificación de integridad del sistema"
    description: "Verifica checksums de archivos críticos"
    type: "security"
    priority: 2
    schedule: "0 2 * * *"
    enabled: false  # Habilitar después de crear baseline
    command: |
      #!/bin/bash
      
      BASELINE="/var/lib/batman/integrity_baseline.txt"
      CURRENT="/tmp/integrity_current.txt"
      
      # Generar checksums actuales
      find /etc /bin /sbin /usr/bin /usr/sbin -type f -exec sha256sum {} \; > "$CURRENT" 2>/dev/null
      
      if [ -f "$BASELINE" ]; then
        # Comparar con baseline
        diff "$BASELINE" "$CURRENT" > /tmp/integrity_diff.txt
        
        if [ -s /tmp/integrity_diff.txt ]; then
          echo "⚠️ CAMBIOS DETECTADOS EN ARCHIVOS DEL SISTEMA:"
          cat /tmp/integrity_diff.txt
          exit 1
        else
          echo "✅ No se detectaron cambios"
        fi
      else
        # Crear baseline inicial
        cp "$CURRENT" "$BASELINE"
        echo "Baseline creado en $BASELINE"
      fi
```

### Escaneo de Vulnerabilidades
```yaml
tasks:
  - id: "vulnerability_scan"
    title: "Escaneo de vulnerabilidades"
    description: "Busca paquetes con vulnerabilidades conocidas"
    type: "security"
    priority: 1
    schedule: "0 5 * * *"
    enabled: true
    command: |
      #!/bin/bash
      
      echo "🔍 Escaneando vulnerabilidades..."
      
      # Actualizar base de datos
      apt-get update -qq
      
      # Verificar actualizaciones de seguridad
      echo -e "\n[Actualizaciones de seguridad disponibles]"
      apt-get -s upgrade | grep -i security
      
      # Si existe lynis, ejecutar auditoría
      if command -v lynis &> /dev/null; then
        echo -e "\n[Ejecutando Lynis]"
        lynis audit system --quick
      fi
      
      # Verificar CVEs en kernel
      echo -e "\n[Versión del Kernel]"
      uname -a
    retry_count: 2
```

---

## 🤖 Análisis con Claude

### Análisis de Código
```yaml
tasks:
  - id: "code_analysis"
    title: "Análisis de calidad de código"
    description: "Claude analiza el código en busca de mejoras"
    type: "analysis"
    priority: 3
    schedule: "0 6 * * 1"  # Lunes a las 6 AM
    enabled: true
    prompt: |
      Analiza el código en el directorio /home/lauta/projects/current y:
      
      1. Identifica posibles bugs o code smells
      2. Sugiere mejoras de rendimiento
      3. Verifica el cumplimiento de mejores prácticas
      4. Busca vulnerabilidades de seguridad
      5. Sugiere refactorizaciones útiles
      
      Genera un reporte estructurado con:
      - Resumen ejecutivo
      - Hallazgos críticos (si los hay)
      - Sugerencias de mejora priorizadas
      - Snippets de código con las mejoras propuestas
    dependencies: []
    timeout: 1200
```

### Análisis de Logs Inteligente
```yaml
tasks:
  - id: "smart_log_analysis"
    title: "Análisis inteligente de logs"
    description: "Claude busca patrones y anomalías en logs"
    type: "analysis"
    priority: 2
    schedule: "0 7 * * *"
    enabled: true
    prompt: |
      Analiza los logs del sistema de las últimas 24 horas:
      
      1. Lee /var/log/syslog y /var/log/auth.log
      2. Identifica:
         - Patrones de error recurrentes
         - Intentos de acceso sospechosos
         - Degradación de rendimiento
         - Servicios que fallan repetidamente
      3. Correlaciona eventos relacionados
      4. Sugiere acciones correctivas
      
      Prioriza hallazgos por severidad e impacto potencial.
    timeout: 900
```

### Documentación Automática
```yaml
tasks:
  - id: "auto_documentation"
    title: "Generación de documentación"
    description: "Claude documenta código no documentado"
    type: "analysis"
    priority: 4
    schedule: "0 8 * * 5"  # Viernes a las 8 AM
    enabled: true
    prompt: |
      Revisa el proyecto en /home/lauta/projects/main y:
      
      1. Identifica funciones/clases sin documentación
      2. Genera docstrings apropiados
      3. Crea/actualiza README.md si es necesario
      4. Documenta APIs y endpoints
      5. Genera ejemplos de uso
      
      Usa el estilo de documentación existente en el proyecto.
      Si no hay estilo definido, usa las mejores prácticas del lenguaje.
```

---

## 💻 Desarrollo

### Limpieza de Dependencias
```yaml
tasks:
  - id: "clean_dependencies"
    title: "Limpieza de dependencias no utilizadas"
    description: "Elimina paquetes y módulos no utilizados"
    type: "maintenance"
    priority: 3
    schedule: "0 5 * * 0"  # Domingos a las 5 AM
    enabled: true
    command: |
      #!/bin/bash
      
      echo "📦 Limpiando dependencias..."
      
      # Node.js projects
      for dir in $(find ~ -name "node_modules" -type d 2>/dev/null); do
        project_dir=$(dirname "$dir")
        if [ -f "$project_dir/package.json" ]; then
          echo "Limpiando $project_dir"
          cd "$project_dir"
          npm prune
          npm dedupe
        fi
      done
      
      # Python virtual environments antiguos
      find ~ -name "venv" -type d -mtime +90 -exec rm -rf {} \; 2>/dev/null || true
      
      # Limpiar cache pip
      pip cache purge 2>/dev/null || true
```

### Build y Tests Automatizados
```yaml
tasks:
  - id: "nightly_builds"
    title: "Build y tests nocturnos"
    description: "Compila y ejecuta tests de proyectos activos"
    type: "maintenance"
    priority: 2
    schedule: "0 1 * * *"
    enabled: true
    command: |
      #!/bin/bash
      
      PROJECTS="/home/lauta/projects/active"
      REPORT="/tmp/build_report_$(date +%Y%m%d).txt"
      
      echo "🏗️ Build Report - $(date)" > "$REPORT"
      echo "=========================" >> "$REPORT"
      
      for project in "$PROJECTS"/*; do
        if [ -d "$project" ]; then
          echo -e "\n📁 Project: $(basename $project)" >> "$REPORT"
          cd "$project"
          
          # Node.js
          if [ -f "package.json" ]; then
            npm test >> "$REPORT" 2>&1 || echo "❌ Tests failed" >> "$REPORT"
          fi
          
          # Python
          if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
            python -m pytest >> "$REPORT" 2>&1 || echo "❌ Tests failed" >> "$REPORT"
          fi
          
          # Go
          if [ -f "go.mod" ]; then
            go test ./... >> "$REPORT" 2>&1 || echo "❌ Tests failed" >> "$REPORT"
          fi
        fi
      done
      
      cat "$REPORT"
    timeout: 1800
    on_failure:
      - create_github_issue: true
```

---

## 🗄️ Base de Datos

### Mantenimiento de PostgreSQL
```yaml
tasks:
  - id: "postgres_maintenance"
    title: "Mantenimiento de PostgreSQL"
    description: "VACUUM, ANALYZE y verificación de salud"
    type: "maintenance"
    priority: 3
    schedule: "0 4 * * 0"  # Domingos a las 4 AM
    enabled: false  # Habilitar si usas PostgreSQL
    command: |
      #!/bin/bash
      
      # Variables
      PGUSER="postgres"
      DATABASES=$(sudo -u postgres psql -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;")
      
      for db in $DATABASES; do
        echo "🗄️ Mantenimiento de $db"
        
        # VACUUM y ANALYZE
        sudo -u postgres vacuumdb -z "$db"
        
        # Verificar tamaño
        SIZE=$(sudo -u postgres psql -t -c "SELECT pg_size_pretty(pg_database_size('$db'));")
        echo "Tamaño: $SIZE"
        
        # Verificar conexiones
        CONNS=$(sudo -u postgres psql -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='$db';")
        echo "Conexiones activas: $CONNS"
      done
      
      # Limpiar logs antiguos
      find /var/log/postgresql -name "*.log" -mtime +30 -delete
```

### Backup de Base de Datos
```yaml
tasks:
  - id: "database_backup"
    title: "Backup completo de bases de datos"
    description: "Respalda todas las bases de datos"
    type: "maintenance"
    priority: 1
    schedule: "0 2 * * *"  # Diario a las 2 AM
    enabled: true
    command: |
      #!/bin/bash
      
      BACKUP_DIR="/backup/databases/$(date +%Y%m%d)"
      mkdir -p "$BACKUP_DIR"
      
      # MySQL/MariaDB
      if command -v mysqldump &> /dev/null; then
        echo "📦 Respaldando MySQL..."
        mysqldump --all-databases > "$BACKUP_DIR/mysql_all.sql"
        gzip "$BACKUP_DIR/mysql_all.sql"
      fi
      
      # PostgreSQL
      if command -v pg_dump &> /dev/null; then
        echo "📦 Respaldando PostgreSQL..."
        sudo -u postgres pg_dumpall > "$BACKUP_DIR/postgres_all.sql"
        gzip "$BACKUP_DIR/postgres_all.sql"
      fi
      
      # MongoDB
      if command -v mongodump &> /dev/null; then
        echo "📦 Respaldando MongoDB..."
        mongodump --out "$BACKUP_DIR/mongodb"
        tar czf "$BACKUP_DIR/mongodb.tar.gz" "$BACKUP_DIR/mongodb"
        rm -rf "$BACKUP_DIR/mongodb"
      fi
      
      # Verificar integridad
      echo "✅ Backups completados:"
      ls -lh "$BACKUP_DIR"
    conditions:
      min_disk_space_gb: 50
    timeout: 3600
```

---

## 📊 Monitoreo

### Recolección de Métricas
```yaml
tasks:
  - id: "collect_metrics"
    title: "Recolección de métricas del sistema"
    description: "Recopila métricas para análisis de tendencias"
    type: "maintenance"
    priority: 3
    schedule: "*/30 * * * *"  # Cada 30 minutos
    enabled: true
    command: |
      #!/bin/bash
      
      METRICS_FILE="/var/lib/batman/metrics/$(date +%Y%m%d).csv"
      mkdir -p $(dirname "$METRICS_FILE")
      
      # Crear header si no existe
      if [ ! -f "$METRICS_FILE" ]; then
        echo "timestamp,cpu_usage,memory_usage,disk_usage,load_average,processes" > "$METRICS_FILE"
      fi
      
      # Recolectar métricas
      TIMESTAMP=$(date +%s)
      CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
      MEMORY=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
      DISK=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
      LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
      PROCS=$(ps aux | wc -l)
      
      # Guardar métricas
      echo "$TIMESTAMP,$CPU,$MEMORY,$DISK,$LOAD,$PROCS" >> "$METRICS_FILE"
      
      # Rotar archivos antiguos
      find $(dirname "$METRICS_FILE") -name "*.csv" -mtime +30 -delete
```

### Alerta de Recursos
```yaml
tasks:
  - id: "resource_alerts"
    title: "Verificación y alerta de recursos"
    description: "Alerta cuando los recursos exceden umbrales"
    type: "maintenance"
    priority: 2
    schedule: "*/15 * * * *"  # Cada 15 minutos
    enabled: true
    command: |
      #!/bin/bash
      
      ALERT=false
      ALERT_MSG=""
      
      # CPU
      CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d'.' -f1)
      if [ "$CPU" -gt 80 ]; then
        ALERT=true
        ALERT_MSG="$ALERT_MSG\n⚠️ CPU alto: ${CPU}%"
      fi
      
      # Memoria
      MEM=$(free | grep Mem | awk '{print ($3/$2) * 100.0}' | cut -d'.' -f1)
      if [ "$MEM" -gt 90 ]; then
        ALERT=true
        ALERT_MSG="$ALERT_MSG\n⚠️ Memoria alta: ${MEM}%"
      fi
      
      # Disco
      DISK=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
      if [ "$DISK" -gt 85 ]; then
        ALERT=true
        ALERT_MSG="$ALERT_MSG\n⚠️ Disco alto: ${DISK}%"
      fi
      
      # Enviar alerta si es necesario
      if [ "$ALERT" = true ]; then
        echo -e "🚨 ALERTA DE RECURSOS$(date)\n$ALERT_MSG"
        # Aquí podrías enviar email/slack/etc
      fi
```

---

## 💾 Respaldos

### Backup Incremental
```yaml
tasks:
  - id: "incremental_backup"
    title: "Backup incremental del sistema"
    description: "Respalda cambios desde el último backup"
    type: "maintenance"
    priority: 2
    schedule: "0 3 * * *"  # Diario a las 3 AM
    enabled: true
    command: |
      #!/bin/bash
      
      BACKUP_BASE="/backup/incremental"
      TODAY=$(date +%Y%m%d)
      SNAPSHOT_FILE="$BACKUP_BASE/snapshot.dat"
      
      mkdir -p "$BACKUP_BASE/$TODAY"
      
      # Directorios a respaldar
      DIRS=(
        "/etc"
        "/home/lauta/.config"
        "/home/lauta/projects"
        "/var/www"
      )
      
      for dir in "${DIRS[@]}"; do
        if [ -d "$dir" ]; then
          echo "📦 Respaldando $dir..."
          tar czf "$BACKUP_BASE/$TODAY/$(basename $dir).tar.gz" \
            --listed-incremental="$SNAPSHOT_FILE" \
            "$dir" 2>/dev/null
        fi
      done
      
      # Limpiar backups antiguos (mantener 30 días)
      find "$BACKUP_BASE" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
      
      echo "✅ Backup incremental completado"
      du -sh "$BACKUP_BASE/$TODAY"
```

### Sincronización Remota
```yaml
tasks:
  - id: "remote_sync"
    title: "Sincronización con servidor remoto"
    description: "Sincroniza backups importantes con servidor remoto"
    type: "maintenance"
    priority: 2
    schedule: "0 5 * * *"  # Diario a las 5 AM
    enabled: false  # Configurar servidor primero
    command: |
      #!/bin/bash
      
      REMOTE_HOST="backup@servidor.ejemplo.com"
      REMOTE_PATH="/backups/$(hostname)"
      LOCAL_PATH="/backup"
      
      # Verificar conectividad
      if ! ssh -q "$REMOTE_HOST" exit; then
        echo "❌ No se puede conectar al servidor remoto"
        exit 1
      fi
      
      echo "🔄 Sincronizando con servidor remoto..."
      
      # Sincronizar usando rsync
      rsync -avz --delete \
        --exclude='*.tmp' \
        --exclude='*.lock' \
        "$LOCAL_PATH/" \
        "$REMOTE_HOST:$REMOTE_PATH/"
      
      # Verificar espacio en remoto
      ssh "$REMOTE_HOST" "df -h $REMOTE_PATH"
    timeout: 3600
    retry_count: 3
```

---

## ⚡ Optimización

### Optimización de Servicios
```yaml
tasks:
  - id: "service_optimization"
    title: "Optimización de servicios del sistema"
    description: "Reinicia servicios con alto consumo de memoria"
    type: "maintenance"
    priority: 3
    schedule: "0 6 * * 0"  # Domingos a las 6 AM
    enabled: true
    command: |
      #!/bin/bash
      
      # Servicios a monitorear
      SERVICES=("nginx" "mysql" "apache2" "php-fpm")
      MEMORY_THRESHOLD=500  # MB
      
      for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service"; then
          # Obtener uso de memoria
          PID=$(systemctl show -p MainPID "$service" | cut -d= -f2)
          if [ "$PID" != "0" ]; then
            MEM=$(ps -p "$PID" -o rss= | awk '{print int($1/1024)}')
            
            if [ "$MEM" -gt "$MEMORY_THRESHOLD" ]; then
              echo "⚡ Reiniciando $service (usando ${MEM}MB)..."
              systemctl restart "$service"
              sleep 5
              
              # Verificar que se reinició correctamente
              if systemctl is-active --quiet "$service"; then
                echo "✅ $service reiniciado correctamente"
              else
                echo "❌ Error al reiniciar $service"
              fi
            fi
          fi
        fi
      done
```

### Cache y Optimización Web
```yaml
tasks:
  - id: "web_optimization"
    title: "Optimización de recursos web"
    description: "Comprime imágenes y optimiza assets"
    type: "maintenance"
    priority: 4
    schedule: "0 7 * * 1"  # Lunes a las 7 AM
    enabled: true
    command: |
      #!/bin/bash
      
      WEB_ROOTS=("/var/www" "/home/lauta/projects/*/public")
      
      for root in $WEB_ROOTS; do
        if [ -d "$root" ]; then
          echo "🎨 Optimizando $root..."
          
          # Comprimir imágenes PNG
          find "$root" -name "*.png" -size +100k -exec optipng -o2 {} \; 2>/dev/null || true
          
          # Comprimir imágenes JPG
          find "$root" -name "*.jpg" -o -name "*.jpeg" -size +100k -exec jpegoptim --max=85 {} \; 2>/dev/null || true
          
          # Minificar CSS (si está instalado cssnano)
          if command -v cssnano &> /dev/null; then
            find "$root" -name "*.css" ! -name "*.min.css" -exec sh -c 'cssnano {} > {}.min' \;
          fi
          
          # Limpiar cache antiguo
          find "$root" -path "*/cache/*" -type f -mtime +30 -delete 2>/dev/null || true
        fi
      done
```

---

## 🎯 Casos de Uso Especiales

### Monitoreo de Certificados SSL
```yaml
tasks:
  - id: "ssl_certificate_check"
    title: "Verificación de certificados SSL"
    description: "Alerta antes de que expiren certificados"
    type: "security"
    priority: 1
    schedule: "0 9 * * *"  # Diario a las 9 AM
    enabled: true
    command: |
      #!/bin/bash
      
      # Dominios a verificar
      DOMAINS=(
        "ejemplo.com"
        "app.ejemplo.com"
        "api.ejemplo.com"
      )
      
      WARNING_DAYS=30
      CRITICAL_DAYS=7
      
      for domain in "${DOMAINS[@]}"; do
        echo "🔐 Verificando $domain..."
        
        # Obtener fecha de expiración
        EXPIRY=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | \
                 openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
        
        if [ -n "$EXPIRY" ]; then
          EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
          CURRENT_EPOCH=$(date +%s)
          DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
          
          if [ $DAYS_LEFT -lt $CRITICAL_DAYS ]; then
            echo "🚨 CRÍTICO: $domain expira en $DAYS_LEFT días!"
          elif [ $DAYS_LEFT -lt $WARNING_DAYS ]; then
            echo "⚠️ ADVERTENCIA: $domain expira en $DAYS_LEFT días"
          else
            echo "✅ $domain: OK ($DAYS_LEFT días restantes)"
          fi
        else
          echo "❌ No se pudo verificar $domain"
        fi
      done
    on_failure:
      - create_github_issue: true
        priority: "urgent"
```

### Análisis de Tendencias con Claude
```yaml
tasks:
  - id: "trend_analysis"
    title: "Análisis de tendencias del sistema"
    description: "Claude analiza métricas históricas"
    type: "analysis"
    priority: 3
    schedule: "0 10 * * 1"  # Lunes a las 10 AM
    enabled: true
    prompt: |
      Analiza las métricas del sistema de la última semana en /var/lib/batman/metrics/:
      
      1. Identifica tendencias en:
         - Uso de CPU
         - Consumo de memoria
         - Espacio en disco
         - Carga del sistema
         
      2. Detecta anomalías o patrones preocupantes
      
      3. Predice posibles problemas futuros basándote en las tendencias
      
      4. Sugiere acciones preventivas específicas
      
      5. Genera visualizaciones en texto (ASCII) de las tendencias principales
      
      Formato del reporte:
      - Resumen ejecutivo
      - Gráficos de tendencias
      - Alertas y predicciones
      - Recomendaciones priorizadas
```

---

## 📝 Notas de Uso

### Cómo Usar las Plantillas

1. **Copiar plantilla** al directorio de tareas:
   ```bash
   nano ~/.batman/tasks/mi_tarea.yaml
   ```

2. **Modificar** según necesidades:
   - Cambiar `id` a algo único
   - Ajustar `schedule` al horario deseado
   - Modificar `command` o `prompt`
   - Establecer `enabled: true` cuando esté listo

3. **Validar** la tarea:
   ```bash
   batman-enhanced --validate-tasks ~/.batman/tasks/mi_tarea.yaml
   ```

4. **Probar** antes de programar:
   ```bash
   batman-enhanced --run-task mi_tarea_id --test
   ```

### Mejores Prácticas

1. **IDs únicos**: Usa nombres descriptivos como `backup_db_daily`
2. **Timeouts apropiados**: Ajusta según la duración esperada
3. **Manejo de errores**: Usa `set -e` en bash scripts
4. **Logging**: Incluye echo statements para debugging
5. **Condiciones**: Usa conditions para evitar ejecutar en mal momento
6. **Dependencias**: Define dependencias entre tareas relacionadas

### Variables Disponibles

En los comandos puedes usar:
- `$HOME` - Directorio home del usuario
- `$(date +%Y%m%d)` - Fecha actual
- `$(hostname)` - Nombre del host

---

*Estas plantillas son puntos de partida. Modifícalas según tus necesidades específicas.* 🦇