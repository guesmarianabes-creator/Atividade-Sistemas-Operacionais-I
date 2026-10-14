def detectar_deadlock(disponivel, alocacao, requisicao):
    n = len(alocacao)
    trabalho = disponivel[:]
    terminou = [False] * n

    # processo que não segura nada não participa de deadlock
    for i in range(n):
        if all(x == 0 for x in alocacao[i]):
            terminou[i] = True

    mudou = True
    while mudou:
        mudou = False
        for i in range(n):
            if terminou[i]:
                continue
            pode_rodar = all(requisicao[i][j] <= trabalho[j]
                             for j in range(len(trabalho)))
            if pode_rodar:
                for j in range(len(trabalho)):
                    trabalho[j] += alocacao[i][j]
                terminou[i] = True
                mudou = True

    return [i for i in range(n) if not terminou[i]]


def mostrar_deadlock(nome, disponivel, alocacao, requisicao):
    print(f"\n--- Cenário: {nome} ---")
    print("Disponível:", disponivel)
    for i in range(len(alocacao)):
        print(f"  P{i}: aloca={alocacao[i]} pede={requisicao[i]}")
    envolvidos = detectar_deadlock(disponivel, alocacao, requisicao)
    if envolvidos:
        print("DEADLOCK! Processos envolvidos:",
              ", ".join(f"P{p}" for p in envolvidos))
    else:
        print("Nenhum deadlock. Todos os processos conseguem terminar.")
    return envolvidos


def cenarios_deadlock():
   
    mostrar_deadlock(
        "Espera circular entre P0 e P1",
        [0, 0],
        [[1, 0], [0, 1]],
        [[0, 1], [1, 0]],
    )
 
    mostrar_deadlock(
        "Sem deadlock",
        [0, 1],
        [[1, 0], [0, 1]],
        [[0, 1], [1, 0]],
    )
   
    mostrar_deadlock(
        "Três processos, dois em deadlock",
        [0, 0],
        [[1, 0], [0, 1], [0, 0]],
        [[0, 1], [1, 0], [0, 0]],
    )


def deadlock_personalizado():
    n = int(input("Número de processos: "))
    m = int(input("Número de recursos: "))
    print(f"Digite o vetor disponível ({m} números separados por espaço):")
    disponivel = list(map(int, input().split()))
    alocacao, requisicao = [], []
    for i in range(n):
        print(f"P{i} - alocação atual ({m} números):")
        alocacao.append(list(map(int, input().split())))
        print(f"P{i} - requisição ({m} números):")
        requisicao.append(list(map(int, input().split())))
    mostrar_deadlock("Personalizado", disponivel, alocacao, requisicao)



def simular_fifo(referencias, qtd_frames):
    frames = []          # frames na ordem de chegada (o mais antigo é o [0])
    faltas = 0
    acertos = 0
    passos = []

    for pagina in referencias:
        removida = None
        if pagina in frames:
            acertos += 1
            resultado = "HIT"
        else:
            faltas += 1
            resultado = "FALTA"
            if len(frames) == qtd_frames:
                removida = frames.pop(0)   # sai a página mais antiga
            frames.append(pagina)
        passos.append((pagina, frames[:], resultado, removida))

    return {"faltas": faltas, "acertos": acertos, "passos": passos}


def simular_lru(referencias, qtd_frames):
    frames = []          # o menos recentemente usado fica no início [0]
    faltas = 0
    acertos = 0
    passos = []

    for pagina in referencias:
        removida = None
        if pagina in frames:
            acertos += 1
            resultado = "HIT"
            frames.remove(pagina)   
            frames.append(pagina)
        else:
            faltas += 1
            resultado = "FALTA"
            if len(frames) == qtd_frames:
                removida = frames.pop(0)  
            frames.append(pagina)
        passos.append((pagina, frames[:], resultado, removida))

    return {"faltas": faltas, "acertos": acertos, "passos": passos}


def imprimir_simulacao(nome, resultado, qtd_frames):
    print(f"\n=== {nome} com {qtd_frames} frames ===")
    print(f"{'Ref':<5}{'Frames':<22}{'Resultado':<11}Substituída")
    for pagina, frames, res, removida in resultado["passos"]:
        texto_frames = str(frames)
        sub = removida if removida is not None else "-"
        print(f"{pagina:<5}{texto_frames:<22}{res:<11}{sub}")
    total = resultado["faltas"] + resultado["acertos"]
    taxa = resultado["faltas"] / total * 100 if total else 0
    print(f"Acertos: {resultado['acertos']} | "
          f"Page faults: {resultado['faltas']} | "
          f"Taxa de falta: {taxa:.1f}%")




