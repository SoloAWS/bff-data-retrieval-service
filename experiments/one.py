import requests
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime

# Configuración
BASE_URL = "https://bff-retrieval-app-1017406670325.us-central1.run.app"
CREATE_TASK_ENDPOINT = "/api/bff/v1/data-retrieval/tasks"
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkRhdGFQYXJ0bmVyIn0.BnLA0KJC3-fQBzpK0KfSO0p4s-KUEHNlpdvUx0Qkzsk"
INVALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpbnZhbGlkIiwibmFtZSI6IkludmFsaWQifQ.invalidSignature"
EXPIRED_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkRhdGFQYXJ0bmVyIiwiZXhwIjoxNTgzMDIyNDAwfQ.Y8K2bgpKHf_o1TYzCyLK8d71vXA85PJFWd3eNNHs5F8"

# Número de pruebas por escenario
NUM_TESTS = 5

# Estructura para almacenar resultados
results = {
    "valid_token": {
        "response_times": [],
        "status_codes": [],
        "success": 0,
        "responses": [],
    },
    "no_token": {
        "response_times": [],
        "status_codes": [],
        "success": 0,
        "responses": [],
    },
    "invalid_token": {
        "response_times": [],
        "status_codes": [],
        "success": 0,
        "responses": [],
    },
    "expired_token": {
        "response_times": [],
        "status_codes": [],
        "success": 0,
        "responses": [],
    },
}


# Datos de muestra para la tarea
def get_task_data():
    return {
        "source_type": "HOSPITAL",
        "source_name": "Hospital San Juan de Dios",
        "source_id": "HSJ-001",
        "location": "Bogotá",
        "retrieval_method": "DIRECT_UPLOAD",
        "batch_id": f"BATCH-2025-{int(time.time())}",
        "priority": 2,
        "metadata": {"department": "Radiología", "project": "Estudio COVID-2025"},
    }


