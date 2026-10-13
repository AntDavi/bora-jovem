"""Conteúdo do MVP: trilhas de economia criativa e oportunidades locais (dados de exemplo)."""

TRILHAS = {
    "audiovisual": {
        "descricao": 'Produzir e editar vídeos curtos para comércios, artistas e redes sociais.',
        "perspectiva": 'Prestar serviço de vídeo para o comércio do bairro (R$ 80–150 por vídeo) ou entrar como editor júnior em produtoras e agências.',
        "requisitos": ['foto'],
        "nome": "🎬 Audiovisual",
        "licoes": [
            ("Seu celular é um estúdio", "Aprenda luz natural, enquadramento e estabilidade. Desafio: grave 30s de algo do seu bairro, perto de uma janela."),
            ("Edição básica no celular", "Baixe o CapCut (grátis). Corte, junte clipes e ponha legenda. Desafio: edite o vídeo de ontem em 3 cortes."),
            ("Conte uma história em 30s", "Começo (gancho), meio, fim. Desafio: faça um vídeo mostrando o 'antes e depois' de um comércio local."),
            ("Monte seu portfólio", "Crie um perfil no Instagram só com seus melhores 6 trabalhos. Desafio: poste 3 vídeos e mande o link aqui."),
            ("Como cobrar pelo trabalho", "Cobre por entrega, não por hora. Comece com R$ 80–150 por vídeo curto para comércios. Desafio: monte sua tabela de preços."),
        ],
    },
    "musica": {
        "descricao": 'Criar, gravar e distribuir suas próprias músicas usando só o celular.',
        "perspectiva": 'Lançar faixas, fazer shows em eventos locais e produzir para outros artistas do bairro.',
        "requisitos": [],
        "nome": "🎵 Música",
        "licoes": [
            ("Produza com o celular", "Apps como BandLab (grátis) gravam e mixam. Desafio: grave uma base de 8 compassos."),
            ("Letra e flow", "Estruture 16 barras: tema, rima, refrão. Desafio: escreva 16 barras sobre sua quebrada."),
            ("Mixagem simples", "Equalize voz e base, tire ruídos. Desafio: mixe sua gravação e compare com uma música que você curte."),
            ("Distribuição e presença", "Publique no YouTube e plataformas de streaming por distribuidores gratuitos. Desafio: lance 1 faixa."),
            ("Shows e trampos", "Procure eventos locais, saraus e batalhas. Desafio: mande mensagem para 3 organizadores."),
        ],
    },
    "design": {
        "descricao": 'Criar artes e identidade visual para pequenos negócios.',
        "perspectiva": 'Atender comércios com logos e posts (R$ 200+ por pacote) e abrir caminho para vagas de designer júnior.',
        "requisitos": [],
        "nome": "🎨 Design e Moda",
        "licoes": [
            ("Fundamentos visuais", "Cor, contraste e tipografia. Desafio: refaça o cartaz de um comércio do bairro no Canva (grátis)."),
            ("Identidade para pequenos negócios", "Logo simples + 2 cores + 1 fonte. Desafio: crie a identidade de um negócio fictício."),
            ("Posts para redes sociais", "Modelos de feed e stories que vendem. Desafio: crie 5 posts para um comércio real."),
            ("Estampa e customização", "Transforme arte em produto: camisetas, ecobags. Desafio: desenhe 1 estampa e peça orçamento de impressão."),
            ("Fechando seu primeiro cliente", "Ofereça um pacote fechado (logo + 5 posts). Desafio: ofereça para 5 comércios do bairro."),
        ],
    },
    "foto": {
        "descricao": 'Fazer fotos profissionais de produtos, eventos e ensaios com o celular.',
        "perspectiva": 'Vender ensaios e fotos de produtos (R$ 100–300) e abrir caminho para as trilhas de vídeo.',
        "requisitos": [],
        "nome": "📸 Fotografia",
        "licoes": [
            ("Luz e composição", "Regra dos terços e luz da manhã/fim de tarde. Desafio: 10 fotos do mesmo lugar em horários diferentes."),
            ("Fotografia de produto", "Fundo liso, luz lateral. Desafio: fotografe 5 produtos de um vendedor local."),
            ("Edição no Lightroom Mobile", "Brilho, contraste e cor. Desafio: edite 5 fotos com o mesmo estilo."),
            ("Ensaios e eventos", "Aniversários, formaturas e ensaios são trampos frequentes. Desafio: faça um ensaio com um amigo."),
            ("Venda seu trabalho", "Pacotes de fotos por R$ 100–300. Desafio: monte um pacote e divulgue no WhatsApp."),
        ],
    },
}

# Oportunidades de exemplo (para o MVP). bairro "*" = remoto/qualquer lugar.
OPORTUNIDADES = [
    {"titulo": "Vídeos curtos para padaria", "bairro": "Capão Redondo", "trilha": "audiovisual", "pagamento": "R$ 150/vídeo", "contato": "@padaria_capao"},
    {"titulo": "Cartaz e posts para salão de beleza", "bairro": "Brasilândia", "trilha": "design", "pagamento": "R$ 200 (pacote)", "contato": "@salao_brasilandia"},
    {"titulo": "Fotos de produtos de brechó", "bairro": "Paraisópolis", "trilha": "foto", "pagamento": "R$ 120/sessão", "contato": "@brecho_paraisopolis"},
    {"titulo": "Produtor para sarau mensal", "bairro": "Capão Redondo", "trilha": "musica", "pagamento": "R$ 100/evento", "contato": "@sarau_capao"},
    {"titulo": "Edição de vídeos para ONG de bairro", "bairro": "Heliópolis", "trilha": "audiovisual", "pagamento": "R$ 300/mês", "contato": "@ong_helio"},
    {"titulo": "Estampas para coletivo de moda", "bairro": "Brasilândia", "trilha": "design", "pagamento": "R$ 80/estampa", "contato": "@coletivo_moda"},
    {"titulo": "Freelas de edição de vídeo (remoto)", "bairro": "*", "trilha": "audiovisual", "pagamento": "R$ 100–250/vídeo", "contato": "@freela_video"},
]

# Anamnese: respostas por botão (chave -> rótulo)
SITUACOES = {
    "estuda": "📚 Só estudo",
    "trabalha": "💼 Só trabalho",
    "ambos": "📚💼 Estudo e trabalho",
    "nemnem": "🏠 Nem estudo nem trabalho no momento",
}
OBJETIVOS = {
    "renda": "💰 Renda extra",
    "emprego": "🧑‍💼 Primeiro emprego / entrar no mercado",
    "negocio": "🚀 Ter meu próprio negócio / prestar serviço",
    "profissao": "🎓 Aprender uma profissão",
}
# interesse -> trilha que ele leva
GOSTOS = {
    "video": ("🎬 Filmar e editar vídeos", "audiovisual"),
    "musica": ("🎵 Música", "musica"),
    "arte": ("🎨 Desenhar e criar artes", "design"),
    "foto": ("📸 Fotografar", "foto"),
}
