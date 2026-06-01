import math
import random


# Stubs temporários substitídos com a existência do base.py


def _distancia_stub(p, q):
    """Distância euclidiana — stub até base.py ficar pronto."""
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def _forca_bruta_stub(pontos):
    """Força bruta O(n²) — stub até base.py ficar pronto."""
    melhor_dist = float("inf")
    melhor_par = (None, None)
    n = len(pontos)
    for i in range(n):
        for j in range(i + 1, n):
            d = _distancia_stub(pontos[i], pontos[j])
            if d < melhor_dist:
                melhor_dist = d
                melhor_par = (pontos[i], pontos[j])
    return melhor_par, melhor_dist



# Tente importar as funções reais de base.py; se não existir, usa stubs


try:
    from base import distancia, forca_bruta          # type: ignore
except ImportError:
    distancia = _distancia_stub
    forca_bruta = _forca_bruta_stub



# Passo de combinação — verifica a faixa central (strip)


def _verificar_faixa(faixa_por_y, d):
    """
    Recebe os pontos da faixa central já ordenados por Y.
    Compara cada ponto com no máximo 7 vizinhos seguintes.
    Retorna (melhor_par, melhor_dist) dentro da faixa.

    Por que 7 vizinhos? Em qualquer retângulo 2d × d só cabem no máximo
    8 pontos com distância mútua ≥ d, logo basta olhar 7 vizinhos.
    """
    melhor_dist = d
    melhor_par = (None, None)
    n = len(faixa_por_y)

    for i in range(n):
        # j percorre até 7 vizinhos; interrompe se Δy já ≥ melhor_dist
        for j in range(i + 1, min(i + 8, n)):
            if faixa_por_y[j][1] - faixa_por_y[i][1] >= melhor_dist:
                break
            dist = distancia(faixa_por_y[i], faixa_por_y[j])
            if dist < melhor_dist:
                melhor_dist = dist
                melhor_par = (faixa_por_y[i], faixa_por_y[j])

    return melhor_par, melhor_dist



# Função recursiva principal


def _closest_pair_rec(px, py):
    """
    Versão interna (recursiva).

    Parâmetros
    ----------
    px : list de tuplas (x, y) — ordenados por X
    py : list de tuplas (x, y) — ordenados por Y (mesmo conjunto)

    Retorna
    -------
    (par, dist) onde par = ((x1,y1), (x2,y2)) e dist é float
    """
    n = len(px)

    # Caso base: 3 ou menos pontos → força bruta
    if n <= 3:
        return forca_bruta(px)

    # ── Divisão ─────────────────────────────────────────────────────────────
    meio = n // 2
    mediana_x = px[meio][0]          # coordenada X da linha divisória

    px_esq = px[:meio]
    px_dir = px[meio:]

    # Conjuntos esquerdo e direito mantidos ordenados por Y
    px_esq_set = set(px_esq)
    py_esq = [p for p in py if p in px_esq_set]
    py_dir = [p for p in py if p not in px_esq_set]

    # ── Conquista ────────────────────────────────────────────────────────────
    par_esq, d_esq = _closest_pair_rec(px_esq, py_esq)
    par_dir, d_dir = _closest_pair_rec(px_dir, py_dir)

    # Melhor resultado das duas metades
    if d_esq <= d_dir:
        melhor_par, d = par_esq, d_esq
    else:
        melhor_par, d = par_dir, d_dir

    # ── Combinação — faixa central ───────────────────────────────────────────
    # Seleciona pontos a distância < d da linha mediana, mantendo ordem por Y
    faixa = [p for p in py if abs(p[0] - mediana_x) < d]

    par_faixa, d_faixa = _verificar_faixa(faixa, d)

    if d_faixa < d:
        return par_faixa, d_faixa

    return melhor_par, d



# API pública


def closest_pair(pontos):
    """
    Encontra o par de pontos mais próximos usando Divisão e Conquista.

    Complexidade: O(n log n)

    Parâmetros
    ----------
    pontos : list de tuplas (x, y)

    Retorna
    -------
    (par, dist)
        par  — tupla ((x1,y1), (x2,y2))
        dist — float com a distância euclidiana mínima
    """
    n = len(pontos)
    if n < 2:
        raise ValueError("São necessários pelo menos 2 pontos.")

    # Pré-processamento: ordenar por X e por Y
    #  para garantir funcionamento autônomo)
    px = sorted(pontos, key=lambda p: (p[0], p[1]))
    py = sorted(pontos, key=lambda p: (p[1], p[0]))

    return _closest_pair_rec(px, py)