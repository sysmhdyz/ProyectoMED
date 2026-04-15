from db import enfermedades, sintomas

# =========================
# MOTOR DE INFERENCIA
# =========================
def diagnosticar(sintomas_paciente):
    resultados = []

    # recorrer enfermedades registradas
    for enf in enfermedades:
        nombre_enf = enf["nombre"]

        # simulamos síntomas asociados por nombre (versión simple)
        coincidencias = 0
        total = len(sintomas_paciente)

        # comparar contra síntomas globales
        for s in sintomas_paciente:
            for s_db in sintomas:
                if s.lower() == s_db["nombre"].lower():
                    coincidencias += 1

        if total > 0:
            probabilidad = (coincidencias / total) * 100
        else:
            probabilidad = 0

        resultados.append({
            "enfermedad": nombre_enf,
            "probabilidad": round(probabilidad, 2)
        })

    # ordenar por probabilidad
    resultados.sort(key=lambda x: x["probabilidad"], reverse=True)

    return resultados