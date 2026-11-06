# Centro de Control Local — Entrega 2 (Arquitectura de Software, ESPE)

**Autor académico:** Jordy Quimbita  
**Sistema:** Sistema de Monitorización y Alertas para Residencias de Adultos Mayores  
**Componente implementado:** Centro de Control Local (`CentroControlLocal`)  
**Tecnologías:** Python 3.10+; biblioteca estándar. Sin `pip`, sensores físicos ni servidores.

## Cómo ejecutar

1. Descomprimir el proyecto y abrir una terminal en la carpeta `CentroControlLocal`.
2. Ejecutar: `python main.py` (en Windows también funciona `py main.py`).
3. Para las pruebas: `python -m unittest discover -s pruebas -v`.
4. Examinar `alertas.log`, que se crea al ejecutar la demostración.

## ¿Qué demuestra?

Una residencia tipo del **escenario académico de la Entrega 1** (30 residentes ficticios; el diseño global considera seis residencias y 180 residentes). El prototipo toma unos pocos casos representativos de esa residencia para probar la lógica. **No despliega seis residencias.**

- Lecturas biométricas con pulso, temperatura, identificador pseudónimo e indicador de caída.
- Validación de tipos, campos y rangos técnicos; rechazo de residentes desconocidos.
- Comparación con `UmbralCritico` del residente mediante `EvaluadorRiesgo`.
- Eventos de dominio `CaidaDetectada`, `RitmoCardiacoCriticoDetectado` y `TemperaturaCriticaDetectada`.
- `AlertaMedica` identificable y **alarma local prioritaria**.
- Filtro de episodios: una anomalía persistente no repite la misma alarma hasta que se normaliza.
- Caída del receptor central de prueba: **la alarma local funciona**; el aviso queda en memoria para reintentarlo al restablecer conectividad.
- Recepción idempotente por ID: el adaptador central no registra dos veces una alerta recibida.
- Bitácora local de alarmas con identificadores pseudónimos, sin nombres ni historias clínicas.

## Estructura por Clean Architecture

```text
CentroControlLocal/
├── dominio/                   # Núcleo: entidades, Value Objects, Domain Events, servicio
│   ├── entidades.py           # Residente, AlertaMedica (Aggregate Roots)
│   ├── objetos_valor.py       # LecturaBiometrica, UmbralCritico
│   ├── eventos.py             # CaidaDetectada, RitmoCardiacoCriticoDetectado, ...
│   └── evaluador_riesgo.py    # EvaluadorRiesgo (Domain Service)
├── aplicacion/                # Caso de uso y puertos; depende solo del dominio
│   ├── casos_uso.py           # ProcesarLectura
│   └── puertos.py             # IProcesarLectura, IAlarmaLocal, IRecepcionAlertas ...
├── adaptadores/               # Traducción y implementaciones de contratos
│   ├── centro_control_local.py
│   ├── adaptador_lecturas.py
│   ├── repositorios_memoria.py
│   ├── alarma_consola.py
│   └── cliente_alertas_prueba.py
├── infraestructura/
│   └── generador_lecturas.py  # Datos de entrada de prueba
├── pruebas/
│   └── test_prototipo.py
└── main.py                    # Composition Root: ensamblaje manual
```

### ¿Por qué esta estructura?

**Arquitectura Limpia**: la regla de dependencia exige que el código interno no conozca infraestructura. El Dominio no importa nada de Aplicación ni Adaptadores. El caso de uso consume **puertos de salida** definidos en Aplicación, que implementan los adaptadores. El **puerto de entrada** `IProcesarLectura` es implementado por el caso de uso y consumido por el adaptador de entrada `CentroControlLocal`. No se usa contenedor de inyección de dependencias: `main.py` conecta las piezas manualmente.

**DDD táctico**: `Residente` conserva `UmbralCritico` y el estado de episodios de riesgo; `LecturaBiometrica` y `UmbralCritico` son Value Objects inmutables; `EvaluadorRiesgo` aplica políticas; los eventos expresan hechos significativos. Se mantienen los contextos conceptuales de Monitorización, Gestión de Residentes y Alertas y Emergencias, sin convertirlos en microservicios.

## Flujo del caso de uso

`GeneradorLecturas` (prueba) → `CentroControlLocal` → `AdaptadorLecturas` (validación y traducción) → `ProcesarLectura` → `RepositorioResidentesMemoria` + `EvaluadorRiesgo` → `Residente.registrar_riesgos()` → eventos de dominio → `AlertaMedica` → **`IAlarmaLocal`** → `IRecepcionAlertas` (central de prueba). Ante falla del receptor, se conserva la alerta mediante `IRepositorioPendientes`; la reconexión llama `reintentar_pendientes()`.

> El flujo anterior representa ejecución, **no la dirección de dependencias del código**. En la Entrega 2, los diagramas UML de paquetes/capas, secuencia y clases deberán representar el código implementado.

## Cobertura y límites

| Requisito de Entrega 1 | Evidencia del prototipo |
|---|---|
| RF-02 Recepción y validación | `AdaptadorLecturas`, `CentroControlLocal` |
| RF-03 Evaluación | `ProcesarLectura`, `EvaluadorRiesgo`, `UmbralCritico` |
| RF-04 Alarma local | `IAlarmaLocal`, `AlarmaConsola` |
| RF-05 Transmisión crítica | `IRecepcionAlertas`, `ClienteAlertasPrueba`, pendientes y reintento |
| Continuidad sin internet | Desconexión de receptor sin bloquear alarma local |
| Datos de prueba sin hardware | `GeneradorLecturas` |
| Inversión de dependencias | Puertos en Aplicación y adaptadores periféricos |

**Fuera del alcance de este componente:** RF-01 (captura física), RF-06 (notificación externa real), BLE operativa, HTTPS/TLS operativa, base de datos, servicio central y avisos reales a hospitales/familiares. Estos se preservan como *contratos previstos* del sistema diseñado en Entrega 1; **no se afirma haberlos desplegado**.

**Limitaciones importantes:** los avisos pendientes se guardan únicamente **en memoria mientras este proceso esté en marcha**; se pierden si se cierra. El caso de uso no integra dispositivos reales ni controla el suministro eléctrico. Los rangos técnicos de entrada (pulso 20–250 bpm; temperatura 25–45 °C) validan datos del ejercicio; los umbrales de alerta (pulso 55–100 bpm, temperatura > 38 °C) son **números ficticios de demostración**, NO recomendaciones clínicas ni software sanitario certificado. El indicador de impacto se interpreta como señal de caída confirmada en el escenario de prueba, no como detección real de caídas. Los tiempos mostrados al ejecutar miden únicamente código local; no acreditan la latencia BLE, red ni despacho de emergencias.

**Privacidad y seguridad del ejercicio:** no se emplean pacientes reales ni datos personales reales; identificadores pseudónimos, entradas validadas y ningún envío externo. Al llevar el sistema a un entorno real faltaría implementar autorización del origen, emparejamiento seguro, HTTPS/TLS 1.3, cifrado y persistencia de pendientes, gestión operativa y validación clínica especializada.

## Demostración reproducible

Al ejecutar `main.py` se muestran lecturas normales, pulso anómalo, su repetición sin nueva alarma, recuperación, caída con receptor fuera de línea, alerta por temperatura y reintento cuando vuelve a estar disponible. Los tests usan exclusivamente `unittest`.

## Referencias técnicas

- Robert C. Martin, *The Clean Architecture* (2012): https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- Python, `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- Python, `unittest`: https://docs.python.org/3/library/unittest.html