def test_scenario(scenario_name, token=None, num_tests=NUM_TESTS):
    """Realiza múltiples pruebas para un escenario específico y registra resultados"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for i in range(num_tests):
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}{CREATE_TASK_ENDPOINT}",
            headers=headers,
            data=json.dumps(get_task_data()),
        )
        response_time = (time.time() - start_time) * 1000  # ms

        # Almacenar resultados
        results[scenario_name]["response_times"].append(response_time)
        results[scenario_name]["status_codes"].append(response.status_code)
        results[scenario_name]["responses"].append(response.text[:100])

        # Evaluar éxito según el escenario
        if scenario_name == "valid_token" and (
            response.status_code == 203 or response.status_code == 200
        ):
            results[scenario_name]["success"] += 1
        elif scenario_name != "valid_token" and (
            response.status_code == 401 or response.status_code == 403
        ):
            results[scenario_name]["success"] += 1

        # Pequeña pausa para evitar sobrecarga de solicitudes
        time.sleep(0.5)


def run_all_tests():
    """Ejecuta todos los escenarios de prueba"""
    print("=== INICIANDO PRUEBAS DE SEGURIDAD JWT ===")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Realizando {NUM_TESTS} pruebas por escenario...\n")

    test_scenario("valid_token", VALID_TOKEN)
    test_scenario("no_token")
    test_scenario("invalid_token", INVALID_TOKEN)
    test_scenario("expired_token", EXPIRED_TOKEN)


def calculate_metrics():
    """Calcula métricas cuantitativas para cada escenario"""
    metrics = {}

    for scenario, data in results.items():
        success_rate = (data["success"] / NUM_TESTS) * 100
        avg_response_time = np.mean(data["response_times"])
        median_response_time = np.median(data["response_times"])

        metrics[scenario] = {
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "median_response_time": median_response_time,
            "min_response_time": min(data["response_times"]),
            "max_response_time": max(data["response_times"]),
            "most_common_status": max(
                set(data["status_codes"]), key=data["status_codes"].count
            ),
        }

    return metrics


def generate_qualitative_analysis():
    """Realiza un análisis cualitativo de los resultados"""
    analysis = {}

    # Análisis de token válido
    if results["valid_token"]["success"] == NUM_TESTS:
        analysis["valid_token"] = (
            "SEGURO: El sistema permite correctamente el acceso con credenciales válidas."
        )
    else:
        analysis["valid_token"] = (
            "INSEGURO: El sistema rechaza algunas credenciales válidas, lo que puede afectar la disponibilidad."
        )

    # Análisis de solicitudes sin token
    if results["no_token"]["success"] == NUM_TESTS:
        analysis["no_token"] = (
            "SEGURO: El sistema rechaza correctamente solicitudes sin autenticación."
        )
    else:
        analysis["no_token"] = (
            "INSEGURO: El sistema permite algunas solicitudes sin autenticación, comprometiendo la confidencialidad."
        )

    # Análisis de token inválido
    if results["invalid_token"]["success"] == NUM_TESTS:
        analysis["invalid_token"] = (
            "SEGURO: El sistema rechaza correctamente tokens con firma inválida."
        )
    else:
        analysis["invalid_token"] = (
            "INSEGURO: El sistema acepta algunos tokens con firma inválida, comprometiendo la integridad."
        )

    # Análisis de token expirado
    if results["expired_token"]["success"] == NUM_TESTS:
        analysis["expired_token"] = (
            "SEGURO: El sistema rechaza correctamente tokens expirados."
        )
    else:
        analysis["expired_token"] = (
            "INSEGURO: El sistema acepta algunos tokens expirados, comprometiendo la vigencia de la autenticación."
        )

    return analysis


def create_visualizations():
    """Crea visualizaciones para los resultados"""
    # Preparar datos para gráficos
    scenarios = list(results.keys())
    success_rates = [results[s]["success"] / NUM_TESTS * 100 for s in scenarios]
    avg_response_times = [np.mean(results[s]["response_times"]) for s in scenarios]

    # Gráfico de barras para tasas de éxito
    plt.figure(figsize=(10, 6))
    plt.bar(scenarios, success_rates, color=["green", "blue", "blue", "blue"])
    plt.axhline(y=100, color="r", linestyle="-", alpha=0.3)
    plt.ylim(0, 105)
    plt.title("Tasa de Éxito por Escenario (%)")
    plt.ylabel("Tasa de Éxito (%)")
    plt.savefig("success_rates.png")

    # Gráfico de barras para tiempos de respuesta
    plt.figure(figsize=(10, 6))
    plt.bar(scenarios, avg_response_times, color=["green", "blue", "blue", "blue"])
    plt.title("Tiempo Promedio de Respuesta por Escenario (ms)")
    plt.ylabel("Tiempo (ms)")
    plt.savefig("response_times.png")

    # Gráfico de distribución de códigos de estado
    status_data = {}
    for scenario in scenarios:
        for status in results[scenario]["status_codes"]:
            if status not in status_data:
                status_data[status] = [0] * len(scenarios)
            scenario_idx = scenarios.index(scenario)
            status_data[status][scenario_idx] += 1

    # Convertir a formato adecuado para graficación
    status_codes = list(status_data.keys())
    status_counts = list(status_data.values())

    plt.figure(figsize=(12, 8))
    bottom = np.zeros(len(scenarios))
    for i, status in enumerate(status_codes):
        plt.bar(scenarios, status_counts[i], bottom=bottom, label=f"Status {status}")
        bottom += status_counts[i]
    plt.title("Distribución de Códigos de Estado por Escenario")
    plt.ylabel("Número de Respuestas")
    plt.legend()
    plt.savefig("status_codes.png")


def print_results(metrics, analysis):
    """Imprime un informe detallado de los resultados"""
    print("\n=== RESULTADOS CUANTITATIVOS ===")

    # Convertir métricas a un formato tabular
    table_data = []
    for scenario, metric in metrics.items():
        table_data.append(
            [
                scenario.replace("_", " ").title(),
                f"{metric['success_rate']:.1f}%",
                f"{metric['avg_response_time']:.1f} ms",
                f"{metric['median_response_time']:.1f} ms",
                f"{metric['min_response_time']:.1f} ms",
                f"{metric['max_response_time']:.1f} ms",
                metric["most_common_status"],
            ]
        )

    headers = [
        "Escenario",
        "Tasa Éxito",
        "Tiempo Prom.",
        "Tiempo Med.",
        "Tiempo Min.",
        "Tiempo Max.",
        "Estado Común",
    ]

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    print("\n=== ANÁLISIS CUALITATIVO ===")
    for scenario, result in analysis.items():
        print(f"- {scenario.replace('_', ' ').title()}: {result}")

    print("\n=== EVALUACIÓN DE HIPÓTESIS ===")

    # Evaluar si se cumple la hipótesis
    security_score = (
        sum(metrics[s]["success_rate"] for s in metrics) / (len(metrics) * 100) * 100
    )

    print(f"Puntuación de Seguridad: {security_score:.2f}%")
    if security_score >= 95:
        conclusion = "✅ HIPÓTESIS CONFIRMADA: El sistema protege eficazmente la confidencialidad de los datos médicos."
        print(conclusion)
        print(
            "Solo el personal autorizado puede acceder a los datos médicos, cumpliendo con el"
        )
        print(
            "atributo de calidad de Seguridad (Confidencialidad) definido en el escenario."
        )
    else:
        conclusion = "❌ HIPÓTESIS NO CONFIRMADA: El sistema presenta vulnerabilidades en la protección de datos médicos."
        print(conclusion)
        print(
            "Se requiere mejorar la implementación de seguridad para garantizar que solo el"
        )
        print("personal autorizado pueda acceder a los datos médicos.")

    print("\n=== CONCLUSIONES ===")
    print(
        "1. Implementación JWT: "
        + (
            "Correcta"
            if metrics["valid_token"]["success_rate"] == 100
            and metrics["invalid_token"]["success_rate"] == 100
            else "Requiere mejoras"
        )
    )
    print(
        "2. Gestión de tokens: "
        + (
            "Efectiva"
            if metrics["expired_token"]["success_rate"] == 100
            else "Vulnerable"
        )
    )
    print(
        "3. Validación de solicitudes: "
        + ("Robusta" if metrics["no_token"]["success_rate"] == 100 else "Débil")
    )
    print(
        "\nSe generaron visualizaciones en los archivos: success_rates.png, response_times.png y status_codes.png"
    )

    return security_score >= 95


def main():
    run_all_tests()
    metrics = calculate_metrics()
    analysis = generate_qualitative_analysis()
    create_visualizations()
    hypothesis_confirmed = print_results(metrics, analysis)

    # Guardar informe en archivo
    with open("informe_experimento_seguridad.txt", "w") as f:
        f.write(f"INFORME DE EXPERIMENTO DE SEGURIDAD\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(
            f"Hipótesis: {'CONFIRMADA' if hypothesis_confirmed else 'NO CONFIRMADA'}\n"
        )
        f.write(
            f"Score de Seguridad: {sum(metrics[s]['success_rate'] for s in metrics) / (len(metrics) * 100) * 100:.2f}%\n"
        )

    print("\nSe ha generado un informe en 'informe_experimento_seguridad.txt'")


if __name__ == "__main__":
    main()