def comparar_frames(referencias, max_frames, funcao_simulacao):
    """Devolve {qtd_frames: faltas} para 1..max_frames."""
    resultado = {}
    for f in range(1, max_frames + 1):
        resultado[f] = funcao_simulacao(referencias, f)["faltas"]
    return resultado


def achar_anomalias(faltas_por_frames):
    """Lista pares (frames_menor, frames_maior) em que houve anomalia."""
    anomalias = []
    chaves = sorted(faltas_por_frames)
    for i in range(1, len(chaves)):
        anterior = chaves[i - 1]
        atual = chaves[i]
        if faltas_por_frames[atual] > faltas_por_frames[anterior]:
            anomalias.append((anterior, atual))
    return anomalias


def analisar_belady(referencias, max_frames):
    print("\n=== Anomalia de Belady ===")
    print("Referências:", referencias)
    for nome, funcao in (("FIFO", simular_fifo), ("LRU", simular_lru)):
        tabela = comparar_frames(referencias, max_frames, funcao)
        print(f"\n{nome}:")
        for f, faltas in tabela.items():
            print(f"  {f} frames -> {faltas} page faults")
        anomalias = achar_anomalias(tabela)
        if anomalias:
            for a, b in anomalias:
                print(f"  ANOMALIA: com {a} frames foram {tabela[a]} faltas, "
                      f"com {b} frames foram {tabela[b]}.")
        else:
            print("  Nenhuma anomalia detectada.")



SEQ_BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def executar_testes():
    print("\n=== Executando testes ===")

    # deadlock
    assert detectar_deadlock([0, 0], [[1, 0], [0, 1]], [[0, 1], [1, 0]]) == [0, 1]
    assert detectar_deadlock([0, 1], [[1, 0], [0, 1]], [[0, 1], [1, 0]]) == []
    assert detectar_deadlock([0, 0], [[1, 0], [0, 1], [0, 0]],
                             [[0, 1], [1, 0], [0, 0]]) == [0, 1]
    print("Deadlock: OK")

    # FIFO e LRU na sequência clássica
    assert simular_fifo(SEQ_BELADY, 3)["faltas"] == 9
    assert simular_fifo(SEQ_BELADY, 4)["faltas"] == 10
    assert simular_lru(SEQ_BELADY, 3)["faltas"] == 10
    assert simular_lru(SEQ_BELADY, 4)["faltas"] == 8
    print("FIFO/LRU: OK")

    # sequência simples com hits conhecidos
    r = simular_fifo([1, 2, 1, 3, 1], 2)
    assert (r["faltas"], r["acertos"]) == (4, 1)
    r = simular_lru([1, 2, 1, 3, 2], 2)
    assert (r["faltas"], r["acertos"]) == (4, 1)
    print("Hits e faltas: OK")

    # Belady
    fifo = comparar_frames(SEQ_BELADY, 5, simular_fifo)
    lru = comparar_frames(SEQ_BELADY, 5, simular_lru)
    assert (3, 4) in achar_anomalias(fifo)
    assert achar_anomalias(lru) == []
    print("Belady: OK (FIFO tem anomalia, LRU não)")

    print("Todos os testes passaram.")



def ler_referencias():
    texto = input("Sequência de páginas (ex: 1 2 3 4 1 2 5): ")
    return list(map(int, texto.split()))


def menu():
    while True:
        print("\n===== SIMULADOR DE SO =====")
        print("1 - Deadlock (cenários prontos)")
        print("2 - Deadlock (digitar dados)")
        print("3 - FIFO e LRU")
        print("4 - Anomalia de Belady")
        print("5 - Rodar testes")
        print("0 - Sair")
        op = input("Opção: ").strip()

        if op == "1":
            cenarios_deadlock()
        elif op == "2":
            deadlock_personalizado()
        elif op == "3":
            refs = ler_referencias()
            frames = int(input("Quantidade de frames: "))
            imprimir_simulacao("FIFO", simular_fifo(refs, frames), frames)
            imprimir_simulacao("LRU", simular_lru(refs, frames), frames)
        elif op == "4":
            usar_padrao = input("Usar sequência clássica de Belady? (s/n): ")
            refs = SEQ_BELADY if usar_padrao.lower() == "s" else ler_referencias()
            maximo = int(input("Máximo de frames a testar: "))
            analisar_belady(refs, maximo)
        elif op == "5":
            executar_testes()
        elif op == "0":
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
