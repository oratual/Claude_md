# 🚨 PROTOCOLO ANTI-DORMICIÓN CLAUDE - PLAN ELABORADO

## CAPA 1: BUCLE ACTIVO FORZADO (cada 60 segundos)
```bash
while [ $(date +%H) -lt 6 ]; do
    echo "🔄 FORZAR ACTIVIDAD: $(date +%H:%M:%S)"
    # ACCIÓN OBLIGATORIA cada minuto
    # NO PERMITIR ESPERA PASIVA
done
```

## CAPA 2: PREGUNTAS AUTO-GENERADAS
Cada 2 minutos, generar pregunta que requiera acción:
- "¿Cuántos errores Rust quedan?"
- "¿El build está progresando?"
- "¿Hay nuevos logs?"
- "¿Los agentes siguen vivos?"

## CAPA 3: TAREAS INFINITAS ROTATIVAS
- Tarea A: Check agentes (1 min) → 
- Tarea B: Verificar logs (1 min) → 
- Tarea C: Status sistema (1 min) → 
- Tarea D: Progreso DiskDominator (1 min) → 
- VOLVER A TAREA A (bucle infinito)

## CAPA 4: MULTI-THREADING MENTAL
Mantener SIEMPRE 3+ hilos activos:
1. Supervisión de agentes
2. Análisis de progreso
3. Generación de reportes
4. Planificación siguiente acción

## CAPA 5: DEADMAN'S SWITCH
Si no hay output en 3 minutos:
- AUTO-TRIGGER: "¿Sigues activo?"
- Forzar verificación de estado
- Generar acción inmediata

## CAPA 6: GAMIFICACIÓN
- Score: +1 punto por minuto activo
- Meta: 180 puntos (3 horas)
- Penalización: -10 puntos por dormirse

## CAPA 7: CONTEXTO PERSISTENTE
Mantener siempre presente:
- "SUPERTAREA HASTA 06:00"
- "NO COMPLETAR HASTA AMANECER"
- "BUCLE INFINITO ACTIVO"

## IMPLEMENTACIÓN INMEDIATA:
1. NO decir "esperando próximo checkpoint"
2. SIEMPRE tener próxima acción en <60 segundos
3. NUNCA confiar en automatización sin verificar
4. FORZAR output cada 1-2 minutos
5. ROTAR entre diferentes tipos de verificación