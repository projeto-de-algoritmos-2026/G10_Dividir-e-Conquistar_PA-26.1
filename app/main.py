"""
Execução:
    python main.py                  # demo padrão (50 aeronaves)
    python main.py --n 200          # 200 aeronaves aleatórias
    python main.py --testes         # roda bateria de testes D&C vs força bruta
    python main.py --n 500 --testes # 500 pontos + testes
"""

import argparse
import random
import time
import math

from closest_pair import closest_pair

# Tenta importar da base; se não existir, usa stubs internos

try:
    from base import distancia, forca_bruta, gerar_pontos  # type: ignore
    _TEM_BASE = True
except ImportError:
    _TEM_BASE = False

    def distancia(p, q):
        return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

    def forca_bruta(pontos):
        melhor_dist = float("inf")
        melhor_par = (None, None)
        for i in range(len(pontos)):
            for j in range(i + 1, len(pontos)):
                d = distancia(pontos[i], pontos[j])
                if d < melhor_dist:
                    melhor_dist = d
                    melhor_par = (pontos[i], pontos[j])
        return melhor_par, melhor_dist

    def gerar_pontos(n, x_max=1000.0, y_max=1000.0, seed=None):
        rng = random.Random(seed)
        return [(round(rng.uniform(0, x_max), 4),
                 round(rng.uniform(0, y_max), 4)) for _ in range(n)]


# ── Limite de segurança aérea (unidades do mapa) ────────────────────────────
LIMITE_SEGURANCA = 50.0


# ---------------------------------------------------------------------------
# Demo — cenário do radar
# ---------------------------------------------------------------------------

def demo_radar(n: int):
    print("=" * 60)
    print("  SISTEMA DE MONITORAMENTO DE TRÁFEGO AÉREO")
    print("  Algoritmo: Par de Pontos mais Próximos — O(n log n)")
    print("=" * 60)

    if not _TEM_BASE:
        print("  [AVISO] base.py não encontrado — usando stubs internos.\n")

    pontos = gerar_pontos(n, seed=42)
    print(f"  Aeronaves monitoradas : {n}")
    print(f"  Limite de segurança   : {LIMITE_SEGURANCA} unidades\n")

    # Cronometra D&C
    t0 = time.perf_counter()
    par_dc, dist_dc = closest_pair(pontos)
    t_dc = time.perf_counter() - t0

    aeronave_a, aeronave_b = par_dc
    print(f"  Par mais próximo detectado:")
    print(f"    Aeronave A : {aeronave_a}")
    print(f"    Aeronave B : {aeronave_b}")
    print(f"    Distância  : {dist_dc:.4f} unidades")
    print(f"    Tempo D&C  : {t_dc*1000:.3f} ms\n")

    if dist_dc < LIMITE_SEGURANCA:
        print("  ⚠  ALERTA: distância abaixo do limite de segurança!")
        print("     Risco de colisão — acionar controlador imediatamente.")
    else:
        print("  ✓  Situação normal. Nenhuma colisão iminente.")

    print("=" * 60)


# ---------------------------------------------------------------------------
# Testes de corretude — D&C deve coincidir com força bruta
# ---------------------------------------------------------------------------

def rodar_testes():
    print("\n" + "=" * 60)
    print("  TESTES DE CORRETUDE: closest_pair vs forca_bruta")
    print("=" * 60)

    casos = [
        # (descricao, pontos)
        ("2 pontos", [(0.0, 0.0), (3.0, 4.0)]),
        ("3 pontos (caso base)", [(0.0, 0.0), (1.0, 0.0), (3.0, 4.0)]),
        ("4 pontos", [(0.0, 0.0), (1.0, 0.0), (3.0, 4.0), (0.5, 0.5)]),
        ("Pontos colineares em X", [(i * 1.0, 0.0) for i in range(10)]),
        ("Pontos colineares em Y", [(0.0, i * 1.0) for i in range(10)]),
        ("Grade 4×4", [(float(x), float(y)) for x in range(4) for y in range(4)]),
        ("20 aleatórios seed=1", gerar_pontos(20, seed=1)),
        ("50 aleatórios seed=7", gerar_pontos(50, seed=7)),
        ("100 aleatórios seed=99", gerar_pontos(100, seed=99)),
        ("200 aleatórios seed=13", gerar_pontos(200, seed=13)),
        ("500 aleatórios seed=42", gerar_pontos(500, seed=42)),
    ]

    passou = 0
    falhou = 0
    EPS = 1e-9

    for desc, pontos in casos:
        par_fb, dist_fb = forca_bruta(pontos)
        par_dc, dist_dc = closest_pair(pontos)

        ok = abs(dist_dc - dist_fb) < EPS
        status = "✓ PASSOU" if ok else "✗ FALHOU"
        if ok:
            passou += 1
        else:
            falhou += 1

        print(f"  {status}  {desc}")
        if not ok:
            print(f"           força bruta : {dist_fb:.6f}  par={par_fb}")
            print(f"           D&C         : {dist_dc:.6f}  par={par_dc}")

    print("-" * 60)
    print(f"  Resultado: {passou} passou(ram), {falhou} falhou(ram)")
    print("=" * 60)

    return falhou == 0


# ---------------------------------------------------------------------------
# Benchmark — compara tempo D&C vs força bruta para tamanhos crescentes
# ---------------------------------------------------------------------------

def benchmark():
    print("\n" + "=" * 60)
    print("  BENCHMARK: D&C vs Força Bruta")
    print(f"  {'n':>7}  {'D&C (ms)':>10}  {'FB (ms)':>10}  {'speedup':>8}")
    print("-" * 60)

    for n in [100, 500, 1_000, 3_000, 5_000]:
        pontos = gerar_pontos(n, seed=0)

        t0 = time.perf_counter()
        closest_pair(pontos)
        t_dc = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        forca_bruta(pontos)
        t_fb = (time.perf_counter() - t0) * 1000

        speedup = t_fb / t_dc if t_dc > 0 else float("inf")
        print(f"  {n:>7}  {t_dc:>10.2f}  {t_fb:>10.2f}  {speedup:>7.1f}x")

    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Radar de tráfego aéreo — Par de Pontos mais Próximos"
    )
    parser.add_argument("--n", type=int, default=50,
                        help="Número de aeronaves (padrão: 50)")
    parser.add_argument("--testes", action="store_true",
                        help="Rodar bateria de testes de corretude")
    parser.add_argument("--benchmark", action="store_true",
                        help="Rodar benchmark D&C vs força bruta")
    args = parser.parse_args()

    demo_radar(args.n)

    if args.testes:
        sucesso = rodar_testes()
        if not sucesso:
            raise SystemExit(1)

    if args.benchmark:
        benchmark()