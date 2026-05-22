#!/bin/bash
# Setup script untuk Raspberry Pi backend

echo "╔════════════════════════════════════════════╗"
echo "║   Biometric Backend Setup                  ║"
echo "║   Raspberry Pi 5                           ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3.10 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python3 << EOF
from modules.db_manager import BiometricDatabase
db = BiometricDatabase('biometrics.db')
print("✅ Database initialized!")
EOF

# Check database
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate environment: source venv/bin/activate"
echo "   2. Enroll users: python3 tools/enroll_face.py"
echo "   3. Start API: python3 api_server.py"
echo ""
