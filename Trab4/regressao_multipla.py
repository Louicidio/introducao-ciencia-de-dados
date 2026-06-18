import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def executar_regressao_multipla(dados):
    # Executa o modelo de Regressão Linear Múltipla.
    df = dados['df']

    X_multi = df[['APROVADA', 'DISTRIBUIDA', 'OCUPADA', 'VAGAS']].values
    y_multi = df['TAXA_OCUPACAO'].values

    X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
        X_multi, y_multi, test_size=0.3, random_state=42
    )

    lr_multi = LinearRegression()
    lr_multi.fit(X_train_m, y_train_m)
    y_pred_lr_multi = lr_multi.predict(X_test_m)

    rmse = np.sqrt(mean_squared_error(y_test_m, y_pred_lr_multi))
    r2 = r2_score(y_test_m, y_pred_lr_multi)

    print(f"    Coeficientes:")
    for feat, coef in zip(['APROVADA', 'DISTRIBUIDA', 'OCUPADA', 'VAGAS'], lr_multi.coef_):
        print(f"      {feat}: {coef:.6f}")
    print(f"    Intercepto: {lr_multi.intercept_:.6f}")
    print(f"    RMSE: {rmse:.4f}")
    print(f"    R²:   {r2:.4f}")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].scatter(y_test_m, y_pred_lr_multi, alpha=0.5, s=10)
    axes[0, 0].plot([y_test_m.min(), y_test_m.max()], [y_test_m.min(), y_test_m.max()], 'r--', linewidth=2)
    axes[0, 0].set_xlabel('Valor Real')
    axes[0, 0].set_ylabel('Valor Predito')
    axes[0, 0].set_title(f'Regressão Múltipla: Real vs Predito (R²={r2:.3f})')

    residuos_multi = y_test_m - y_pred_lr_multi
    axes[0, 1].scatter(y_pred_lr_multi, residuos_multi, alpha=0.5, s=10)
    axes[0, 1].axhline(y=0, color='r', linestyle='--')
    axes[0, 1].set_xlabel('Valor Predito')
    axes[0, 1].set_ylabel('Resíduo')
    axes[0, 1].set_title('Análise de Resíduos')

    feature_names = ['APROVADA', 'DISTRIBUIDA', 'OCUPADA', 'VAGAS']
    coefs_abs = np.abs(lr_multi.coef_)
    bars = axes[1, 0].barh(feature_names, coefs_abs, color=['#2196F3', '#4CAF50', '#FF9800', '#F44336'])
    axes[1, 0].set_xlabel('|Coeficiente|')
    axes[1, 0].set_title('Importância das Features (|coeficiente|)')

    axes[1, 1].hist(residuos_multi, bins=30, color='#2196F3', edgecolor='black', alpha=0.7)
    axes[1, 1].axvline(x=0, color='r', linestyle='--')
    axes[1, 1].set_xlabel('Resíduo')
    axes[1, 1].set_ylabel('Frequência')
    axes[1, 1].set_title('Distribuição dos Resíduos')

    plt.tight_layout()
    plt.savefig('Graficos/regressao_linear_multipla.png', dpi=150, bbox_inches='tight')
    print("    Gráfico salvo: Graficos/regressao_linear_multipla.png")

    return {'rmse': rmse, 'r2': r2}
