import json

def afd(Q, sigma, delta, q0, F, cadeia):
    qA = q0
    for s in cadeia:
        qA = delta[(qA, s)]
    return qA in F

#Kauã - AFND-e para AFND
def fecho_epsilon(estado, delta):
    #Retorna o fecho-ε de um estado (todos alcançáveis por ε).

    visitados = {estado}
    pilha = [estado]

    while pilha:
        atual = pilha.pop()
        # Procura por transições épsilon (ε)
        if (atual, "ε") in delta:
            for prox in delta[(atual, "ε")]:
                if prox not in visitados:
                    visitados.add(prox)
                    pilha.append(prox)
    return visitados

def afnde_para_afnd(estados, alfabeto, delta, estado_inicial, finais):
    """ Converte um AFND-e para um AFND. """
    novo_delta = {}
    novos_finais = set()

    # Calcula o fecho-ε para todos os estados
    fechos = {q: fecho_epsilon(q, delta) for q in estados}

    #Calcula as novas transições
    for q in estados:
        for a in alfabeto:
            alcançados = set()
            # A regra é: ε-fecho(δ(ε-fecho(q), a))
            for p in fechos[q]:
                if (p, a) in delta:
                    for r in delta[(p, a)]:
                        alcançados |= fechos[r]
            if alcançados:
                novo_delta[(q, a)] = sorted(list(alcançados))

    # Define os novos estados finais
    for q in estados:
        if any(f in fechos[q] for f in finais):
            novos_finais.add(q)

    # Retorna o novo autômato (sem épsilon)
    return estados, alfabeto, novo_delta, estado_inicial, sorted(list(novos_finais))



def afnd_para_afd(estados, alfabeto, delta, estado_inicial, finais):
    #Kauê 
    return 0

def minimizar_afd(estados, alfabeto, delta, estado_inicial, finais):
    #Vitor 
    return 0


def formatar_delta_para_print(delta):
    """Função auxiliar para imprimir o dicionário delta de forma legível."""
    delta_para_print = {}
    for (estado, simbolo), destinos in delta.items():
        chave_str = f"({estado},{simbolo})"
        delta_para_print[chave_str] = destinos
    return delta_para_print

# Garante que o código só rode quando executado como script
if __name__ == "__main__":

    # LÊ O ARQUIVO DE ENTRADA (O AFND-e)
    with open("entradaAFND.json", "r") as f:
        dados = json.load(f)

    # PREPARA O DELTA
    delta_convertido = {}
    for chave, destinos in dados["delta"].items():
        estado, simbolo = chave.strip("()").split(",")
        # O AFND-e tem *listas* de destinos
        if not isinstance(destinos, list):
            destinos = [destinos]
        delta_convertido[(estado, simbolo)] = destinos

    print("--- Iniciando pipeline de conversão ---")

    (afn_estados, afn_alfabeto, afn_delta, afn_inicial, afn_finais) = afnde_para_afnd(
        dados["Q"],
        dados["Sigma"],
        delta_convertido,
        dados["q0"],
        dados["F"]
    )
    
    print("\n--- (AFND sem ε) ---")
    print(json.dumps(formatar_delta_para_print(afn_delta), indent=2))
