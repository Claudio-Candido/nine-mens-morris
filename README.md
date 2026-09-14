# Trilha — Nine Men's Morris

[![Licença: MIT](https://img.shields.io/badge/Licença-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black.svg)](https://flask.palletsprojects.com/)

Aplicação web do jogo clássico **Nine Men's Morris** (conhecido em português como **Trilha** ou **Moinho**), implementada em **Python + Flask** com interface moderna em HTML/CSS/JavaScript.

Dois jogadores alternam turnos no mesmo browser. O estado do jogo é mantido em sessão Flask.

---

## Índice

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Regras do jogo](#regras-do-jogo)
- [Stack tecnológica](#stack-tecnológica)
- [Arquitetura](#arquitetura)
- [API HTTP](#api-http)
- [Instalação e execução](#instalação-e-execução)
- [Testes](#testes)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Licença](#licença)

---

## Visão geral

O **Nine Men's Morris** é um jogo de estratégia milenar (origem romana / medieval) jogado num tabuleiro com 24 interseções e três fases distintas:

1. **Colocação** — cada jogador coloca 9 peças.
2. **Movimento** — peças deslocam-se para posições adjacentes.
3. **Voo (flying)** — quando restam 3 peças, o jogador pode saltar para qualquer casa livre.

O objetivo é formar **moinhos** (três peças alinhadas) e, com isso, remover peças do adversário. Vence quem reduzir o oponente a menos de 3 peças ou o bloquear completamente.

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| Tabuleiro interativo | SVG com 24 posições, linhas e destaques visuais |
| Três fases oficiais | Colocação → Movimento → Voo |
| Formação de moinhos | Detecção automática e obrigação de remover peça adversária |
| Regra de proteção de moinho | Não se remove peça que está em moinho (salvo se todas estiverem protegidas) |
| Condições de vitória | Menos de 3 peças ou bloqueio total de movimentos |
| Reinício de partida | Botão para recomeçar a qualquer momento |
| Modal de regras | Resumo das regras dentro da interface |
| Sessão por browser | Estado persistente durante a sessão Flask |
| Interface em português | Textos, mensagens e labels em PT |

---

## Regras do jogo

### Fases

1. **Fase 1 — Colocação**  
   Cada jogador, alternadamente, coloca uma peça numa interseção vazia. Quem forma um moinho remove imediatamente uma peça do oponente (que não esteja num moinho, se possível).

2. **Fase 2 — Movimento**  
   Após todas as 18 peças estarem no tabuleiro, move-se uma peça própria para uma casa **adjacente** livre. Formar moinho → remover peça adversária.

3. **Fase 3 — Voo**  
   Quando um jogador fica com apenas **3 peças**, pode mover qualquer uma das suas peças para **qualquer** casa livre (não precisa de adjacência).

### Vitória

- O oponente fica com **menos de 3 peças**, **ou**
- O oponente **não tem nenhum movimento legal** (bloqueio).

### Moinhos

Um moinho é qualquer linha de três peças da mesma cor nas 16 linhas oficiais do tabuleiro (4 por quadrado + 4 raios).

---

## Stack tecnológica

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3.10+, Flask |
| Lógica de jogo | Módulo puro Python (`game_logic.py`) |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| Tabuleiro | SVG gerado dinamicamente |
| Estado | Sessão Flask (`session`) |
| Testes | `unittest` / `pytest` |

---

## Arquitetura

```
┌─────────────────────────────────────────┐
│  Browser (SVG + JS)                     │
│  · Clique nas posições                  │
│  · Destaque de movimentos legais        │
└───────────────────┬─────────────────────┘
                    │ HTTP JSON
┌───────────────────▼─────────────────────┐
│  Flask (app.py)                         │
│  · GET  /              → index.html     │
│  · GET  /api/state     → estado atual   │
│  · POST /api/action    → place/move/remove │
│  · POST /api/reset     → novo jogo      │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│  NineMensMorris (game_logic.py)         │
│  · board[24], fases, moinhos, vitória   │
│  · to_dict() / from_dict() para sessão  │
└─────────────────────────────────────────┘
```

- A lógica de jogo é **independente** do Flask (facilita testes unitários).
- O frontend calcula movimentos legais de fase 2/3 a partir do estado e das adjacências; a validação final é sempre feita no backend.

---

## API HTTP

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Página principal do jogo |
| `GET` | `/api/state` | Estado completo do jogo (JSON) |
| `POST` | `/api/action` | Executa ação (`place`, `move`, `remove`) |
| `POST` | `/api/reset` | Reinicia a partida |

### Exemplo — colocar peça

```bash
curl -X POST http://127.0.0.1:5000/api/action \
  -H "Content-Type: application/json" \
  -d '{"action": "place", "pos": 0}'
```

### Exemplo — mover peça

```bash
curl -X POST http://127.0.0.1:5000/api/action \
  -H "Content-Type: application/json" \
  -d '{"action": "move", "from_pos": 0, "to_pos": 1}'
```

### Exemplo — remover peça (após moinho)

```bash
curl -X POST http://127.0.0.1:5000/api/action \
  -H "Content-Type: application/json" \
  -d '{"action": "remove", "pos": 8}'
```

Resposta típica:

```json
{
  "success": true,
  "message": "Peça colocada.",
  "game_state": {
    "board": ["P1", null, ...],
    "current_player": "P2",
    "phase": 1,
    "must_remove": false,
    "valid_placements": [1, 2, ...],
    "message": "Vez do Jogador 2 (Pretas) - Coloque uma peça.",
    ...
  }
}
```

---

## Instalação e execução

### Pré-requisitos

- Python **3.10** ou superior
- `pip` e `venv` (recomendado)

### Passos

```bash
# 1. Clonar
git clone https://github.com/Claudio-Candido/nine-mens-morris.git
cd nine-mens-morris

# 2. Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Dependências
pip install -r requirements.txt

# 4. Arrancar
python app.py
```

Abrir no browser: **http://127.0.0.1:5000**

Por omissão o servidor escuta em `0.0.0.0:5000` com `debug=True`.  
Em produção, defina `SECRET_KEY` por variável de ambiente e desative o debug.

```bash
export SECRET_KEY="sua-chave-secreta-forte"
python app.py
```

---

## Testes

Suite de testes unitários da lógica de jogo e de rotas Flask básicas:

```bash
source .venv/bin/activate
python -m pytest test_game_logic.py -v
```

Cobertura principal:

- Estado inicial
- Colocação e troca de turno
- Formação de moinho e remoção
- Proteção de peças em moinho
- Movimento e fase de voo
- Condição de vitória (< 3 peças)
- Rotas Flask (`/`, `/api/state`, `/api/action`, `/api/reset`)

---

## Estrutura do projeto

```text
nine-mens-morris/
├── app.py                 # Aplicação Flask e rotas API
├── game_logic.py          # Motor do jogo (NineMensMorris)
├── test_game_logic.py     # Testes unitários
├── requirements.txt
├── LICENSE                # MIT
├── README.md
├── .gitignore
├── static/
│   ├── css/
│   │   └── style.css      # Tema escuro, responsivo
│   └── js/
│       └── main.js        # Tabuleiro SVG, interação e API
└── templates/
    └── index.html         # Layout principal + modal de regras
```

---

## Licença

Distribuído sob a licença [MIT](LICENSE).

---

**Trilha (Nine Men's Morris)** — estratégia clássica, interface moderna, 100 % open source.
