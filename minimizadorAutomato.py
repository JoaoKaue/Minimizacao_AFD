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
    # Converte os estados finais de lista/set de strings para set de strings para operação mais rápida
    finais_set = set(finais)

    # --- Etapa 1: Remover estados inacessíveis ---
    acessiveis = {estado_inicial}
    novos_acessiveis = {estado_inicial}

    # Prepara o delta para acesso mais fácil no formato (estado, simbolo): destino
    delta_flat = delta

    while novos_acessiveis:
        proximos = set()
        for estado in novos_acessiveis:
            for simbolo in alfabeto:
                # Delta do AFD tem valor como string (destino)
                prox_estado = delta_flat.get((estado, simbolo))
                if prox_estado and prox_estado not in acessiveis:
                    proximos.add(prox_estado)
        acessiveis.update(proximos)
        novos_acessiveis = proximos

    # Estados Acessíveis e Finais Acessíveis
    Q_ac = sorted(list(acessiveis))
    F_ac = finais_set.intersection(acessiveis)

    # --- Etapa 2: Partição Inicial (Pi_0 = {Finais, Não-Finais}) ---
    nao_finais = set(Q_ac) - F_ac
    particao = [F_ac, nao_finais]

    # Limpa partições vazias
    particao = [p for p in particao if p]

    particao_anterior = []

    # --- Etapa 3: Refinamento da Partição ---
    while particao != particao_anterior:
        particao_anterior = [set(p) for p in particao] # Copia para comparação
        nova_particao = []

        # Para cada grupo G na partição atual
        for grupo in particao:
            sub_grupos = {}
            for estado in grupo:
                # A "assinatura" do estado é uma tupla dos índices/grupos de destino
                assinatura = []
                for simbolo in alfabeto:
                    estado_destino = delta_flat.get((estado, simbolo))

                    # Encontra o índice do grupo (na partição_anterior) ao qual o estado_destino pertence
                    grupo_destino_idx = -1
                    if estado_destino: # Se a transição for definida
                        for idx, g in enumerate(particao_anterior):
                            if estado_destino in g:
                                grupo_destino_idx = idx
                                break
                    assinatura.append(grupo_destino_idx)

                assinatura_tuple = tuple(assinatura)

                # Separa em subgrupos com base na assinatura
                if assinatura_tuple not in sub_grupos:
                    sub_grupos[assinatura_tuple] = []
                sub_grupos[assinatura_tuple].append(estado)

            # Adiciona os novos subgrupos à nova particao
            for sub_grupo in sub_grupos.values():
                nova_particao.append(set(sub_grupo))

        # Atualiza a partição
        particao = nova_particao

    # --- Etapa 4: Construção do AFD Mínimo ---

    # Mapeia cada estado original para o nome do novo estado
    mapa_estados = {}
    estados_minimo = set()
    estado_inicial_minimo = None
    finais_minimo = set()

    for idx, grupo in enumerate(particao):
        # Novo nome para o estado: "q{idx}"
        # Se for um grupo grande, tenta usar um nome mais descritivo
        novo_estado_nome = f"qMin_{idx}"
        estados_minimo.add(novo_estado_nome)

        for estado in grupo:
            mapa_estados[estado] = novo_estado_nome

        if estado_inicial in grupo:
            estado_inicial_minimo = novo_estado_nome

        if grupo.intersection(F_ac):
            finais_minimo.add(novo_estado_nome)

    # Constrói a nova função de transição delta_minimo
    delta_minimo = {}
    for estado_original, novo_estado_origem in mapa_estados.items():
        for simbolo in alfabeto:
            estado_destino_original = delta_flat.get((estado_original, simbolo))

            # Garante que a transição é válida e acessível (não deve ser -1, mas é bom checar)
            if estado_destino_original in mapa_estados:
                novo_estado_destino = mapa_estados[estado_destino_original]

                # Adiciona a transição se for a primeira vez para o novo_estado_origem e simbolo
                if (novo_estado_origem, simbolo) not in delta_minimo:
                    delta_minimo[(novo_estado_origem, simbolo)] = novo_estado_destino

    return (estados_minimo, alfabeto, delta_minimo, estado_inicial_minimo, finais_minimo)


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
    
# --- Converte AFND para AFD ---
(afd_estados, afd_alfabeto, afd_delta, afd_inicial, afd_finais) = afnd_para_afd(
    afn_estados,
    afn_alfabeto,
    afn_delta,
    afn_inicial,
    afn_finais
)

# --- Minimiza o AFD ---
(estados_minimo, alfabeto_minimo, delta_minimo, estado_inicial_minimo, finais_minimo) = minimizar_afd(
    afd_estados,
    afd_alfabeto,
    afd_delta,
    afd_inicial,
    afd_finais
)

# --- Salva o resultado em JSON ---
saida_json = {
    "Q": sorted(list(estados_minimo)),
    "Sigma": sorted(list(alfabeto_minimo)),
    "delta": {
        f"({origem},{simbolo})": destino
        for (origem, simbolo), destino in delta_minimo.items()
    },
    "q0": estado_inicial_minimo,
    "F": sorted(list(finais_minimo)),
    "cadeia": dados.get("cadeia", "N/A")
}

with open("afd_minimizado.json", "w") as f_out:
    json.dump(saida_json, f_out, indent=4)

print("\n✅ AFD minimizado salvo em 'afd_minimizado.json'")



