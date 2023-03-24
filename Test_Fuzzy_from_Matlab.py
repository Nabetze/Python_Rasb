import skfuzzy as fuzz

# Cargar el archivo .fis
with open('PI_9.fis', 'r') as f:
    fuzzy_control = fuzz.control.load_from_fis(f)

# Acceder a los antecedentes y consecuentes del sistema de control difuso
antecedents = fuzzy_control.antecedents
consequents = fuzzy_control.consequents