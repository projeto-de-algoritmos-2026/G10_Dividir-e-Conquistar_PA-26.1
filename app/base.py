"""
Base — funções fundamentais para o problema do Par de Pontos mais Próximos.

Responsabilidades:
    - distancia(p, q)      : distância euclidiana entre dois pontos
    - forca_bruta(pontos)  : solução O(n²) — também usada como caso base do D&C
    - gerar_pontos(n, ...) : geração de pontos aleatórios (entrada de teste)
    - ler_pontos(caminho)  : leitura de pontos de um arquivo de texto
    - ordenar_por_x(pts)   : pré-processamento Px
    - ordenar_por_y(pts)   : pré-processamento Py

Representação de ponto: tupla (x, y) com floats.
"""

import math
import random


# ---------------------------------------------------------------------------
# Distância euclidiana
# ---------------------------------------------------------------------------

def distancia(p, q):
    """Distância euclidiana entre os pontos p e q."""
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return math.sqrt(dx * dx + dy * dy)


# ---------------------------------------------------------------------------
# Força bruta — O(n²)
# ---------------------------------------------------------------------------

def forca_bruta(pontos):
    """
    Par de pontos mais próximos por força bruta.
    Complexidade: O(n²).

    Também serve como caso base da recursão de Divisão e Conquista
    quando o subconjunto tem 3 ou menos pontos.

    Retorna: ((p1, p2), distancia)
    """
    n = len(pontos)
    if n < 2:
        return (None, None), float("inf")

    melhor_par = (pontos[0], pontos[1])
    melhor_dist = distancia(pontos[0], pontos[1])

    for i in range(n):
        for j in range(i + 1, n):
            d = distancia(pontos[i], pontos[j])
            if d < melhor_dist:
                melhor_dist = d
                melhor_par = (pontos[i], pontos[j])

    return melhor_par, melhor_dist


# ---------------------------------------------------------------------------
# Entrada de dados
# ---------------------------------------------------------------------------

def gerar_pontos(n, x_max=1000.0, y_max=1000.0, seed=None):
    """
    Gera n pontos aleatórios uniformemente distribuídos em
    [0, x_max] x [0, y_max]. Use `seed` para reprodutibilidade.

    No tema do trabalho, cada ponto representa a posição de uma aeronave
    sobre o plano monitorado pelo radar.
    """
    rng = random.Random(seed)
    return [
        (round(rng.uniform(0, x_max), 4),
         round(rng.uniform(0, y_max), 4))
        for _ in range(n)
    ]


def ler_pontos(caminho):
    """
    Lê pontos de um arquivo de texto. Formato: uma linha por ponto, com
    `x` e `y` separados por espaço ou vírgula. Linhas vazias e linhas
    começando com '#' são ignoradas.

    Exemplo de arquivo:
        # aeronaves no setor norte
        12.3 45.6
        100.0, 200.0
    """
    pontos = []
    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = linha.replace(",", " ").split()
            if len(partes) < 2:
                continue
            pontos.append((float(partes[0]), float(partes[1])))
    return pontos


# ---------------------------------------------------------------------------
# Pré-processamento (Px e Py)
# ---------------------------------------------------------------------------

def ordenar_por_x(pontos):
    """Retorna nova lista ordenada por X (desempate por Y)."""
    return sorted(pontos, key=lambda p: (p[0], p[1]))


def ordenar_por_y(pontos):
    """Retorna nova lista ordenada por Y (desempate por X)."""
    return sorted(pontos, key=lambda p: (p[1], p[0]))
