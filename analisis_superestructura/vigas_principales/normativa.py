"""Referencias normativas y factores editables usados por el motor.

Las ecuaciones codificadas corresponden al Manual de Puentes MTC 2018. Los
factores se conservan en la configuracion para que una revision normativa sea
un cambio explicito y auditable, no una constante oculta en el calculo.
"""

REFERENCIAS_MTC_2018 = {
    "carga_viva": "MTC 2018, 2.4.3.2, pp. 91-101",
    "combinaciones": "MTC 2018, 2.4.5, pp. 129-135",
    "distribucion": "MTC 2018, 2.6.4.2.2, pp. 163-177",
    "acero": "MTC 2018, 2.9.2-2.9.5, pp. 394-469",
    "seccion_compuesta": "MTC 2018, 2.9.5.0.1.1, pp. 432-434",
    "construibilidad": "MTC 2018, 2.9.5.0.3, pp. 441-443",
    "servicio": "MTC 2018, 2.9.5.0.4, pp. 443-445",
    "fatiga": "MTC 2018, 2.9.4.6 y 2.9.5.0.5, pp. 397-403 y 445",
    "flexion": "MTC 2018, 2.9.5.0.6-2.9.5.0.8, pp. 446-454",
    "corte": "MTC 2018, 2.9.5.0.9, pp. 454-457",
}

# Umbral de amplitud constante tomado de las categorias de detalle AASHTO/MTC.
# Se usa para el chequeo de vida infinita; la categoria es una entrada de
# proyecto y debe corresponder al detalle realmente fabricado.
CAFL_MPA = {
    "A": 165.0,
    "B": 110.0,
    "B_PRIMA": 82.7,
    "C": 69.0,
    "C_PRIMA": 82.7,
    "D": 48.3,
    "E": 31.0,
    "E_PRIMA": 17.9,
}

