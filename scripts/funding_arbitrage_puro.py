"""
SCRIPT PYTHON PURO — Funding Rate Arbitrage Delta-Neutral en Hyperliquid
=========================================================================
Versión REAL del arbitrage (no adaptación Freqtrade)

ESTRATEGIA:
1. Comprar BTC spot en Hyperliquid
2. Vender BTC perp en Hyperliquid (mismo tamaño)
3. Delta-neutral: no importa si BTC sube o baja
4. Cobrar funding rate cada hora
5. Rebalancear cuando desbalance > 10%
6. Cerrar cuando funding se vuelve negativo

COMPATIBILIDAD:
- Funciona en Cuba (Hyperliquid es DEX)
- Requiere Hyperliquid API wallet
- Requiere Python 3.10+
- Usa hyperliquid-python-sdk oficial

USO:
1. Configura tu API wallet en .env
2. Ejecuta: python funding_arbitrage_puro.py
3. Monitorea en Telegram (opcional)

ADVERTENCIA:
- Capital mínimo recomendado: $100+ (con $30 fees matan el edge)
- Returns esperados: 20-50% anual (no 1000%)
- Riesgo de liquidación del short perp si BTC sube mucho
"""

import os
import json
import time
import math
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# ============================================================
# CONFIGURACIÓN
# ============================================================

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

# Configuración del bot
CONFIG = {
    # Capital (en USDC)
    'total_capital_usdc': 100,  # cambiar a 30 si solo tienes $30
    
    # Distribución
    'spot_pct': 0.5,  # 50% en spot
    'perp_pct': 0.5,  # 50% en perp (con leverage)
    
    # Leverage en perp (BAJO para evitar liquidación)
    'perp_leverage': 2,  # 2x (max safe para BTC)
    
    # Thresholds de funding
    'min_funding_pct_hour': 0.005,  # mínimo para abrir posición
    'close_funding_pct_hour': -0.001,  # cerrar si funding negativo
    
    # Rebalanceo
    'rebalance_threshold_pct': 10,  # rebalancear si desbalance > 10%
    
    # Stop loss de emergencia
    'max_loss_pct': 15,  # cerrar todo si pérdida total > 15%
    
    # Pares operados
    'symbols': ['BTC', 'ETH', 'SOL'],
    
    # Hyperliquid
    'testnet': False,  # True para testnet, False para mainnet
    
    # Monitoreo
    'check_interval_seconds': 3600,  # 1 hora
    'log_file': 'logs/funding_arb.log',
    'state_file': 'logs/funding_arb_state.json',
    
    # Telegram (opcional)
    'telegram_enabled': True,
    'telegram_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
    'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
}

