import json

def afd(Q, sigma, delta, q0, F, cadeia):
    qA = q0
    for s in cadeia:
        qA = delta[(qA, s)]
    return qA in F

# Função de Kauã: Conversão de AFND-e para AFND
def afnde_para_afnd(estados, alfabeto, delta, estado_inicial, finais):
    # Kauã
    return 0


def afnd_para_afd(estados, alfabeto, delta, estado_inicial, finais):
    from collections import deque

    # Função auxiliar para obter os próximos estados a partir de um conjunto de estados e um símbolo
    def mover(estados_set, simbolo):
        resultado = set()
        for estado in estados_set:
            transicoes = delta.get((estado, simbolo), [])
            if isinstance(transicoes, str):  # Se for AFD, pode vir como string
                resultado.add(transicoes)
            else:
                resultado.update(transicoes)
        return resultado

    # Estado inicial do AFD será o conjunto que contém apenas o estado inicial do AFND
    estado_inicial_afd = frozenset([estado_inicial])
    fila = deque([estado_inicial_afd])
    visitados = set()
    novos_estados = []
    nova_delta = {}
    novos_finais = set()

    while fila:
        atual = fila.popleft()
        if atual in visitados:
            continue
        visitados.add(atual)
        novos_estados.append(atual)

        # Verifica se algum estado do conjunto é final
        if any(e in finais for e in atual):
            novos_finais.add(atual)

        for simbolo in alfabeto:
            prox = mover(atual, simbolo)
            prox_frozen = frozenset(prox)
            nova_delta[(atual, simbolo)] = prox_frozen
            if prox_frozen not in visitados:
                fila.append(prox_frozen)

    # Renomeia os estados para strings legíveis
    estado_map = {estado: f"S{i}" for i, estado in enumerate(novos_estados)}
    estados_renomeados = list(estado_map.values())
    delta_renomeado = {
        (estado_map[orig], simbolo): estado_map[dest]
        for (orig, simbolo), dest in nova_delta.items()
    }
    finais_renomeados = [estado_map[e] for e in novos_finais]
    estado_inicial_renomeado = estado_map[estado_inicial_afd]

    return estados_renomeados, alfabeto, delta_renomeado, estado_inicial_renomeado, finais_renomeados


def minimizar_afd(estados, alfabeto, delta, estado_inicial, finais):
    #Vitor
    return 0

# Lê os dados do arquivo JSON
with open("entradaAFND.json", "r") as f:
    dados = json.load(f)

# Converte as chaves da função de transição para tuplas
delta_convertido = {}
for chave, valor in dados["delta"].items():
    estado, simbolo = chave.strip("()").split(",")
    delta_convertido[(estado, simbolo)] = valor

# Executa o AFD
# Verifica se é AFND (se alguma transição leva a múltiplos estados)
is_afnd = any(isinstance(v, list) for v in delta_convertido.values())

if is_afnd:
    estados_afd, sigma_afd, delta_afd, q0_afd, finais_afd = afnd_para_afd(
        dados["Q"], 
        dados["Sigma"], 
        delta_convertido, 
        dados["q0"], 
        dados["F"]
    )
    resultado = afd(estados_afd, sigma_afd, delta_afd, q0_afd, finais_afd, dados["cadeia"])
else:
    resultado = afd(
        dados["Q"], 
        dados["Sigma"], 
        delta_convertido, 
        dados["q0"], 
        dados["F"], 
        dados["cadeia"]
    )


# Exibe o resultado
print("Cadeia aceita." if resultado else "Cadeia rejeitada.")