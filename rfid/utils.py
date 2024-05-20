# Fonction pour déterminer si un bloc est vide
def is_block_empty(data):
    # Si le bloc contient uniquement des zéros ou des valeurs nulles, il est considéré comme vide
    return all(x == 0 or x == b'\x00' for x in data)