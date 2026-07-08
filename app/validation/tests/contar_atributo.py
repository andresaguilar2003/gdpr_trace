import os
import pm4py

# Ruta al archivo comprimido
RUTA_LOG = r"data\input\BPI Challenge 2017.xes.gz"
ACTIVIDAD_BUSCADA = "W_Personal Loan collection"

def contar_coincidencias():
    if not os.path.exists(RUTA_LOG):
        print(f"❌ No se encuentra el archivo en la ruta: {RUTA_LOG}")
        return

    print("=" * 80)
    print(f"CARGANDO Y ANALIZANDO LOG: {os.path.basename(RUTA_LOG)}")
    print("=" * 80)
    print("⏳ Esto puede tomar unos segundos debido al volumen del dataset...")

    # Cargar usando PM4Py tal como hace tu test funcional
    log = pm4py.read_xes(RUTA_LOG)

    # Convertir a DataFrame o estructura limpia si PM4Py lo requiere
    if hasattr(log, "columns"):
        log = pm4py.convert_to_event_log(log)

    total_casos = len(log)
    total_eventos = 0
    contador_actividad = 0

    # Recorrer las trazas y eventos de forma estructurada
    for trace in log:
        for event in trace:
            total_eventos += 1
            # PM4Py almacena el valor de 'concept:name' directamente en el diccionario del evento
            if event.get("concept:name") == ACTIVIDAD_BUSCADA:
                contador_actividad += 1

    print("\n" + "=" * 80)
    print("📊 RESULTADO DEL ANÁLISIS")
    print("=" * 80)
    print(f"  → Casos (trazas) cargados: {total_casos:,}")
    print(f"  → Eventos totales evaluados: {total_eventos:,}")
    print(f"  → La actividad '{ACTIVIDAD_BUSCADA}' aparece: {contador_actividad} veces.")
    print("=" * 80)

if __name__ == "__main__":
    contar_coincidencias()