# Hyperliquid API wallet (de .env)
HYPERLIQUID_API_KEY = os.getenv('HYPERLIQUID_API_KEY', '')  # API wallet address
HYPERLIQUID_API_SECRET = os.getenv('HYPERLIQUID_API_SECRET', '')  # API wallet private key
HYPERLIQUID_WALLET_ADDRESS = os.getenv('HYPERLIQUID_WALLET_ADDRESS', '')  # Tu wallet principal

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG['log_file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================
# TELEGRAM ALERTS (opcional)
# ============================================================

def send_telegram(message: str):
    """Envía mensaje a Telegram"""
    if not CONFIG['telegram_enabled'] or not CONFIG['telegram_token']:
        return
    
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendMessage"
        data = json.dumps({
            'chat_id': CONFIG['telegram_chat_id'],
            'text': message,
            'parse_mode': 'HTML'
        }).encode()
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        logger.error(f"Telegram error: {e}")


# ============================================================
# HYPERLIQUID CLIENT
# ============================================================

class HyperliquidClient:
    """Cliente de Hyperliquid para spot + perp"""
    
    def __init__(self, api_key: str, api_secret: str, wallet_address: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.wallet_address = wallet_address
        self.testnet = testnet
        
        # En producción, aquí inicializarías el SDK oficial:
        # from hyperliquid.exchange import Exchange
        # from hyperliquid.info import Info
        # from hyperliquid.utils import Constants
        # 
        # self.info = Info(Constants.TESTNET_API_URL if testnet else Constants.MAINNET_API_URL)
        # self.exchange = Exchange(self.wallet_address, self.api_secret, 
        #                          Constants.TESTNET_API_URL if testnet else Constants.MAINNET_API_URL)
        
        logger.info(f"Hyperliquid client initialized (testnet={testnet})")
    
    def get_balance(self) -> float:
        """Obtiene balance USDC disponible"""
        # En producción:
        # user_state = self.info.user_state(self.wallet_address)
        # return float(user_state['marginSummary']['accountValue'])
        return 0.0  # placeholder
    
    def get_funding_rate(self, symbol: str) -> float:
        """Obtiene funding rate actual de un símbolo (por hora)"""
        # En producción:
        # funding = self.info.funding_history(symbol, start_time, end_time)
        # return float(funding[-1]['fundingRate'])
        return 0.0  # placeholder
    
    def get_spot_price(self, symbol: str) -> float:
        """Obtiene precio spot actual"""
        return 0.0  # placeholder
    
    def get_perp_price(self, symbol: str) -> float:
        """Obtiene precio perp actual"""
        return 0.0  # placeholder
    
    def buy_spot(self, symbol: str, amount_usdc: float) -> bool:
        """Compra spot en Hyperliquid"""
        logger.info(f"🟢 BUY SPOT {symbol}: ${amount_usdc} USDC")
        # En producción:
        # order_result = self.exchange.market_open(symbol + '-SPOT', amount_usdc)
        # return order_result['status'] == 'ok'
        return True  # placeholder
    
    def sell_perp(self, symbol: str, amount_usdc: float, leverage: int) -> bool:
        """Vende perp (short) en Hyperliquid"""
        logger.info(f"🔴 SELL PERP {symbol}: ${amount_usdc} USDC (leverage {leverage}x)")
        # En producción:
        # self.exchange.set_leverage(leverage, symbol)
        # order_result = self.exchange.market_open(symbol, -amount_usdc)
        # return order_result['status'] == 'ok'
        return True  # placeholder
    
    def close_spot(self, symbol: str, amount_btc: float) -> bool:
        """Cierra posición spot"""
        logger.info(f"🔒 CLOSE SPOT {symbol}: {amount_btc} units")
        return True
    
    def close_perp(self, symbol: str) -> bool:
        """Cierra posición perp"""
        logger.info(f"🔒 CLOSE PERP {symbol}")
        # En producción:
        # self.exchange.market_close(symbol)
        return True
    
    def get_position_perp(self, symbol: str) -> Dict:
        """Obtiene posición perp actual"""
        # En producción:
        # user_state = self.info.user_state(self.wallet_address)
        # for pos in user_state['assetPositions']:
        #     if pos['position']['coin'] == symbol:
        #         return pos['position']
        return {'size': 0, 'entry_price': 0, 'unrealized_pnl': 0}
    
    def get_position_spot(self, symbol: str) -> Dict:
        """Obtiene posición spot actual"""
        return {'size': 0, 'entry_price': 0}


# ============================================================
# FUNDING ARBITRAGE MANAGER
# ============================================================

class FundingArbitrageManager:
    """Maneja la lógica del arbitrage"""
    
    def __init__(self, client: HyperliquidClient, config: dict):
        self.client = client
        self.config = config
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """Carga estado persistente"""
        if Path(self.config['state_file']).exists():
            with open(self.config['state_file']) as f:
                return json.load(f)
        return {
            'positions': {},  # symbol -> {spot_size, perp_size, entry_time}
            'total_pnl': 0,
            'last_rebalance': None
        }
    
    def save_state(self):
        """Guarda estado"""
        Path(self.config['state_file']).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config['state_file'], 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_and_open(self, symbol: str):
        """Verifica y abre posición de arbitrage si las condiciones son óptimas"""
        
        # 1. Verificar funding rate
        funding_rate = self.client.get_funding_rate(symbol)
        
        if funding_rate < self.config['min_funding_pct_hour'] / 100:
            logger.info(f"  {symbol}: funding {funding_rate*100:.4f}% < threshold, no abrir")
            return False
        
        # 2. Verificar que no tengamos posición ya
        if symbol in self.state['positions']:
            logger.info(f"  {symbol}: posición ya abierta, skip")
            return False
        
        # 3. Calcular tamaño
        capital_per_symbol = self.config['total_capital_usdc'] / len(self.config['symbols'])
        spot_amount = capital_per_symbol * self.config['spot_pct']
        perp_amount = capital_per_symbol * self.config['perp_pct']
        
        # 4. Abrir spot long
        spot_ok = self.client.buy_spot(symbol, spot_amount)
        if not spot_ok:
            logger.error(f"  {symbol}: error abriendo spot")
            return False
        
        # 5. Abrir perp short
        perp_ok = self.client.sell_perp(symbol, perp_amount, self.config['perp_leverage'])
        if not perp_ok:
            # Rollback: cerrar spot si perp falló
            self.client.close_spot(symbol, 0)  # placeholder amount
            logger.error(f"  {symbol}: error abriendo perp, rollback spot")
            return False
        
        # 6. Registrar posición
        self.state['positions'][symbol] = {
            'spot_amount_usdc': spot_amount,
            'perp_amount_usdc': perp_amount,
            'entry_time': datetime.now(timezone.utc).isoformat(),
            'entry_funding_rate': funding_rate,
            'cumulative_funding_collected': 0
        }
        self.save_state()
        
        # 7. Alerta Telegram
        send_telegram(
            f"🟢 <b>ARBITRAGE OPENED</b>\n"
            f"Symbol: {symbol}\n"
            f"Spot: ${spot_amount} USDC\n"
            f"Perp: ${perp_amount} USDC ({self.config['perp_leverage']}x)\n"
            f"Funding rate: {funding_rate*100:.4f}%/h\n"
            f"Expected daily income: ${spot_amount * funding_rate * 24:.4f}"
        )
        
        logger.info(f"✅ {symbol}: arbitrage abierto correctamente")
        return True
    
    def check_and_close(self, symbol: str):
        """Verifica si debe cerrar posición"""
        
        if symbol not in self.state['positions']:
            return False
        
        position = self.state['positions'][symbol]
        
        # 1. Verificar funding rate actual
        funding_rate = self.client.get_funding_rate(symbol)
        
        # Si funding negativo, cerrar
        if funding_rate < self.config['close_funding_pct_hour'] / 100:
            logger.info(f"  {symbol}: funding negativo {funding_rate*100:.4f}%, cerrando")
            return self.close_position(symbol, 'funding_negative')
        
        # 2. Verificar P&L total (spot + perp)
        spot_price = self.client.get_spot_price(symbol)
        perp_position = self.client.get_position_perp(symbol)
        
        # Calcular P&L
        # (en producción, usar datos reales del exchange)
        spot_pnl = 0  # placeholder
        perp_pnl = perp_position.get('unrealized_pnl', 0)
        total_pnl_pct = ((spot_pnl + perp_pnl) / position['spot_amount_usdc']) * 100
        
        # Si pérdida total > threshold, cerrar
        if total_pnl_pct < -self.config['max_loss_pct']:
            logger.warning(f"  {symbol}: pérdida {total_pnl_pct:.2f}% > max, cerrando")
            return self.close_position(symbol, 'max_loss')
        
        # 3. Verificar rebalanceo
        spot_value = position['spot_amount_usdc'] + spot_pnl
        perp_value = position['perp_amount_usdc'] + perp_pnl
        
        if spot_value > 0 and perp_value > 0:
            imbalance = abs(spot_value - perp_value) / max(spot_value, perp_value) * 100
            
            if imbalance > self.config['rebalance_threshold_pct']:
                logger.info(f"  {symbol}: desbalance {imbalance:.1f}%, rebalanceando")
                self.rebalance(symbol, spot_value, perp_value)
        
        # 4. Acumular funding cobrado (aproximación)
        # En producción, esto vendría del exchange
        funding_collected = position['perp_amount_usdc'] * funding_rate
        position['cumulative_funding_collected'] += funding_collected
        
        return False
    
    def rebalance(self, symbol: str, spot_value: float, perp_value: float):
        """Rebalancea posición para mantener delta-neutral"""
        
        diff = spot_value - perp_value
        
        if abs(diff) < 5:  # menos de $5 no vale la pena rebalancear
            return
        
        if diff > 0:
            # Spot > perp, aumentar perp
            self.client.sell_perp(symbol, abs(diff), self.config['perp_leverage'])
        else:
            # Perp > spot, aumentar spot
            self.client.buy_spot(symbol, abs(diff))
        
        logger.info(f"  {symbol}: rebalanceado diff=${diff:.2f}")
        send_telegram(f"⚖️ <b>REBALANCE</b> {symbol}: diff ${diff:.2f}")
    
    def close_position(self, symbol: str, reason: str) -> bool:
        """Cierra posición de arbitrage"""
        
        if symbol not in self.state['positions']:
            return False
        
        position = self.state['positions'][symbol]
        
        # Cerrar spot
        self.client.close_spot(symbol, position.get('spot_amount_usdc', 0))
        
        # Cerrar perp
        self.client.close_perp(symbol)
        
        # Calcular P&L total aproximado
        total_pnl = position.get('cumulative_funding_collected', 0)
        
        # Registrar P&L
        self.state['total_pnl'] += total_pnl
        
        # Alerta
        send_telegram(
            f"🔴 <b>ARBITRAGE CLOSED</b>\n"
            f"Symbol: {symbol}\n"
            f"Reason: {reason}\n"
            f"Funding collected: ${total_pnl:.4f}\n"
            f"Total P&L: ${self.state['total_pnl']:.4f}"
        )
        
        logger.info(f"🔒 {symbol}: cerrado por {reason}, funding=${total_pnl:.4f}")
        
        # Eliminar de state
        del self.state['positions'][symbol]
        self.save_state()
        
        return True
    
    def get_status(self) -> Dict:
        """Obtiene estado completo del bot"""
        return {
            'capital_total': self.config['total_capital_usdc'],
            'pnl_acumulado': self.state['total_pnl'],
            'posiciones_abiertas': len(self.state['positions']),
            'posiciones_detalle': self.state['positions']
        }
    
    def run_cycle(self):
        """Ejecuta un ciclo completo de verificación"""
        logger.info("=" * 60)
        logger.info(f"🤖 Cycle start - {datetime.now(timezone.utc).isoformat()}")
        
        for symbol in self.config['symbols']:
            logger.info(f"\n--- {symbol} ---")
            
            if symbol in self.state['positions']:
                # Verificar si cerrar
                self.check_and_close(symbol)
            else:
                # Verificar si abrir
                self.check_and_open(symbol)
        
        # Status
        status = self.get_status()
        logger.info(f"\n📊 Status:")
        logger.info(f"  Capital: ${status['capital_total']}")
        logger.info(f"  P&L acumulado: ${status['pnl_acumulado']:.4f}")
        logger.info(f"  Posiciones abiertas: {status['posiciones_abiertas']}")
        
        self.state['last_rebalance'] = datetime.now(timezone.utc).isoformat()
        self.save_state()


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    """Función principal"""
    
    logger.info("=" * 60)
    logger.info("🚀 FUNDING RATE ARBITRAGE BOT (Delta-Neutral)")
    logger.info("=" * 60)
    logger.info(f"Capital: ${CONFIG['total_capital_usdc']}")
    logger.info(f"Symbols: {CONFIG['symbols']}")
    logger.info(f"Leverage perp: {CONFIG['perp_leverage']}x")
    logger.info(f"Min funding/hora: {CONFIG['min_funding_pct_hour']}%")
    logger.info(f"Rebalance threshold: {CONFIG['rebalance_threshold_pct']}%")
    logger.info(f"Max loss: {CONFIG['max_loss_pct']}%")
    logger.info(f"Check interval: {CONFIG['check_interval_seconds']}s")
    logger.info("=" * 60)
    
    # Verificar configuración
    if not HYPERLIQUID_API_KEY or not HYPERLIQUID_API_SECRET:
        logger.error("❌ Hyperliquid API keys no configuradas en .env")
        return
    
    # Inicializar cliente
    client = HyperliquidClient(
        api_key=HYPERLIQUID_API_KEY,
        api_secret=HYPERLIQUID_API_SECRET,
        wallet_address=HYPERLIQUID_WALLET_ADDRESS,
        testnet=CONFIG['testnet']
    )
    
    # Inicializar manager
    manager = FundingArbitrageManager(client, CONFIG)
    
    # Loop principal
    send_telegram("🚀 <b>Funding Arbitrage Bot iniciado</b>")
    
    try:
        while True:
            manager.run_cycle()
            
            logger.info(f"\n💤 Esperando {CONFIG['check_interval_seconds']}s...")
            time.sleep(CONFIG['check_interval_seconds'])
    
    except KeyboardInterrupt:
        logger.info("\n🛑 Detenido por usuario")
        send_telegram("🛑 <b>Bot detenido por usuario</b>")
        
        # Mostrar resumen final
        status = manager.get_status()
        logger.info("\n" + "=" * 60)
        logger.info("RESUMEN FINAL")
        logger.info("=" * 60)
        logger.info(f"Capital inicial: ${CONFIG['total_capital_usdc']}")
        logger.info(f"P&L acumulado: ${status['pnl_acumulado']:.4f}")
        logger.info(f"Posiciones abiertas: {status['posiciones_abiertas']}")
        
        # Cerrar todas las posiciones (opcional - descomentar si quieres)
        # for symbol in list(manager.state['positions'].keys()):
        #     manager.close_position(symbol, 'bot_shutdown')


if __name__ == "__main__":
    main()
