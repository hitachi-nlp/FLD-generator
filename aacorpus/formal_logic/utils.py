def templatify(rep: str) -> str:
    if rep.startswith('${'):
        return rep
    else:
        return '${' + rep + '}'


def detemplatify(rep: str) -> str:
    if rep.startswith('${'):
        return rep[2:-1]
    else:
        return rep
