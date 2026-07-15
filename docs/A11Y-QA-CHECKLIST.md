# QA A11y — VoiceOver / NVDA (NM-17)

Epic: [NM-10](https://mlcreativehub.atlassian.net/browse/NM-10) · Task: [NM-17](https://mlcreativehub.atlassian.net/browse/NM-17)

## Escopo das jornadas

| # | Jornada | Páginas | Critério de passa |
|---|---------|---------|-------------------|
| 1 | Home | `index.html` | Skip link → `#conteudo`; landmarks; ticker pausável; H1 de página |
| 2 | Artigo | `single-news-1.html` … `3` | Um H1 = manchete; comentários com labels; focus visível |
| 3 | Busca | header search (qualquer home) | Input/botão nomeados; expand/collapse anunciado |
| 4 | Contato | `contact.html` | Labels de formulário; envio via teclado |

## Checklist automatizado (CI / local)

Rodar a partir da raiz do template:

```bash
python3 scripts/a11y_qa_audit.py
```

O script falha (exit ≠ 0) se qualquer critério estrutural das 4 jornadas falhar.

## Checklist manual VoiceOver (macOS / iOS) e NVDA (Windows)

Marque após validar com leitor de tela + teclado apenas:

### Home
- [ ] `Tab` revela “Ir para o conteúdo” e salta o header
- [ ] Rotor/landmarks listam `main`, nav “Menu principal”, complementary
- [ ] Botão “Pausar destaques” funciona e anuncia estado
- [ ] Setas do carrossel (Owl), se presentes, têm nome

### Artigo
- [ ] Título da notícia é o único H1
- [ ] Breadcrumb anuncia página atual
- [ ] Campos de comentário têm nome acessível
- [ ] Links sociais anunciam a rede (não só “link”)

### Busca
- [ ] Botão “Abrir busca” / “Fechar busca”
- [ ] Campo “Buscar no site” utilizável com SR

### Contato
- [ ] Nome, e-mail e mensagem têm label/aria-label
- [ ] Ordem de foco lógica no formulário

### CMP
- [ ] Dialog de cookies prende o foco (Tab cicla no modal)
- [ ] Fechar restaura o foco no gatilho

## Barreiras restantes (candidatas a backlog)

| Item | Severidade | Notas |
|------|------------|-------|
| `gallery-style1.html` / `gallery-style2.html` / `single-news-4.html` no upstream são páginas “not found” (Yoast) | Média | Substituídas no WIP Notícias Mobile (`backup/wip-noticias-mobile-2026-07-15`) |
| Textos de demo ainda em inglês em vários cards | Baixa | Conteúdo editorial, fora do escopo a11y estrutural |
| Validação humana VoiceOver/NVDA em dispositivo real | — | Preencher caixas acima antes de fechar o Epic NM-10 |

## Resultado desta entrega

- Auditoria estrutural automatizada: ver resultado do `a11y_qa_audit.py` no PR.
- Canal de feedback: `contact.html` + declaração em `acessibilidade.html`.
- **Epic NM-10** só deve ir para Feito após as 4 jornadas manuais acima estarem marcadas.
