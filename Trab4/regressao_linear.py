import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def executar_regressao_linear(dados):
    """Executa o modelo de Regressão Linear Simples."""

    print("\n" + "=" * 70)
    print("MODELO: REGRESSÃO LINEAR SIMPLES")
    print("=" * 70)

    df = dados['df']

    X_simple = df[['OCUPADA']].values
    y_simple = df['TAXA_OCUPACAO'].values

    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
        X_simple, y_simple, test_size=0.3, random_state=42
    )

    lr_simple = LinearRegression()
    lr_simple.fit(X_train_s, y_train_s)
    y_pred_lr_simple = lr_simple.predict(X_test_s)

    rmse = np.sqrt(mean_squared_error(y_test_s, y_pred_lr_simple))
    r2 = r2_score(y_test_s, y_pred_lr_simple)

    print(f"    Coeficiente (B1): {lr_simple.coef_[0]:.6f}")
    print(f"    Intercepto (B0):  {lr_simple.intercept_:.6f}")
    print(f"    RMSE: {rmse:.4f}")
    print(f"    R²:   {r2:.4f}")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    axes[0].scatter(X_test_s, y_test_s, alpha=0.3, s=10, label='Dados Reais')
    x_line = np.linspace(X_test_s.min(), X_test_s.max(), 100).reshape(-1, 1)
    y_line = lr_simple.predict(x_line)
    axes[0].plot(x_line, y_line, 'r-', linewidth=2, label=f'y = {lr_simple.coef_[0]:.4f}x + {lr_simple.intercept_:.4f}')
    axes[0].set_xlabel('OCUPADA')
    axes[0].set_ylabel('TAXA_OCUPACAO')
    axes[0].set_title('Regressão Linear Simples')
    axes[0].legend()

    axes[1].scatter(y_test_s, y_pred_lr_simple, alpha=0.5, s=10)
    axes[1].plot([y_test_s.min(), y_test_s.max()], [y_test_s.min(), y_test_s.max()], 'r--', linewidth=2)
    axes[1].set_xlabel('Valor Real')
    axes[1].set_ylabel('Valor Predito')
    axes[1].set_title(f'Real vs Predito (R²={r2:.3f})')

    residuos_lr = y_test_s - y_pred_lr_simple
    axes[2].scatter(y_pred_lr_simple, residuos_lr, alpha=0.5, s=10)
    axes[2].axhline(y=0, color='r', linestyle='--')
    axes[2].set_xlabel('Valor Predito')
    axes[2].set_ylabel('Resíduo')
    axes[2].set_title('Análise de Resíduos')

    plt.tight_layout()
    plt.savefig('Graficos/regressao_linear_simples.png', dpi=150, bbox_inches='tight')
    print("    Gráfico salvo: Graficos/regressao_linear_simples.png")

    return {'rmse': rmse, 'r2': r2}
