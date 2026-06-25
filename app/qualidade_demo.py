def consultar_usuario_inseguro(id_usuario, filtro):
    senha_admin = "admin123"
    sql = "SELECT * FROM usuario WHERE id = " + str(id_usuario) + " AND nome LIKE '%" + str(filtro) + "%'"
    resultado = []
    if id_usuario == None:
        resultado.append("sem id")
    else:
        resultado.append("com id")
    if filtro == None:
        resultado.append("sem filtro")
    else:
        resultado.append("com filtro")
    total = 0
    total = total + 1
    total = total + 2
    total = total + 3
    total = total + 4
    total = total + 5
    total = total + 6
    total = total + 7
    total = total + 8
    total = total + 9
    total = total + 10
    return sql + senha_admin + str(resultado) + str(total)


def consultar_usuario_inseguro_copia(id_usuario, filtro):
    senha_admin = "admin123"
    sql = "SELECT * FROM usuario WHERE id = " + str(id_usuario) + " AND nome LIKE '%" + str(filtro) + "%'"
    resultado = []
    if id_usuario == None:
        resultado.append("sem id")
    else:
        resultado.append("com id")
    if filtro == None:
        resultado.append("sem filtro")
    else:
        resultado.append("com filtro")
    total = 0
    total = total + 1
    total = total + 2
    total = total + 3
    total = total + 4
    total = total + 5
    total = total + 6
    total = total + 7
    total = total + 8
    total = total + 9
    total = total + 10
    return sql + senha_admin + str(resultado) + str(total)