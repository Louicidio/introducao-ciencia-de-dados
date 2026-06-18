import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)


def sigmoid(z):
    # Função sigmoide: S(z) = 1 / (1 + e^(-z))
    z = np.clip(z, -500, 500)
    return 1 / (1 + np.exp(-z))


def log_verossimilhanca(X, y, beta):
    # Calcula a log-verossimilhança.
    z = X @ beta
    p = sigmoid(z)
    p = np.clip(p, 1e-15, 1 - 1e-15)
    return np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))


def gradiente_descendente(X, y, lr=0.01, n_iter=1000):
    # Otimização por Gradiente Descendente.
    n, m = X.shape
    beta = np.zeros(m)
    log_likelihoods = []

    for i in range(n_iter):
        z = X @ beta
        p = sigmoid(z)
        grad = X.T @ (y - p)
        beta += lr * grad
        ll = log_verossimilhanca(X, y, beta)
        log_likelihoods.append(ll)

    return beta, log_likelihoods


def executar_regressao_logistica(dados):
    # Executa o modelo de Regressão Logística com pipeline completo.

    features = dados['features']
    X_train_scaled = dados['X_train_scaled']
    X_test_scaled = dados['X_test_scaled']
    y_train_class = dados['y_train_class']
    y_test_class = dados['y_test_class']

    # --- Log-Verossimilhança e Gradiente ---
    print("\n--- 7.1 Log-Verossimilhança e Gradiente ---")

    X_log = np.column_stack([np.ones(X_train_scaled.shape[0]), X_train_scaled])
    y_log = y_train_class

    beta_gd, ll_history = gradiente_descendente(X_log, y_log, lr=0.01, n_iter=1000)

    print(f"    Coeficientes (Gradiente Descendente):")
    print(f"      Intercepto: {beta_gd[0]:.4f}")
    for feat, coef in zip(features, beta_gd[1:]):
        print(f"      {feat}: {coef:.4f}")

    # --- Modelo Scikit-learn ---
    print("\n--- 7.2 Modelo Scikit-learn ---")

    log_reg = LogisticRegression(max_iter=1000, random_state=42)
    log_reg.fit(X_train_scaled, y_train_class)
    y_pred_log = log_reg.predict(X_test_scaled)
    y_prob_log = log_reg.predict_proba(X_test_scaled)[:, 1]

    acc_log = accuracy_score(y_test_class, y_pred_log)
    prec_log = precision_score(y_test_class, y_pred_log)
    rec_log = recall_score(y_test_class, y_pred_log)
    f1_log = f1_score(y_test_class, y_pred_log)

    print(f"    Coeficientes (Scikit-learn):")
    print(f"      Intercepto: {log_reg.intercept_[0]:.4f}")
    for feat, coef in zip(features, log_reg.coef_[0]):
        print(f"      {feat}: {coef:.4f}")
    print(f"\n    Acurácia:  {acc_log:.4f}")
    print(f"    Precisão:  {prec_log:.4f}")
    print(f"    Recall:    {rec_log:.4f}")
    print(f"    F1-Score:  {f1_log:.4f}")

    # --- Gráficos ---
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].plot(ll_history, 'b-', linewidth=1.5)
    axes[0, 0].set_xlabel('Iteração')
    axes[0, 0].set_ylabel('Log-Verossimilhança')
    axes[0, 0].set_title('Convergência do Gradiente Descendente')
    axes[0, 0].grid(True, alpha=0.3)

    cm_log = confusion_matrix(y_test_class, y_pred_log)
    sns.heatmap(cm_log, annot=True, fmt='d', cmap='Greens', ax=axes[0, 1],
                xticklabels=['Baixa', 'Alta'], yticklabels=['Baixa', 'Alta'])
    axes[0, 1].set_xlabel('Predito')
    axes[0, 1].set_ylabel('Real')
    axes[0, 1].set_title('Regressão Logística: Matriz de Confusão')

    metricas = ['Acurácia', 'Precisão', 'Recall', 'F1-Score']
    valores_log = [acc_log, prec_log, rec_log, f1_log]
    bars = axes[0, 2].bar(metricas, valores_log, color=['#2196F3', '#4CAF50', '#FF9800', '#F44336'])
    axes[0, 2].set_ylim(0, 1.1)
    axes[0, 2].set_title('Regressão Logística: Métricas de Desempenho')
    for bar, val in zip(bars, valores_log):
        axes[0, 2].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                        f'{val:.3f}', ha='center', va='bottom', fontweight='bold')

    z_range = np.linspace(-6, 6, 200)
    axes[1, 0].plot(z_range, sigmoid(z_range), 'b-', linewidth=2)
    axes[1, 0].axhline(y=0.5, color='r', linestyle='--', alpha=0.5)
    axes[1, 0].axvline(x=0, color='r', linestyle='--', alpha=0.5)
    axes[1, 0].set_xlabel('z')
    axes[1, 0].set_ylabel('S(z)')
    axes[1, 0].set_title('Função Sigmoid')
    axes[1, 0].grid(True, alpha=0.3)

    coefs = log_reg.coef_[0]
    colors = ['#4CAF50' if c > 0 else '#F44336' for c in coefs]
    bars = axes[1, 1].barh(features, coefs, color=colors)
    axes[1, 1].axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    axes[1, 1].set_xlabel('Coeficiente')
    axes[1, 1].set_title('Coeficientes da Regressão Logística')

    X_2d = X_train_scaled[:, [0, 2]]
    y_2d = y_train_class

    log_reg_2d = LogisticRegression(max_iter=1000, random_state=42)
    log_reg_2d.fit(X_2d, y_2d)

    x_min, x_max = X_2d[:, 0].min() - 1, X_2d[:, 0].max() + 1
    y_min, y_max = X_2d[:, 1].min() - 1, X_2d[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                          np.linspace(y_min, y_max, 200))
    Z = log_reg_2d.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    axes[1, 2].contourf(xx, yy, Z, alpha=0.3, cmap='RdYlGn')
    axes[1, 2].scatter(X_2d[y_2d == 0, 0], X_2d[y_2d == 0, 1],
                       c='red', s=10, alpha=0.5, label='Baixa Ocupação')
    axes[1, 2].scatter(X_2d[y_2d == 1, 0], X_2d[y_2d == 1, 1],
                       c='green', s=10, alpha=0.5, label='Alta Ocupação')
    axes[1, 2].set_xlabel('APROVADA (normalizada)')
    axes[1, 2].set_ylabel('OCUPADA (normalizada)')
    axes[1, 2].set_title('Fronteira de Decisão')
    axes[1, 2].legend(fontsize=9)

    plt.tight_layout()
    plt.savefig('Graficos/regressao_logistica.png', dpi=150, bbox_inches='tight')
    print("    Gráfico salvo: Graficos/regressao_logistica.png")

    # --- Interpretação dos Coeficientes --

    print("\nOs coeficientes da Regressão Logística representam o log-odds:")
    print("Odds Ratio = e^(coeficiente)\n")

    for feat, coef in zip(features, log_reg.coef_[0]):
        odds_ratio = np.exp(coef)
        direcao = "aumenta" if coef > 0 else "diminui"
        print(f"  {feat:<15}: B = {coef:+.4f} | OR = {odds_ratio:.4f} | {direcao} a probabilidade de alta ocupação")

    return {
        'acc': acc_log, 'prec': prec_log, 'rec': rec_log, 'f1': f1_log,
        'log_reg': log_reg
    }
