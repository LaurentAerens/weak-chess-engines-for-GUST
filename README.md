# Weak Chess Engines for GUST

[![Build and Release](https://github.com/LaurentAerens/weak-chess-engines-for-GUST/actions/workflows/build-release.yml/badge.svg)](https://github.com/LaurentAerens/weak-chess-engines-for-GUST/actions/workflows/build-release.yml)
[![Test Chess Engines](https://github.com/LaurentAerens/weak-chess-engines-for-GUST/actions/workflows/test.yml/badge.svg)](https://github.com/LaurentAerens/weak-chess-engines-for-GUST/actions/workflows/test.yml)

A collection of intentionally weak chess engines built in Python using the `python-chess` library. These engines are UCI (Universal Chess Interface) compatible and designed for testing, analysis, and educational purposes.

## 🎯 Purpose

These engines are specifically designed to play **weak chess** while maintaining UCI compatibility. They're perfect for:

- **Testing stronger engines** against predictably weak opponents
- **Educational purposes** to understand what makes chess play weak
- **Benchmarking** chess engine improvements
- **Analysis** of common chess mistakes and anti-patterns
- **Fun challenges** - can you lose to these engines?

## 🚀 Quick Start

### Option 1: Play with Built-in GUI (Recommended)
```bash
# Clone the repository
git clone https://github.com/LaurentAerens/weak-chess-engines-for-GUST.git
cd weak-chess-engines-for-GUST

# Install dependencies
pip install -r requirements.txt

# Launch the chess GUI
python main.py
```

### Option 2: Download Pre-built Executables
1. Go to the [Releases](https://github.com/LaurentAerens/weak-chess-engines-for-GUST/releases) page
2. Download the appropriate package for your platform (Windows, Linux, or macOS)
3. Extract the ZIP file
4. Load the engines in your favorite UCI-compatible chess GUI

### Option 3: Run Engines Individually
```bash
# Run an engine directly (example: Random Engine)
python scripts/random_engine.py
```

## 🎮 Features

### 🖥️ Built-in Chess GUI
- **Visual chess board** with drag-and-drop piece movement
- **Engine selection menu** with difficulty ratings and descriptions
- **Real-time game status** and move history
- **Hint system** for when you're stuck
- **New game functionality** to restart anytime
- **Cross-platform** - works on Windows, macOS, and Linux

### 🤖 Available Engines

### 1. Random Engine
- **Weakness Level**: ⭐⭐⭐⭐⭐ (Extremely Weak)
- **Strategy**: Plays completely random legal moves
- **Characteristics**: No planning, no evaluation, pure randomness
- **Good for**: Absolute baseline testing

### 2. Alphabetical Engine
- **Weakness Level**: ⭐⭐⭐⭐ (Very Weak)
- **Strategy**: Always picks the first move alphabetically by algebraic notation
- **Characteristics**: Completely predictable, sorts moves like "a4", "b3", "Bc4", etc.
- **Good for**: Learning chess notation, highly exploitable patterns

### 3. Reverse Alphabetical Engine
- **Weakness Level**: ⭐⭐⭐⭐ (Very Weak)
- **Strategy**: Always picks the last move alphabetically by algebraic notation
- **Characteristics**: Opposite of alphabetical engine, prefers moves starting with later letters
- **Good for**: Testing pattern recognition, predictable but different behavior

### 4. Blunder Engine  
- **Weakness Level**: ⭐⭐⭐⭐ (Very Weak)
- **Strategy**: Actively looks for the worst possible moves
- **Characteristics**: Evaluates positions and deliberately chooses bad moves, hangs pieces intentionally
- **Good for**: Testing against engines that make tactical blunders

### 5. Greedy Capture Engine
- **Weakness Level**: ⭐⭐⭐ (Weak)
- **Strategy**: Always captures when possible, ignoring strategy
- **Characteristics**: One-track mind focused only on capturing material
- **Good for**: Testing against materialistic but strategically blind opponents

### 6. Shuffle Engine
- **Weakness Level**: ⭐⭐⭐ (Weak)
- **Strategy**: Prefers to move pieces back and forth without purpose
- **Characteristics**: Creates shuffling patterns, wastes tempo, repeats positions
- **Good for**: Testing against time-wasting, aimless play

### 7. Anti-Positional Engine
- **Weakness Level**: ⭐⭐ (Moderately Weak)
- **Strategy**: Deliberately violates chess principles
- **Characteristics**: Avoids central control, blocks own pawns, develops pieces poorly
- **Good for**: Testing against opponents who understand tactics but ignore positional play

## 🛠️ Technical Details

### UCI Compatibility
All engines implement the Universal Chess Interface (UCI) protocol, making them compatible with popular chess GUIs such as:
- Arena Chess GUI
- ChessBase
- Scid vs. PC
- Lucas Chess
- Cute Chess
- And many others!

### Engine Architecture
```
main.py                     # GUI application for playing chess
src/
├── base_engine.py          # Base UCI engine implementation
├── engines/
│   ├── random_engine.py    # Random move engine
│   ├── blunder_engine.py   # Deliberate blunder engine
│   ├── greedy_capture_engine.py  # Capture-focused engine
│   ├── shuffle_engine.py   # Shuffling/tempo-wasting engine
│   └── anti_positional_engine.py # Anti-positional engine
scripts/                    # Entry points for each engine (UCI mode)
examples/                   # Demo scripts and testing utilities
└── build.py               # Local build script for executables
```

### Dependencies
- Python 3.8+
- `python-chess` library (handles board representation, move generation, UCI protocol)

## 🏗️ Building from Source

### Local Development
```bash
# Clone and setup
git clone https://github.com/LaurentAerens/weak-chess-engines-for-GUST.git
cd weak-chess-engines-for-GUST
pip install -r requirements.txt

# Test an engine
python scripts/random_engine.py
```

### Building Executables
```bash
# Install PyInstaller
pip install pyinstaller

# Build all engines
pyinstaller --onefile scripts/random_engine.py
pyinstaller --onefile scripts/blunder_engine.py
pyinstaller --onefile scripts/greedy_capture_engine.py
pyinstaller --onefile scripts/shuffle_engine.py
pyinstaller --onefile scripts/anti_positional_engine.py

# Executables will be in the dist/ directory
```

## 🔄 Automated Releases

This project uses GitHub Actions for automated building and releasing:

- **Continuous Integration**: Tests run on every push and pull request
- **Automated Builds**: Executables are built for Windows, Linux, and macOS
- **Automated Releases**: Create a new release by pushing a git tag

To create a new release:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 📝 Usage Examples

### Using the Built-in GUI
```bash
# Start the application
python main.py

# 1. Select an engine from the dropdown menu
# 2. Click "New Game" to start
# 3. Click on pieces to move them
# 4. Get hints if you're stuck
# 5. Try different engines for varying difficulty
```

### Using with Arena Chess GUI
1. Download and install [Arena Chess GUI](http://www.playwitharena.de/)
2. Go to `Engines` → `Install New Engine`
3. Browse to the downloaded engine executable
4. The engine will appear in your engine list
5. Start a new game and select the weak engine as your opponent

### Using with command line UCI
```bash
# Start an engine
./random_engine_windows.exe

# Send UCI commands
uci
isready
position startpos moves e2e4
go movetime 1000
quit
```

## 🧪 Testing and Validation

The project includes comprehensive testing:

```bash
# Run tests
python -m pytest tests/

# Test engine imports and basic functionality
python -c "from src.engines import *; print('All engines imported successfully!')"
```

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

- **New weak engines** with different weaknesses
- **Improved weakness algorithms** for existing engines
- **Performance optimizations**
- **Additional UCI features**
- **Documentation improvements**
- **Test coverage expansion**

### Development Setup
```bash
# Fork the repository and clone your fork
git clone https://github.com/your-username/weak-chess-engines-for-GUST.git
cd weak-chess-engines-for-GUST

# Create a new branch
git checkout -b feature/new-weak-engine

# Make your changes and test
pip install -r requirements.txt
python scripts/your_new_engine.py

# Submit a pull request
```

## 📊 Performance Characteristics

| Engine | Avg. Moves/Game | Material Loss Rate | Tactical Blunders/Game |
|--------|----------------|-------------------|----------------------|
| Random | 40-80 | Very High | 15-25 |
| Alphabetical | 35-75 | Very High | 12-22 |
| Reverse Alphabetical | 35-75 | Very High | 12-22 |
| Blunder | 30-60 | Extremely High | 20-30 |
| Greedy Capture | 50-90 | High | 10-20 |
| Shuffle | 60-120 | Medium | 5-15 |
| Anti-Positional | 70-110 | Medium | 8-18 |

*Note: These are approximate values and will vary based on the opponent's strength*

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **python-chess library** by Niklas Fiekas for excellent chess programming foundations
- **UCI protocol** creators for standardizing chess engine communication
- **Chess community** for feedback and testing

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/LaurentAerens/weak-chess-engines-for-GUST/issues)
- **Discussions**: [GitHub Discussions](https://github.com/LaurentAerens/weak-chess-engines-for-GUST/discussions)
- **Email**: laurent.aerens@example.com

---

*Remember: These engines are intentionally weak! If you're losing to them, consider it a learning opportunity! 😄*