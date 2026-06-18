from torchvision.datasets import ImageFolder
from torch.utils.data import Subset
import numpy as np
import matplotlib.pyplot as plt
import cv2
from sklearn.cluster import KMeans

PASTA_DATASET = "caltech-101"
IMG_SIZE = 224
CATEGORIAS = ["beaver", "cougar_face", "crocodile", "okapi", "Leopards"]
IMAGENS_POR_CATEGORIA = 5
IMAGENS_QUERY_POR_CATEGORIA = 1
N_CLUSTERS = 100

# Parâmetros de pós-processamento
LIMITE_DIFERENCA_FORMATO = 0.15   # filtro por formato: diferença máxima de circularidade aceita
N_CLUSTERS_POS = 5                # cluster: número de grupos para re-ranking
BONUS_CLUSTER = 0.25              # cluster: bônus adicionado ao score do cluster da query


# ── Dataset ───────────────────────────────────────────────────────────────────

def carregar_datasets(categorias=None, imagens_por_categoria=5, n_query=1):
    """
    Retorna dois Subsets separados:
      - dataset_docs:   imagens usadas como base de documentos
      - dataset_query:  imagens usadas como queries (nunca aparecem nos docs)
    """
    dataset = ImageFolder(root=PASTA_DATASET)

    if categorias:
        cats_validas = {dataset.class_to_idx[c] for c in categorias}
    else:
        cats_validas = set(range(len(dataset.classes)))

    indices_docs = []
    indices_query = []

    for label in cats_validas:
        indices_cat = [
            idx for idx, (_, l) in enumerate(dataset.imgs)
            if l == label
        ][:imagens_por_categoria]

        indices_query.extend(indices_cat[-n_query:])
        indices_docs.extend(indices_cat[:-n_query])

    return (
        Subset(dataset, indices_docs),
        Subset(dataset, indices_query),
        dataset
    )


def preprocessar_imagem(img_pil):
    img = img_pil.convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE))
    return np.array(img)


# ── Regiões ───────────────────────────────────────────────────────────────────

def gerar_regioes_grid(img_size=IMG_SIZE, grid_size=3):
    regioes = []
    cell_w = img_size // grid_size
    cell_h = img_size // grid_size
    for linha in range(grid_size):
        for coluna in range(grid_size):
            x = coluna * cell_w
            y = linha * cell_h
            regioes.append((x, y, cell_w, cell_h))
    return regioes


