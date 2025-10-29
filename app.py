"""Exemplo didático de IA sem dependências externas.

Este script gera um conjunto de dados sintético com 3 classes, implementa
um classificador k-NN simples em Python puro, avalia a acurácia e permite
predições interativas sem instalar pacotes externos.

Objetivo: demonstrar os conceitos básicos de treinamento/avaliação/predição
de forma executável no venv atual (que pode não ter wheels para scikit-learn).
"""

from __future__ import annotations

import math
import random
from typing import List, Tuple


def generate_synthetic_data(
    n_per_class: int = 50, seed: int = 42
) -> Tuple[List[List[float]], List[int], List[str]]:

    random.seed(seed)
    # Três centróides (cada um com 4 features, semelhante ao formato do Iris)
    centroids = [
        [5.0, 3.5, 1.4, 0.2],  # classe 0 (ex.: setosa)
        [6.0, 3.0, 4.5, 1.5],  # classe 1 (ex.: versicolor)
        [6.5, 3.0, 5.5, 2.0],  # classe 2 (ex.: virginica)
    ]
    labels = ["class_0", "class_1", "class_2"]
    X: List[List[float]] = []
    y: List[int] = []
    for idx, c in enumerate(centroids):
        for _ in range(n_per_class):
            # adicionar ruído gaussiano simples
            point = [c_i + random.uniform(-0.6, 0.6) for c_i in c]
            X.append(point)
            y.append(idx)
    return X, y, labels


def train_test_split(
    X: List[List[float]], y: List[int], test_size: float = 0.2, seed: int = 1
) -> Tuple:
    random.seed(seed)
    indices = list(range(len(X)))
    random.shuffle(indices)
    split = int(len(X) * (1 - test_size))
    train_idx = indices[:split]
    test_idx = indices[split:]
    X_train = [X[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_test = [y[i] for i in test_idx]
    return X_train, X_test, y_train, y_test


def euclidean(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def knn_predict(
    X_train: List[List[float]], y_train: List[int], x: List[float], k: int = 5
) -> int:
    # calcula distâncias
    dists = [(euclidean(x, xt), label) for xt, label in zip(X_train, y_train)]
    dists.sort(key=lambda t: t[0])
    topk = dists[:k]
    counts: dict[int, int] = {}
    for _, label in topk:
        counts[label] = counts.get(label, 0) + 1
    # escolhe label com maior contagem
    pred = max(counts.items(), key=lambda t: t[1])[0]
    return pred


def evaluate(
    X_train: List[List[float]],
    y_train: List[int],
    X_test: List[List[float]],
    y_test: List[int],
    k: int = 5,
) -> float:
    correct = 0
    for x, y_true in zip(X_test, y_test):
        if knn_predict(X_train, y_train, x, k=k) == y_true:
            correct += 1
    return correct / len(X_test) if X_test else 0.0


def predict_interactive(
    X_train: List[List[float]], y_train: List[int], labels: List[str]
) -> None:
    prompt = "Digite 4 números (sep_l sep_w pet_l pet_w) separados por espaços, ou ENTER para sair: "
    s = input(prompt).strip()
    if not s:
        return
    try:
        vals = [float(x) for x in s.split()]
        if len(vals) != 4:
            print("Preciso exatamente 4 valores.")
            return
        pred = knn_predict(X_train, y_train, vals, k=5)
        print(f"Predição: {labels[pred]}")
    except Exception as e:
        print("Entrada inválida:", e)


def main() -> None:
    print("Gerando dados sintéticos e avaliando um classificador k-NN simples...")
    X, y, labels = generate_synthetic_data(n_per_class=50, seed=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, seed=7)
    acc = evaluate(X_train, y_train, X_test, y_test, k=5)
    print(f"Acurácia do k-NN (k=5) no conjunto de teste sintético: {acc:.3f}")
    print("Teste interativo: você pode inserir 4 valores para uma previsão.")
    while True:
        predict_interactive(X_train, y_train, labels)
        cont = input("Outra previsão? (s/n): ").strip().lower()
        if cont != "s":
            break


if __name__ == "__main__":
    main()
