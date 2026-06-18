# 🤖 Crypto Bot Cuba

> Bot de trading cripto **open source** diseñado para funcionar desde **Cuba** (y cualquier país con restricciones)
> Funciona en **Hyperliquid** (DEX non-custodial, sin KYC, sin IP block)
> Controlado desde **Android** vía Termux + Telegram + FreqDroid

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Freqtrade](https://img.shields.io/badge/Freqtrade-compatible-green.svg)](https://www.freqtrade.io/)
[![Hyperliquid](https://img.shields.io/badge/Exchange-Hyperliquid-blue.svg)](https://hyperliquid.xyz/)

---

## 🇨🇺 ¿Por qué este bot existe?

Los cubanos no pueden usar Binance, Bybit, KuCoin ni la mayoría de exchanges centralizados (lista negra OFAC). Las soluciones tradicionales no funcionan.

Este bot soluciona eso:
- ✅ **Funciona en Cuba** (Hyperliquid es DEX on-chain, no puede bloquear países)
- ✅ **Sin KYC** (no hay documento que filtrar)
- ✅ **Non-custodial** (nadie puede confiscar tus fondos)
- ✅ **Mobile-first** (controlado desde Android)
- ✅ **100% Open source** (código auditable)

---

## 📊 Estrategias incluidas

| Estrategia | Sharpe Ratio | Capital Min | Difficulty | Origen |
|------------|--------------|-------------|------------|--------|
| **Time Series Momentum** | 1.28–2.21 | $30+ | Media | Paper académico Moskowitz 2012 |
| **Funding Rate Arbitrage** | 2.0 | $100+ | Alta | Paper arXiv "Fundamentals of Perpetual Futures" |
| **SMA Crossover v4** (bonus) | 0.36 | $30+ | Baja | Backtest propio (PF 1.85, win rate 60%) |

📚 Documentación detallada de cada estrategia en [`docs/`](docs/).

---

## 🏗️ Arquitectura

```
┌────────────────────────────────────────────────┐
│  TU ANDROID                                     │
│  ├─ Termux (corre Freqtrade 24/7)              │
│  ├─ Trust Wallet (custodia tus fondos)         │
│  ├─ Telegram (alertas en tiempo real)          │
│  └─ FreqDroid (app control bot)                │
└────────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────────┐
│  HYPERLIQUID L1 (DEX non-custodial)            │
│  ├─ Tu wallet con USDC                          │
│  ├─ Positions BTC/ETH/SOL (leverage 3-5x)     │
│  └─ On-chain, sin KYC, sin IP block            │
└────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Requisitos
- Android 7+ con conexión internet
- $30-100 USD para empezar
- 1-2 horas para setup inicial

### Instalación (resumen)

1. **Instalar Termux** (desde F-Droid, NO Play Store)
2. **Instalar Freqtrade**:
   ```bash
   pkg update && pkg install git python -y
   git clone https://github.com/freqtrade/freqtrade.git
   cd freqtrade && python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
3. **Crear Trust Wallet** + comprar USDC + bridge a Hyperliquid
4. **Configurar Telegram bot** con BotFather
5. **Copiar estrategias y configs** a `user_data/`
6. **Paper trading 7 días** (obligatorio)
7. **Live trading** empezando con $10

📚 Guía completa paso a paso: [`docs/GUIA_GENERAL.md`](docs/GUIA_GENERAL.md)

---

## 📁 Estructura del repositorio

```
crypto-bot-cuba/
├── strategies/                          # Estrategias Freqtrade
│   ├── TimeSeriesMomentum.py           # ⭐ Recomendada para $30
│   ├── FundingRateArbitrage.py         # Para $100+ (adaptación Freqtrade)
│   └── SmaCrossoverV4.py               # Backup (backtest propio)
├── configs/                             # Configuraciones
│   ├── config_tsm.json                 # Config para TSM
│   └── config_funding_arb.json         # Config para Funding Arb
├── scripts/                             # Scripts utilitarios
│   ├── funding_arbitrage_puro.py       # ⭐ Funding Arb REAL (delta-neutral)
│   ├── install_freqtrade_termux.sh     # Instalador automático Termux
│   └── .env.example                    # Template variables entorno
├── docs/                                # Documentación
│   ├── GUIA_GENERAL.md                 # ⭐ Empezar aquí
│   ├── GUIA_TIME_SERIES_MOMENTUM.md    # Guía estrategia TSM
│   └── GUIA_FUNDING_RATE_ARBITRAGE.md  # Guía estrategia Funding Arb
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚙️ Configuración rápida

### 1. Variables de entorno (`.env`)
```bash
HYPERLIQUID_API_KEY=tu_api_wallet_address
HYPERLIQUID_API_SECRET=tu_api_wallet_private_key
HYPERLIQUID_WALLET_ADDRESS=tu_wallet_principal
TELEGRAM_BOT_TOKEN=tu_telegram_bot_token
TELEGRAM_CHAT_ID=tu_chat_id_numerico
```

### 2. Comando para paper trading
```bash
freqtrade trade \
  --config user_data/config_tsm.json \
  --strategy TimeSeriesMomentum \
  --dry-run
```

### 3. Comando para live trading
```bash
freqtrade trade \
  --config user_data/config_tsm.json \
  --strategy TimeSeriesMomentum
```

---

## 🇨🇺 Cómo obtener USDC desde Cuba

Opciones verificadas que funcionan en Cuba:
- **QbitPay** (https://qbitpay.com) — acepta MLC
- **QvaPay** (https://qvapay.com) — Cuba-specific
- **BitPapa** (https://bitpapa.com) — P2P global
- **Paxful** (https://paxful.com) — P2P global

📚 Detalles en [`docs/GUIA_GENERAL.md`](docs/GUIA_GENERAL.md).

---

## 📈 Expectativas realistas

| Escenario | Con $30 | Con $100 | Con $500+ |
|-----------|---------|----------|-----------|
| Sharpe esperado | 0.5-1.0 | 1.0-1.5 | 1.5-2.0 |
| CAGR anual | 10-25% | 20-40% | 30-50% |
| Max drawdown | 15-25% | 10-20% | 10-15% |
| P&L absoluto anual | $3-8 | $20-40 | $150-250 |
| Recomendación | TSM | TSM + Funding Arb | Ambas + diversificar |

⚠️ **No es dinero fácil**: trading con leverage puede liquidar tu cuenta. Solo invierte lo que puedas perder.

---

## 🛡️ Características de seguridad

- ✅ **Non-custodial**: tus fondos están en TU wallet, no en un exchange
- ✅ **Sin KYC**: no hay datos personales que filtrar
- ✅ **Open source**: código auditable
- ✅ **Insurance fund Hyperliquid**: ~$50M para compensar hacks
- ✅ **Stop loss obligatorio**: cada trade tiene protección
- ✅ **Daily loss limit**: bot se apaga si pierdes >30% en 1 día
- ✅ **Trailing stops**: protege ganancias automáticamente

---

## ⚠️ Riesgos importantes

1. **Leverage 5x**: BTC puede caer 20% en 1 día = 100% pérdida del margin
2. **Hyperliquid smart contract risk**: bug en código puede comprometer fondos
3. **Batería móvil**: Termux consume ~5-10%/hora, necesitas cargador siempre
4. **Conexión internet**: si pierdes internet, bot no puede cerrar posiciones
5. **Pérdida de seed phrase**: si pierdes 12 palabras de Trust Wallet, pierdes TODO
6. **Past performance ≠ future**: estrategias pueden dejar de funcionar

---

## 🆘 Soporte y comunidad

- 📖 **Documentación**: [`docs/`](docs/)
- 🐛 **Issues**: abre un issue en GitHub
- 💬 **Telegram Freqtrade community**: https://t.me/freqtrade_public
- 📚 **Freqtrade docs**: https://www.freqtrade.io/
- 📚 **Hyperliquid docs**: https://hyperliquid.gitbook.io/

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/mejora`
3. Commit tus cambios: `git commit -m 'Agrega mejora'`
4. Push a la rama: `git push origin feature/mejora`
5. Abre un Pull Request

Áreas donde se necesita ayuda:
- 🌐 Traducciones (inglés, portugués)
- 📊 Nuevas estrategias verificadas académicamente
- 🐛 Bug fixes y mejoras de performance
- 📚 Mejoras en documentación
- 🇨🇺 Testing en condiciones reales de Cuba

---

## 📜 License

MIT License — ver [LICENSE](LICENSE).

Puedes usar, modificar y distribuir libremente. Si mejoras el código, se agradecen PRs pero no es obligatorio.

---

## ⚖️ Disclaimer

**Este software es para fines educativos e informativos únicamente.**

- ❌ NO es asesoría financiera
- ❌ NO garantiza returns
- ❌ NO es adecuado para todos los inversores
- ✅ Trading con leverage implica riesgo de pérdida TOTAL del capital
- ✅ Solo invierte lo que puedas permitirte perder
- ✅ Valida todo en paper trading antes de ir live
- ✅ Performance pasada no garantiza performance futura

Los autores no se responsabilizan por pérdidas financieras derivadas del uso de este software.

---

## 🙏 Agradecimientos

- **Freqtrade team** — por el excelente bot open source
- **Hyperliquid team** — por el DEX non-custodial más rápido
- **Moskowitz, Ooi, Pedersen** — por la investigación académica sobre momentum
- **Comunidad crypto Cuba** — por inspirar este proyecto

---

## ⭐ Si te sirve, dale una estrella

Ayuda a otros cubanos (y personas de países con restricciones similares) a encontrar este proyecto.
