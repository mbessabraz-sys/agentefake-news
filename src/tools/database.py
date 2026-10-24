from src.agent.state import KnowledgeChunk


KNOWLEDGE_BASE: list[KnowledgeChunk] = [
    {
        "fonte": "Conceitos",
        "texto": (
            "Fake news é conteúdo falso ou enganoso apresentado como se fosse notícia "
            "verdadeira. Pesquisadores preferem o termo 'desordem informacional', que "
            "separa: misinformation (informação falsa compartilhada sem intenção de "
            "causar dano), disinformation (falsa e criada de propósito para enganar) e "
            "malinformation (informação verdadeira usada para causar dano, como "
            "vazamento de dados privados)."
        ),
    },
    {
        "fonte": "Sinais de alerta",
        "texto": (
            "Sinais comuns de fake news: título sensacionalista em caixa alta, apelo "
            "forte à emoção (raiva, medo, indignação), ausência de autor, data ou "
            "fonte citada, erros de português, pedido para 'compartilhar urgente', "
            "e site desconhecido com endereço parecido com o de um veículo conhecido."
        ),
    },
    {
        "fonte": "Método SIFT",
        "texto": (
            "Método SIFT, de Mike Caulfield: Stop (pare antes de compartilhar), "
            "Investigate the source (investigue quem publicou), Find better coverage "
            "(procure cobertura em outros veículos confiáveis) e Trace claims "
            "(rastreie a afirmação, imagem ou citação até a origem)."
        ),
    },
    {
        "fonte": "Leitura lateral",
        "texto": (
            "Leitura lateral é abrir novas abas e pesquisar sobre a fonte, em vez de "
            "só ler a própria página. Verificadores profissionais fazem isso: "
            "descobrem quem está por trás do site, qual o histórico dele e o que "
            "outras fontes dizem sobre ele."
        ),
    },
    {
        "fonte": "Imagens e vídeos",
        "texto": (
            "Para checar imagens, use busca reversa (Google Lens, TinEye) e veja se a "
            "foto é antiga ou de outro contexto. Para vídeos, extraia quadros e busque "
            "a origem. Fique atento a deepfakes: rosto com bordas estranhas, piscar "
            "irregular, voz dessincronizada. Imagens geradas por IA podem ter mãos, "
            "textos e reflexos incoerentes."
        ),
    },
    {
        "fonte": "Agências de checagem",
        "texto": (
            "No Brasil, agências de checagem conhecidas incluem Aos Fatos, Agência "
            "Lupa, Projeto Comprova, Fato ou Fake (g1) e Boatos.org. Antes de "
            "compartilhar, pesquise o tema nesses sites."
        ),
    },
    {
        "fonte": "Vieses cognitivos",
        "texto": (
            "Caímos em fake news por viés de confirmação (acreditamos no que "
            "reforça o que já pensamos), efeito de repetição (o que vemos muitas "
            "vezes parece verdadeiro) e pelas bolhas dos algoritmos de redes sociais."
        ),
    },
]


def get_knowledge_base() -> list[KnowledgeChunk]:
    return KNOWLEDGE_BASE
