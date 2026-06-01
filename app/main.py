"""
Radar de tráfego aéreo — Par de Pontos mais Próximos (Divisão e Conquista).

Modos de uso:
    python main.py                       # menu interativo (default)
    python main.py --n 200                # demo direta, 200 aeronaves
    python main.py --testes               # bateria de testes
    python main.py --benchmark            # D&C vs força bruta
"""

import argparse
import math
import time

from closest_pair import closest_pair

try:
    from base import distancia, forca_bruta, gerar_pontos, ler_pontos
    _TEM_BASE = True
except ImportError:
    _TEM_BASE = False
    import random

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

    def ler_pontos(caminho):
        pontos = []
        with open(caminho, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue
                partes = linha.replace(",", " ").split()
                if len(partes) >= 2:
                    pontos.append((float(partes[0]), float(partes[1])))
        return pontos


# ---------------------------------------------------------------------------
# Estado da sessão interativa
# ---------------------------------------------------------------------------

class Estado:
    def __init__(self):
        self.n = 50
        self.seed = 42
        self.limite_seguranca = 50.0
        self.pontos_carregados = None      # se != None, sobrescreve gerar_pontos
        self.origem_pontos = "aleatórios"  # rótulo p/ exibir no menu


# ---------------------------------------------------------------------------
# Ações
# ---------------------------------------------------------------------------

def _pontos_atuais(estado: Estado):
    if estado.pontos_carregados is not None:
        return estado.pontos_carregados, f"arquivo ({len(estado.pontos_carregados)} pontos)"
    pts = gerar_pontos(estado.n, seed=estado.seed)
    return pts, f"aleatórios n={estado.n} seed={estado.seed}"


def acao_demo(estado: Estado):
    pontos, origem = _pontos_atuais(estado)
    print()
    print("=" * 60)
    print("  SISTEMA DE MONITORAMENTO DE TRÁFEGO AÉREO")
    print("  Algoritmo: Par de Pontos mais Próximos — O(n log n)")
    print("=" * 60)
    print(f"  Pontos                : {origem}")
    print(f"  Limite de segurança   : {estado.limite_seguranca} unidades")
    print()

    if len(pontos) < 2:
        print("  [ERRO] são necessários pelo menos 2 pontos.")
        print("=" * 60)
        return

    t0 = time.perf_counter()
    par, dist = closest_pair(pontos)
    t_dc = time.perf_counter() - t0

    a, b = par
    print("  Par mais próximo detectado:")
    print(f"    Aeronave A : {a}")
    print(f"    Aeronave B : {b}")
    print(f"    Distância  : {dist:.4f} unidades")
    print(f"    Tempo D&C  : {t_dc*1000:.3f} ms")
    print()
    if dist < estado.limite_seguranca:
        print("  ⚠  ALERTA: distância abaixo do limite de segurança!")
        print("     Risco de colisão — acionar controlador imediatamente.")
    else:
        print("  ✓  Situação normal. Nenhuma colisão iminente.")
    print("=" * 60)


def acao_testes(_estado: Estado):
    print()
    print("=" * 60)
    print("  TESTES DE CORRETUDE: closest_pair vs forca_bruta")
    print("=" * 60)

    casos = [
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

    EPS = 1e-9
    passou = falhou = 0
    for desc, pontos in casos:
        _, dist_fb = forca_bruta(pontos)
        _, dist_dc = closest_pair(pontos)
        ok = abs(dist_dc - dist_fb) < EPS
        print(f"  {'✓ PASSOU' if ok else '✗ FALHOU'}  {desc}")
        passou += int(ok)
        falhou += int(not ok)

    print("-" * 60)
    print(f"  Resultado: {passou} passou(ram), {falhou} falhou(ram)")
    print("=" * 60)
    return falhou == 0


def acao_benchmark(_estado: Estado):
    print()
    print("=" * 60)
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


def acao_carregar_arquivo(estado: Estado):
    caminho = input("  Caminho do arquivo (.txt com 'x y' por linha): ").strip()
    if not caminho:
        print("  Cancelado.")
        return
    try:
        pontos = ler_pontos(caminho)
    except FileNotFoundError:
        print(f"  [ERRO] arquivo não encontrado: {caminho}")
        return
    except Exception as e:
        print(f"  [ERRO] falha ao ler arquivo: {e}")
        return
    if len(pontos) < 2:
        print(f"  [ERRO] arquivo precisa ter pelo menos 2 pontos (tem {len(pontos)}).")
        return
    estado.pontos_carregados = pontos
    estado.origem_pontos = f"arquivo: {caminho}"
    print(f"  ✓ {len(pontos)} pontos carregados de {caminho}.")


def acao_usar_aleatorios(estado: Estado):
    estado.pontos_carregados = None
    estado.origem_pontos = "aleatórios"
    print("  ✓ voltando a usar pontos aleatórios.")


def acao_configurar(estado: Estado):
    print()
    print(f"  Configuração atual:")
    print(f"    n               = {estado.n}")
    print(f"    seed            = {estado.seed}")
    print(f"    limite de alerta= {estado.limite_seguranca}")
    print(f"    fonte de pontos = {estado.origem_pontos}")
    print()
    print("  Deixe em branco para manter o valor atual.")

    val = input(f"  Novo n [{estado.n}]: ").strip()
    if val:
        try:
            estado.n = max(2, int(val))
        except ValueError:
            print("  [ignorado] n inválido.")

    val = input(f"  Nova seed [{estado.seed}]: ").strip()
    if val:
        try:
            estado.seed = int(val)
        except ValueError:
            print("  [ignorado] seed inválida.")

    val = input(f"  Novo limite de alerta [{estado.limite_seguranca}]: ").strip()
    if val:
        try:
            estado.limite_seguranca = float(val)
        except ValueError:
            print("  [ignorado] limite inválido.")

    print("  ✓ configuração atualizada.")


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

MENU = """
============================================================
  RADAR — Par de Pontos mais Próximos (Divisão e Conquista)
============================================================
  [1] Rodar demo do radar
  [2] Rodar testes de corretude (D&C vs força bruta)
  [3] Rodar benchmark
  [4] Carregar pontos de um arquivo
  [5] Voltar a usar pontos aleatórios
  [6] Configurar (n, seed, limite de alerta)
  [0] Sair
------------------------------------------------------------"""


def loop_interativo():
    if not _TEM_BASE:
        print("[AVISO] base.py não encontrado — usando stubs internos.")
    estado = Estado()
    while True:
        print(MENU)
        print(f"  Fonte atual : {estado.origem_pontos}   "
              f"n={estado.n}   seed={estado.seed}   "
              f"limite={estado.limite_seguranca}")
        try:
            escolha = input("  Escolha uma opção: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Encerrando.")
            return

        if escolha == "1":
            acao_demo(estado)
        elif escolha == "2":
            acao_testes(estado)
        elif escolha == "3":
            acao_benchmark(estado)
        elif escolha == "4":
            acao_carregar_arquivo(estado)
        elif escolha == "5":
            acao_usar_aleatorios(estado)
        elif escolha == "6":
            acao_configurar(estado)
        elif escolha in ("0", "q", "sair", "exit"):
            print("  Encerrando.")
            return
        else:
            print("  [opção inválida]")


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Radar de tráfego aéreo — Par de Pontos mais Próximos"
    )
    parser.add_argument("--n", type=int, default=None,
                        help="Número de aeronaves (executa demo direto)")
    parser.add_argument("--testes", action="store_true",
                        help="Executa bateria de testes e sai")
    parser.add_argument("--benchmark", action="store_true",
                        help="Executa benchmark e sai")
    args = parser.parse_args()

    # Modo não-interativo: usa flags como antes
    if args.n is not None or args.testes or args.benchmark:
        estado = Estado()
        if args.n is not None:
            estado.n = args.n
            acao_demo(estado)
        if args.testes:
            ok = acao_testes(estado)
            if not ok:
                raise SystemExit(1)
        if args.benchmark:
            acao_benchmark(estado)
    else:
        # Sem argumentos: menu interativo
        loop_interativo()
