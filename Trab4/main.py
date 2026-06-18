import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, r2_score

import warnings
warnings.filterwarnings('ignore')

plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
sns.set_style('whitegrid')

from data_loader import carregar_e_preparar_dados, preparar_modelos
from knn_model import executar_knn
from regressao_linear import executar_regressao_linear
from regressao_multipla import executar_regressao_multipla
from regressao_logistica import executar_regressao_logistica


def comparar_modelos(result_knn, result_lr, result_multi, result_log):
    # Gera gráfico comparativo entre todos os modelos.

    print("\n--- Modelos de Classificação ---")
    print(f"{'Modelo':<25} {'Acurácia':<12} {'Precisão':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 73)
    print(f"{'KNN':<25} {result_knn['acc']:<12.4f} {result_knn['prec']:<12.4f} {result_knn['rec']:<12.4f} {result_knn['f1']:<12.4f}")
    print(f"{'Regressão Logística':<25} {result_log['acc']:<12.4f} {result_log['prec']:<12.4f} {result_log['rec']:<12.4f} {result_log['f1']:<12.4f}")

    print("\n--- Modelos de Regressão ---")
    print(f"{'Modelo':<30} {'RMSE':<12} {'R²':<12}")
    print("-" * 54)
    print(f"{'KNN Regressão':<30} {result_knn['rmse']:<12.4f} {result_knn['r2']:<12.4f}")
    print(f"{'Regressão Linear Simples':<30} {result_lr['rmse']:<12.4f} {result_lr['r2']:<12.4f}")
    print(f"{'Regressão Linear Múltipla':<30} {result_multi['rmse']:<12.4f} {result_multi['r2']:<12.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    modelos_clf = ['KNN', 'Regressão Logística']
    accs = [result_knn['acc'], result_log['acc']]
    f1s = [result_knn['f1'], result_log['f1']]

    x_pos = np.arange(len(modelos_clf))
    width = 0.35

    bars1 = axes[0].bar(x_pos - width/2, accs, width, label='Acurácia', color='#2196F3')
    bars2 = axes[0].bar(x_pos + width/2, f1s, width, label='F1-Score', color='#4CAF50')
    axes[0].set_xlabel('Modelo')
    axes[0].set_ylabel('Score')
    axes[0].set_title('Comparação: Modelos de Classificação')
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(modelos_clf)
    axes[0].legend()
    axes[0].set_ylim(0, 1.1)
    for bar in bars1:
        axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                     f'{bar.get_height():.3f}', ha='center', va='bottom')
    for bar in bars2:
        axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                     f'{bar.get_height():.3f}', ha='center', va='bottom')

    modelos_reg = ['KNN Reg', 'Linear Simples', 'Linear Múltipla']
    rmses = [result_knn['rmse'], result_lr['rmse'], result_multi['rmse']]
    r2s = [result_knn['r2'], result_lr['r2'], result_multi['r2']]

    x_pos2 = np.arange(len(modelos_reg))
    bars3 = axes[1].bar(x_pos2 - width/2, rmses, width, label='RMSE', color='#FF9800')
    bars4 = axes[1].bar(x_pos2 + width/2, r2s, width, label='R²', color='#9C27B0')
    axes[1].set_xlabel('Modelo')
    axes[1].set_ylabel('Valor')
    axes[1].set_title('Comparação: Modelos de Regressão')
    axes[1].set_xticks(x_pos2)
    axes[1].set_xticklabels(modelos_reg, rotation=15)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('Graficos/comparacao_modelos.png', dpi=150, bbox_inches='tight')


def main():
    # Função principal que executa todo o pipeline.

    # 1. Carregar e preparar dados
    df = carregar_e_preparar_dados('ano_completo_unificado.xlsx')
    dados = preparar_modelos(df)

    # 2. Executar modelos
    result_knn = executar_knn(dados)
    result_lr = executar_regressao_linear(dados)
    result_multi = executar_regressao_multipla(dados)
    result_log = executar_regressao_logistica(dados)

    # 3. Comparar modelos
    comparar_modelos(result_knn, result_lr, result_multi, result_log)

    # 4. Resumo final
    print("\n" + "=" * 70)
    print("TRABALHO CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print("\nGráficos gerados na pasta Graficos/:")
    print("  1. Graficos/knn_resultados.png")
    print("  2. Graficos/knn_regressao.png")
    print("  3. Graficos/regressao_linear_simples.png")
    print("  4. Graficos/regressao_linear_multipla.png")
    print("  5. Graficos/regressao_logistica.png")
    print("  6. Graficos/comparacao_modelos.png")

if __name__ == '__main__':
    main()
