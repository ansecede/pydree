import re


def parse_size(size: float) -> str:
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while i < len(units) and size > 1000:
        size /= 1000
        i += 1
    return f"{round(size * 100) / 100} {units[i]}"


def obtener_descripcion(dir_name: str, descriptions: dict[str, str]):
    if dir_name in descriptions:
        return descriptions[dir_name]

    description = extraer_cuartil_ano(dir_name, descriptions)
    if description:
        return description

    for pattern, descripcion in descriptions.items():
        if re.match(pattern, dir_name):
            return descripcion

    return "Sin descripción"


def extraer_cuartil_ano(dir_name: str, descriptions: dict[str, str]):
    # Expresión regular para capturar cuartil y año
    pattern = r'Q([1-4])-(\d{4})'
    match = re.match(pattern, dir_name)

    if match:
        desc = descriptions[pattern]
        quarter = match.group(1)
        year = match.group(2)
        desc = desc.replace("QQ", quarter)
        desc = desc.replace("YY", year)
        return desc
    return None
