#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# INSTALADOR AUTOMÁTICO FREQTRADE PARA TERMUX (Android)
# ============================================================
# Estrategia: v4 SMA Crossover (la ganadora del backtest)
# Exchange: Hyperliquid (compatible Cuba)
# Mobile-first: control vía Telegram + FreqDroid
# ============================================================
#
# CÓMO USAR:
# 1. Instala Termux desde F-Droid (NO Google Play, esa está desactualizada)
#    URL: https://f-droid.org/packages/com.termux/
#
# 2. Abre Termux y ejecuta:
#    pkg update && pkg upgrade -y
#    pkg install git python nano curl -y
#
# 3. Copia este script a Termux:
#    (puedes usar: curl -O https://tu-url/script.sh)
#    O copiarlo manualmente
#
# 4. Dale permisos de ejecución:
#    chmod +x install_freqtrade_termux.sh
#
# 5. Ejecútalo:
#    ./install_freqtrade_termux.sh
#
# ============================================================

set -e  # salir si hay error

echo "🚀 ====================================================== 🚀"
echo "🚀 INSTALANDO FREQTRADE EN TERMUX"
echo "🚀 Estrategia: v4 SMA Crossover (Hyperliquid)        "
echo "🚀 ====================================================== 🚀"
echo ""

# Step 1: Actualizar Termux
echo "📦 [1/8] Actualizando Termux..."
pkg update -y && pkg upgrade -y

# Step 2: Instalar dependencias del sistema
echo "📦 [2/8] Instalando dependencias del sistema..."
pkg install -y python python-pip git nano curl wget openssh ca-certificates

# Step 3: Configurar storage (acceso a archivos del móvil)
echo "📱 [3/8] Configurando acceso a storage..."
yes | termux-setup-storage 2>/dev/null || echo "  (storage ya configurado)"

# Step 4: Crear directorio de trabajo
echo "📁 [4/8] Creando directorio de trabajo..."
mkdir -p ~/freqtrade_bot
cd ~/freqtrade_bot

# Step 5: Clonar Freqtrade
echo "📥 [5/8] Clonando Freqtrade desde GitHub..."
if [ -d "freqtrade" ]; then
    echo "  Freqtrade ya existe, actualizando..."
    cd freqtrade
    git pull
    cd ..
else
    git clone https://github.com/freqtrade/freqtrade.git
fi

# Step 6: Crear entorno virtual Python
echo "🐍 [6/8] Creando entorno virtual Python..."
cd freqtrade
python -m venv .venv
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip wheel setuptools

# Step 7: Instalar dependencias de Freqtrade
echo "📚 [7/8] Instalando dependencias de Freqtrade (puede tomar 10-15 min)..."
pip install -e .

# Verificar instalación
echo "✅ Verificando instalación..."
freqtrade --version

# Step 8: Crear estructura user_data
echo "📁 [8/8] Creando estructura user_data..."
freqtrade create-userdir --userdir user_data

echo ""
echo "✅ ====================================================== ✅"
echo "✅ FREQTRADE INSTALADO CORRECTAMENTE"
echo "✅ ====================================================== ✅"
echo ""
echo "📁 Ubicación: ~/freqtrade_bot/freqtrade"
echo "🐍 Venv: ~/freqtrade_bot/freqtrade/.venv"
echo ""
echo "PRÓXIMOS PASOS:"
echo ""
echo "1. Copia los archivos de configuración a ~/freqtrade_bot/freqtrade/user_data/:"
echo "   - config_hl.json (configuración principal)"
echo "   - strategies/SmaCrossoverV4.py (estrategia)"
echo ""
echo "2. Edita config_hl.json con tus API keys:"
echo "   nano ~/freqtrade_bot/freqtrade/user_data/config_hl.json"
echo ""
echo "3. Test de la estrategia (dry-run):"
echo "   cd ~/freqtrade_bot/freqtrade"
echo "   source .venv/bin/activate"
echo "   freqtrade trade --config user_data/config_hl.json --strategy SmaCrossoverV4 --dry-run"
echo ""
echo "4. Para trading LIVE (después de validar en dry-run):"
echo "   freqtrade trade --config user_data/config_hl.json --strategy SmaCrossoverV4"
echo ""
echo "📚 Documentación: https://www.freqtrade.io/"
echo ""