def selecionar_regiao_query(img, query_idx, classe):
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    titulo = f"Query {query_idx} - {classe} | Selecione a regiao e pressione ENTER"
    print(f"\n[Query {query_idx}] Selecione a região na janela e pressione ENTER.")
    bbox = cv2.selectROI(titulo, img_bgr, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    x, y, w, h = bbox
    if w == 0 or h == 0:
        print("Nenhuma região selecionada. Usando região central como padrão.")
        q = IMG_SIZE // 4
        return (q, q, IMG_SIZE // 2, IMG_SIZE // 2)
    return (int(x), int(y), int(w), int(h))


# ── SIFT + BoVW ───────────────────────────────────────────────────────────────
sift = cv2.SIFT_create()

def extrair_descritores_sift(img, bbox):
    x, y, w, h = bbox
    regiao = img[y:y+h, x:x+w]
    gray = cv2.cvtColor(regiao, cv2.COLOR_RGB2GRAY)
    _, descritores = sift.detectAndCompute(gray, None)
    return descritores


def criar_vocabulario(todos_descritores, n_clusters):
    descritores_concat = np.vstack(todos_descritores).astype(np.float32)
    print(f"Total de descritores SIFT para K-means: {len(descritores_concat)}")
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, _, centros = cv2.kmeans(
        descritores_concat, n_clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )
    return centros


def construir_histograma(descritores, centros, n_clusters):
    if descritores is None:
        return np.zeros(n_clusters)
    dist = np.linalg.norm(descritores[:, np.newaxis] - centros[np.newaxis, :], axis=2)
    palavras = np.argmin(dist, axis=1)
    hist, _ = np.histogram(palavras, bins=n_clusters, range=(0, n_clusters))
    hist = hist.astype(np.float32)
    hist /= (np.linalg.norm(hist) + 1e-8)
    return hist


# ── Indexação ─────────────────────────────────────────────────────────────────

def indexar_documentos(dataset_docs, n_clusters=N_CLUSTERS):
    regioes = gerar_regioes_grid()

    print("Extraindo descritores SIFT dos documentos...")
    todos_descritores = []
    entradas = []

    for doc_id, (img_pil, label) in enumerate(dataset_docs):
        img = preprocessar_imagem(img_pil)
        for bbox in regioes:
            des = extrair_descritores_sift(img, bbox)
            if des is not None:
                todos_descritores.append(des)
            entradas.append((des, label, doc_id, bbox, img))

    print(f"Criando vocabulário com {n_clusters} palavras visuais...")
    centros = criar_vocabulario(todos_descritores, n_clusters)

    print("Construindo histogramas BoVW por região...")
    indice = []
    for des, label, doc_id, bbox, img in entradas:
        hist = construir_histograma(des, centros, n_clusters)
        indice.append({
            "doc_id": doc_id,
            "label": label,
            "bbox": bbox,
            "histograma": hist,
            "imagem": img
        })

    return indice, centros


# ── Similaridade e IoU ────────────────────────────────────────────────────────

def similaridade_cosseno(hist_a, hist_b):
    norm_a = np.linalg.norm(hist_a)
    norm_b = np.linalg.norm(hist_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return np.dot(hist_a, hist_b) / (norm_a * norm_b)


def calcular_iou(box_a, box_b):
    xA = max(box_a[0], box_b[0])
    yA = max(box_a[1], box_b[1])
    xB = min(box_a[0] + box_a[2], box_b[0] + box_b[2])
    yB = min(box_a[1] + box_a[3], box_b[1] + box_b[3])
    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    area_inter = inter_w * inter_h
    area_a = box_a[2] * box_a[3]
    area_b = box_b[2] * box_b[3]
    area_uniao = area_a + area_b - area_inter
    if area_uniao == 0:
        return 0.0
    return area_inter / area_uniao


def buscar_query(query_img, indice, centros, bbox_query, top_k=5):
    des_q = extrair_descritores_sift(query_img, bbox_query)
    hist_query = construir_histograma(des_q, centros, N_CLUSTERS)

    # Calcula sim e IoU para TODAS as regiões de todos os documentos
    todos_candidatos = []
    for item in indice:
        sim = similaridade_cosseno(hist_query, item["histograma"])
        iou = calcular_iou(bbox_query, item["bbox"])
        todos_candidatos.append({**item, "similaridade": sim, "iou": iou})

    # ── Ranking por Similaridade ──────────────────────────────────────────
    melhores_sim = {}
    for c in todos_candidatos:
        doc_id = c["doc_id"]
        if doc_id not in melhores_sim or c["similaridade"] > melhores_sim[doc_id]["similaridade"]:
            melhores_sim[doc_id] = c

    ranking_sim = sorted(
        melhores_sim.values(),
        key=lambda x: x["similaridade"],
        reverse=True
    )[:top_k]

    # ── Ranking por IoU ───────────────────────────────────────────────────
    melhores_iou = {}
    for c in todos_candidatos:
        doc_id = c["doc_id"]
        if doc_id not in melhores_iou or c["iou"] > melhores_iou[doc_id]["iou"]:
            melhores_iou[doc_id] = c

    ranking_iou = sorted(
        melhores_iou.values(),
        key=lambda x: (x["iou"], x["similaridade"]),
        reverse=True
    )[:top_k]

    return ranking_sim, ranking_iou, hist_query


# ── Pós-processamento 1: Filtro por Formato ───────────────────────────────────

def calcular_circularidade(img_rgb, bbox=None):
    """
    Calcula a circularidade do maior contorno encontrado em uma região da imagem.
    Circularidade = 4π·área / perímetro², vale 1.0 para um círculo perfeito.

    - Para a query: bbox é a ROI selecionada pelo usuário — usa exatamente essa região.
    - Para documentos: bbox=None, usa a imagem inteira (detecção automática do objeto
      principal), equivalente ao que o usuário fez manualmente na query.
    """
    if bbox is not None:
        x, y, w, h = bbox
        recorte = img_rgb[y:y+h, x:x+w]
    else:
        recorte = img_rgb

    cinza = cv2.cvtColor(recorte, cv2.COLOR_RGB2GRAY)

    # Otsu adapta o limiar automaticamente, mais robusto que threshold fixo
    _, binaria = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contornos) == 0:
        return 0.0

    maior = max(contornos, key=cv2.contourArea)
    area = cv2.contourArea(maior)
    perimetro = cv2.arcLength(maior, True)

    if perimetro == 0:
        return 0.0

    return (4 * np.pi * area) / (perimetro ** 2)


def filtrar_por_formato(ranking, query_img, bbox_query, limite_diferenca=LIMITE_DIFERENCA_FORMATO):
    """
    Filtra o ranking comparando o formato da ROI selecionada pelo usuário na query
    com o formato detectado automaticamente em cada documento (imagem inteira).

    A query usa a bbox exata do usuário; os documentos não têm bbox do usuário,
    então o maior contorno é detectado na imagem completa do documento.
    Percorre o ranking completo para que candidatos além do top-k possam
    reposicionar-se após remoções.
    """
    circ_query = calcular_circularidade(query_img, bbox=bbox_query)

    mantidos = []
    removidos = []

    for item in ranking:
        # Imagem inteira do documento — sem bbox fixa de grid
        circ_item = calcular_circularidade(item["imagem"], bbox=None)
        diferenca = abs(circ_query - circ_item)
        item_anotado = {**item, "circularidade": circ_item, "dif_formato": diferenca}

        if diferenca <= limite_diferenca:
            mantidos.append(item_anotado)
        else:
            removidos.append(item_anotado)

    print(f"  [Filtro Formato] circularidade query={circ_query:.3f} | "
          f"mantidos={len(mantidos)} | removidos={len(removidos)}")

    return mantidos, removidos, circ_query


# ── Pós-processamento 2: Re-ranking por Cluster ───────────────────────────────

def reranking_por_cluster(ranking, hist_query, n_clusters=N_CLUSTERS_POS, bonus=BONUS_CLUSTER):
    """
    Agrupa os candidatos do ranking via KMeans sobre seus histogramas BoVW.
    O cluster ao qual o histograma da query pertence recebe um bônus no score,
    promovendo candidatos visualmente similares à query no ranking final.
    """
    if len(ranking) < n_clusters:
        # Menos candidatos que clusters: reduz k para evitar erro do KMeans
        n_clusters = max(2, len(ranking))

    histogramas = np.array([item["histograma"] for item in ranking])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(histogramas)
    cluster_query = kmeans.predict(hist_query.reshape(1, -1))[0]

    ranking_novo = []
    for item, cluster_id in zip(ranking, clusters):
        bonus_item = bonus if cluster_id == cluster_query else 0.0
        score_final = item["similaridade"] + bonus_item
        ranking_novo.append({
            **item,
            "cluster": int(cluster_id),
            "cluster_query": int(cluster_query),
            "bonus_cluster": bonus_item,
            "score_final": score_final
        })

    ranking_novo.sort(key=lambda x: x["score_final"], reverse=True)

    n_promovidos = sum(1 for i in ranking_novo if i["bonus_cluster"] > 0)
    print(f"  [Re-ranking Cluster] cluster query={cluster_query} | "
          f"candidatos promovidos={n_promovidos} / {len(ranking_novo)}")

    return ranking_novo, cluster_query


# ── Visualização ──────────────────────────────────────────────────────────────

def visualizar_amostras(imagens, labels, classes):
    for cat_idx in sorted(set(labels)):
        nome_cat = classes[cat_idx]
        imgs_cat = [imagens[i] for i, l in enumerate(labels) if l == cat_idx]

        fig, axes = plt.subplots(1, len(imgs_cat), figsize=(15, 3))
        if len(imgs_cat) == 1:
            axes = [axes]
        for i, img in enumerate(imgs_cat):
            axes[i].imshow(img)
            axes[i].axis("off")

        fig.suptitle(nome_cat)
        plt.tight_layout()
        plt.savefig(f"amostras_{nome_cat}.png")
        plt.close()
        print(f"Salvo: amostras_{nome_cat}.png")


def visualizar_recuperacao(query_idx, query_img, bbox_query, label_query,
                            ranking_sim, ranking_iou,
                            ranking_formato, ranking_cluster,
                            classes):
    """
    Gera quatro figuras por query:
      1. Ranking por Similaridade Visual (baseline)
      2. Ranking por IoU
      3. Pós-processamento: Filtro por Formato
      4. Pós-processamento: Re-ranking por Cluster
    """
    configs = [
        ("Ranking por Similaridade Visual",  ranking_sim,     "sim",     False, None),
        ("Ranking por IoU",                  ranking_iou,     "iou",     True,  None),
        ("Pós-proc.: Filtro por Formato",    ranking_formato, "formato", False, "dif_formato"),
        ("Pós-proc.: Re-ranking por Cluster",ranking_cluster, "cluster", False, "score_final"),
    ]

    for titulo, ranking, sufixo, usar_bbox_res, campo_extra in configs:
        if not ranking:
            print(f"  [Aviso] Ranking '{sufixo}' vazio, pulando visualização.")
            continue

        n = len(ranking)
        fig, axes = plt.subplots(1, n + 1, figsize=(3 * (n + 1), 3))

        img_q = query_img.copy()
        x, y, w, h = bbox_query
        cv2.rectangle(img_q, (x, y), (x+w, y+h), (255, 0, 0), 2)
        axes[0].imshow(img_q)
        axes[0].set_title(f"QUERY\n{classes[label_query]}", fontweight="bold")
        axes[0].axis("off")

        for i, res in enumerate(ranking):
            img_res = res["imagem"].copy()
            if usar_bbox_res:
                rx, ry, rw, rh = res["bbox"]
                cv2.rectangle(img_res, (rx, ry), (rx+rw, ry+rh), (0, 255, 0), 2)

            acerto = res["label"] == label_query
            cor = "green" if acerto else "red"

            # Linha de score principal
            if sufixo == "iou":
                score_str = f"IoU: {res['iou']:.2f}"
            elif sufixo == "cluster":
                score_str = f"Score: {res['score_final']:.2f}"
                if res["bonus_cluster"] > 0:
                    score_str += " ★"
            elif sufixo == "formato":
                score_str = f"Sim: {res['similaridade']:.2f}"
                score_str += f"\nΔcirc: {res['dif_formato']:.3f}"
            else:
                score_str = f"Sim: {res['similaridade']:.2f}"

            axes[i+1].imshow(img_res)
            axes[i+1].set_title(
                f"Top-{i+1}\n{classes[res['label']]}\n{score_str}",
                color=cor, fontsize=8
            )
            axes[i+1].axis("off")

        plt.suptitle(titulo)
        plt.tight_layout()
        plt.savefig(f"recuperacao_query{query_idx}_{sufixo}.png")
        plt.close()
        print(f"Salvo: recuperacao_query{query_idx}_{sufixo}.png")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    dataset_docs, dataset_query, dataset_base = carregar_datasets(
        categorias=CATEGORIAS,
        imagens_por_categoria=IMAGENS_POR_CATEGORIA,
        n_query=IMAGENS_QUERY_POR_CATEGORIA
    )

    classes = dataset_base.classes

    print(f"Documentos: {len(dataset_docs)} | Queries: {len(dataset_query)}")

    # Visualiza documentos
    imagens_docs, labels_docs = [], []
    for img_pil, label in dataset_docs:
        imagens_docs.append(preprocessar_imagem(img_pil))
        labels_docs.append(label)
    visualizar_amostras(imagens_docs, labels_docs, classes)

    # Indexa apenas os documentos
    indice, centros = indexar_documentos(dataset_docs, n_clusters=N_CLUSTERS)
    print(f"\nIndexação concluída! Total de regiões indexadas: {len(indice)}")

    # Executa queries com imagens separadas
    print("\nExecutando recuperação com imagens de query separadas...")
    for query_idx, (img_pil, label_query) in enumerate(dataset_query):
        query_img = preprocessar_imagem(img_pil)
        bbox_query = selecionar_regiao_query(query_img, query_idx, classes[label_query])

        # Rankings base
        ranking_sim, ranking_iou, hist_query = buscar_query(
            query_img, indice, centros,
            bbox_query=bbox_query,
            top_k=5
        )

        print(f"\n[Query {query_idx}] Aplicando pós-processamento...")

        # ── Pós-processamento 1: Filtro por Formato ───────────────────────
        # Usa o ranking_sim completo (sem corte top_k) para que candidatos
        # removidos abram espaço para outros. Por isso buscamos top_k ampliado.
        ranking_sim_amplo, _, hist_query = buscar_query(
            query_img, indice, centros,
            bbox_query=bbox_query,
            top_k=len(indice)   # todos os documentos
        )
        mantidos_formato, _, circ_query = filtrar_por_formato(
            ranking_sim_amplo, query_img, bbox_query,
            limite_diferenca=LIMITE_DIFERENCA_FORMATO
        )
        ranking_formato = mantidos_formato[:5]  # top-5 após filtro

        # ── Pós-processamento 2: Re-ranking por Cluster ───────────────────
        # Opera sobre o ranking amplo (todos os documentos) para que o KMeans
        # tenha candidatos suficientes para formar grupos significativos.
        # Após o agrupamento e aplicação do bônus, corta no top-5.
        ranking_cluster_amplo, cluster_query = reranking_por_cluster(
            ranking_sim_amplo, hist_query,
            n_clusters=N_CLUSTERS_POS,
            bonus=BONUS_CLUSTER
        )
        ranking_cluster = ranking_cluster_amplo[:5]

        visualizar_recuperacao(
            query_idx, query_img, bbox_query, label_query,
            ranking_sim, ranking_iou,
            ranking_formato, ranking_cluster,
            classes
        )

if __name__ == "__main__":
    main()