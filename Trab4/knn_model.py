import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, mean_squared_error, r2_score
)


def executar_knn(dados):
    """Executa o modelo KNN para classificação e regressão."""

    print("\n" + "=" * 70)
    print("MODELO: KNN (K-Nearest Neighbors)")
    print("=" * 70)

    X_train_scaled = dados['X_train_scaled']
    X_test_scaled = dados['X_test_scaled']
    y_train_class = dados['y_train_class']
    y_test_class = dados['y_test_class']
    y_train_reg = dados['y_train_reg']
    y_test_reg = dados['y_test_reg']

    # --- KNN Classificação ---
    print("\n--- KNN Classificação ---")

    k_range = range(1, 21)
    k_scores = []
    for k in k_range:
        knn_temp = KNeighborsClassifier(n_neighbors=k)
        knn_temp.fit(X_train_scaled, y_train_class)
        k_scores.append(knn_temp.score(X_test_scaled, y_test_class))

    best_k = list(k_range)[np.argmax(k_scores)]
    print(f"    Melhor K: {best_k} (Acurácia: {max(k_scores):.4f})")

    knn_clf = KNeighborsClassifier(n_neighbors=best_k)
    knn_clf.fit(X_train_scaled, y_train_class)
    y_pred_knn = knn_clf.predict(X_test_scaled)

    acc_knn = accuracy_score(y_test_class, y_pred_knn)
    prec_knn = precision_score(y_test_class, y_pred_knn)
    rec_knn = recall_score(y_test_class, y_pred_knn)
    f1_knn = f1_score(y_test_class, y_pred_knn)

    print(f"    Acurácia:  {acc_knn:.4f}")
    print(f"    Precisão:  {prec_knn:.4f}")
    print(f"    Recall:    {rec_knn:.4f}")
    print(f"    F1-Score:  {f1_knn:.4f}")

    # Gráficos KNN Classificação
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    axes[0].plot(k_range, k_scores, 'b-o', linewidth=2, markersize=5)
    axes[0].axvline(x=best_k, color='r', linestyle='--', label=f'Melhor K={best_k}')
    axes[0].set_xlabel('K')
    axes[0].set_ylabel('Acurácia')
    axes[0].set_title('KNN: Acurácia vs K')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    cm_knn = confusion_matrix(y_test_class, y_pred_knn)
    sns.heatmap(cm_knn, annot=True, fmt='d', cmap='Blues', ax=axes[1],
                xticklabels=['Baixa', 'Alta'], yticklabels=['Baixa', 'Alta'])
    axes[1].set_xlabel('Predito')
    axes[1].set_ylabel('Real')
    axes[1].set_title('KNN: Matriz de Confusão')

    metricas = ['Acurácia', 'Precisão', 'Recall', 'F1-Score']
    valores_knn = [acc_knn, prec_knn, rec_knn, f1_knn]
    bars = axes[2].bar(metricas, valores_knn, color=['#2196F3', '#4CAF50', '#FF9800', '#F44336'])
    axes[2].set_ylim(0, 1.1)
    axes[2].set_title('KNN: Métricas de Desempenho')
    for bar, val in zip(bars, valores_knn):
        axes[2].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                     f'{val:.3f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig('Graficos/knn_resultados.png', dpi=150, bbox_inches='tight')
    print("    Gráfico salvo: Graficos/knn_resultados.png")

    # --- KNN Regressão ---
    print("\n--- KNN Regressão ---")
    knn_reg = KNeighborsRegressor(n_neighbors=best_k)
    knn_reg.fit(X_train_scaled, y_train_reg)
    y_pred_knn_reg = knn_reg.predict(X_test_scaled)

    rmse_knn = np.sqrt(mean_squared_error(y_test_reg, y_pred_knn_reg))
    r2_knn = r2_score(y_test_reg, y_pred_knn_reg)
    print(f"    RMSE: {rmse_knn:.4f}")
    print(f"    R²:   {r2_knn:.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].scatter(y_test_reg, y_pred_knn_reg, alpha=0.5, s=10)
    axes[0].plot([0, 1], [0, 1], 'r--', linewidth=2)
    axes[0].set_xlabel('Valor Real')
    axes[0].set_ylabel('Valor Predito')
    axes[0].set_title(f'KNN Regressão: Real vs Predito (R²={r2_knn:.3f})')

    residuos_knn = y_test_reg - y_pred_knn_reg
    axes[1].hist(residuos_knn, bins=30, color='#2196F3', edgecolor='black', alpha=0.7)
    axes[1].axvline(x=0, color='r', linestyle='--')
    axes[1].set_xlabel('Resíduo')
    axes[1].set_ylabel('Frequência')
    axes[1].set_title('KNN Regressão: Distribuição dos Resíduos')

    plt.tight_layout()
    plt.savefig('Graficos/knn_regressao.png', dpi=150, bbox_inches='tight')
    print("    Gráfico salvo: Graficos/knn_regressao.png")

    return {
        'acc': acc_knn, 'prec': prec_knn, 'rec': rec_knn, 'f1': f1_knn,
        'rmse': rmse_knn, 'r2': r2_knn
    }
