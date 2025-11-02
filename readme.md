## PixelMaker

PixelMaker é uma ferramenta de edição focada em pixel art e manipulação de paletas de cores. Fornece uma interface gráfica para carregar imagens, editar paletas (individualmente ou em lote), aplicar alterações de cores e exportar o resultado. O projeto foi desenvolvido em Python com uma interface modular organizada na pasta `src/`.

## Objetivo

O objetivo principal do PixelMaker é transformar imagens de alta resolução (por exemplo, geradas por IA) em sprites usáveis e visualmente agradáveis para jogos, interfaces e pixel art. Ele é parte de um fluxo que desenvolvi para:
- Reduzir e normalizar a resolução preservando silhuetas e detalhes essenciais para sprite (downscale e posterização seletiva);
- Extrair e quantizar paletas de cores apropriadas para sprites e workflows de jogos;
- Editar paletas manualmente ou em lote, remapear cores e aplicar substituições controladas;
- Realizar limpeza de pixels (correções manuais, remoção de artefatos gerados por downscaling) e aplicar dithering quando desejado;
- Fatiar, recortar e exportar sprites como imagens individuais, sprite sheets ou PNGs indexados com paleta.

## Como funciona (visão geral)

O software é composto por módulos que se encarregam de responsabilidades específicas:

- `src/main_window.py`: Janela principal e ponto de entrada da interface gráfica.
- `src/art_processor.py`: Funções de processamento de imagem (leitura, redimensionamento por vizinhança, aplicação de paleta, etc.).
- `src/palette_processor.py`: Lógica para manipular paletas — carregar, salvar, editar cores e operações em lote.
- `src/stylesheet.py`: Estilos e aparências usados pela interface.
- `src/ui/` (pacote): Componentes da interface (carregador de arquivos, visualizador de imagem, editores de paleta, grupos de controles, etc.).

Fluxo típico de uso (foco: transformar imagens de IA em sprites):
1. O usuário abre o aplicativo (`main.py`).
2. Carrega uma imagem de alta resolução (gerada por IA) via menu ou arrastar e soltar.
3. Escolhe o tamanho alvo do sprite / fator de redução e pré-visualiza o downscale (modos de amostragem e parâmetros).
4. O aplicativo sugere uma paleta extraída da imagem; o usuário pode quantizar automaticamente ou ajustar no `palette_editor`/`palette_bulk_editor`.
5. O `art_processor` aplica a quantização e o usuário faz limpeza manual de pixels, ajustes de contraste/limiar e, opcionalmente, aplica dithering.
6. O usuário recorta/fatia a imagem em sprites, ajusta alinhamentos e exporta como PNG individuais, sprite sheet ou imagens indexadas com a paleta final.

## Requisitos

- Python 3.8+ (recomendado 3.10/3.11)
- Dependências listadas em `requirements.txt` (use o virtual environment do Python)

## Instalação e execução (Windows / PowerShell)

1. Crie um ambiente virtual e ative-o:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Instale dependências:

```powershell
pip install -r requirements.txt
```

3. Execute o aplicativo:

```powershell
python main.py
```

Observação: se o seu sistema bloquear a execução do script de ativação do PowerShell (política de execução), execute como administrador:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Estrutura do projeto

- `main.py` — script de inicialização do aplicativo.
- `requirements.txt` — dependências do Python.
- `src/` — código-fonte principal.
	- `main_window.py` — GUI principal.
	- `art_processor.py` — processamento de imagens e operações de pixel art.
	- `palette_processor.py` — manipulação de paletas de cores.
	- `stylesheet.py` — temas/estilos para a interface.
	- `ui/` — widgets e componentes da interface (carregadores, editores, displays).

## Boas práticas e notas técnicas

- Trabalhe sempre em um ambiente virtual.
- Faça backup de paletas antes de operações em lote.
- Arquivos de paleta podem ser salvo/compartilhados para reutilização.

Edge cases comuns:
- Imagens com mais cores do que a paleta: comportamentos esperados incluem indexação por cor mais próxima ou mapeamento explícito.
- Arquivos de imagem corrompidos ou formatos não suportados: o app deve apresentar uma mensagem de erro clara.