import db

# =========================
# MOTOR DE INFERENCIA
# =========================
def diagnosticar(sintomas_paciente):
    """
    Compara los síntomas ingresados por el médico contra los síntomas
    registrados para cada enfermedad en la base de datos.

    Retorna lista de resultados ordenada por probabilidad descendente,
    incluyendo solo enfermedades con al menos 1 coincidencia.
    """
    db.cargar_todo()
    enfermedades = db.get_enfermedades()

    # Normalizar síntomas del paciente
    sintomas_input = [s.strip().lower() for s in sintomas_paciente if s.strip()]

    resultados = []

    for enf in enfermedades:
        sintomas_enf = db.get_sintomas_de_enfermedad(enf["id"])

        if not sintomas_enf:
            continue  # enfermedad sin síntomas registrados, se omite

        nombres_enf = [s["nombre"].strip().lower() for s in sintomas_enf]
        total_enf   = len(nombres_enf)

        # Coincidencias exactas y parciales
        coincidencias = 0
        sintomas_coinciden = []

        for s_input in sintomas_input:
            for s_enf in nombres_enf:
                if s_input == s_enf or s_input in s_enf or s_enf in s_input:
                    coincidencias += 1
                    sintomas_coinciden.append(s_enf)
                    break  # no contar doble el mismo síntoma de la enfermedad

        if coincidencias == 0:
            continue

        # Probabilidad: qué porcentaje de los síntomas de la enfermedad coinciden
        probabilidad = round((coincidencias / total_enf) * 100, 1)

        resultados.append({
            "enfermedad":        enf["nombre"],
            "probabilidad":      probabilidad,
            "coincidencias":     coincidencias,
            "total_sintomas":    total_enf,
            "sintomas_coinciden": sintomas_coinciden,
        })

    # Ordenar de mayor a menor probabilidad
    resultados.sort(key=lambda x: x["probabilidad"], reverse=True)

    return resultados
