# Adding a New Chess Engine

This guide explains all the places you need to update when adding a new chess engine to the project.

## Step-by-Step Checklist

### 1. Create the Engine Class
**Location**: `src/engines/your_engine_name.py`

Create a new Python file in the `src/engines/` directory that implements your engine logic.

**Requirements**:
- Import necessary dependencies (chess, base_engine)
- Inherit from `BaseUCIEngine`
- Implement the `get_best_move()` method
- Include the UCI entry point at the bottom

**Template**:
```python
"""
Your Engine Name - Brief description of strategy
"""

import time
from typing import Optional
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine


class YourEngineClass(BaseUCIEngine):
    """Engine that does something specific."""
    
    def __init__(self):
        super().__init__("Your Engine Name", "Your Name")
    
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """Implement your move selection logic here."""
        # Simulate some thinking time
        time.sleep(min(think_time, 0.2))
        
        if self.stop_thinking:
            return None
            
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        # YOUR LOGIC HERE
        # Return a chess.Move object
        
        return selected_move


if __name__ == "__main__":
    run_engine(YourEngineClass)
```

### 2. Create the UCI Script Entry Point
**Location**: `scripts/your_engine_name.py`

Create a launcher script that allows the engine to be run as a standalone UCI executable.

**Template**:
```python
#!/usr/bin/env python3
"""
Entry point for Your Engine Name
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from engines.your_engine_name import YourEngineClass, run_engine

if __name__ == "__main__":
    run_engine(YourEngineClass)
```

### 3. Update the GUI (main.py)
**Location**: `main.py`

**Changes needed**:

#### 3.1. Add Import Statement (around line 20-30)
```python
from engines.your_engine_name import YourEngineClass
```

#### 3.2. Add to EngineSelector Dictionary (around line 195-205)
```python
self.engines = {
    "Random Engine (⭐⭐⭐⭐⭐)": RandomEngine,
    # ... existing engines ...
    "Your Engine Name (⭐⭐⭐)": YourEngineClass,  # Add your engine here with rating
}
```

#### 3.3. Add Engine Description (around line 245-330)
```python
info_texts = {
    # ... existing descriptions ...
    "Your Engine Name (⭐⭐⭐)": 
        "Brief headline!\n\n"
        "• Bullet point about strategy\n"
        "• Bullet point about behavior\n"
        "• Bullet point about characteristics\n"
        "• What it's good for testing\n"
        "• Additional notes",
}
```

### 4. Update Tournament Script (tournament.py)
**Location**: `tournament.py`

**Changes needed**:

#### 4.1. Add Import Statement (around line 10-19)
```python
from src.engines.your_engine_name import YourEngineClass
```

#### 4.2. Add to ENGINES List (around line 21-32)
```python
ENGINES = [
    ("Random", RandomEngine),
    # ... existing engines ...
    ("Your Engine Name", YourEngineClass),  # Add your engine here
]
```

### 5. Update Build Script (build.py)
**Location**: `build.py`

**Changes needed**:

Add your engine to the `engines` list (around line 36-45):
```python
engines = [
    ("scripts/random_engine.py", "random_engine"),
    # ... existing engines ...
    ("scripts/your_engine_name.py", "your_engine_name"),  # Add here
]
```

### 6. Update GitHub Actions Workflow
**Location**: `.github/workflows/build-release.yml`

**Changes needed**:

#### 6.1. Add Build Command (around line 44-54)
```yaml
- name: Build executables
  run: |
    # ... existing builds ...
    pyinstaller --onefile --name your_engine_name_${{ matrix.os }} scripts/your_engine_name.py
```

#### 6.2. Add Windows Artifact (around line 61-71)
```yaml
- name: Prepare artifacts (Windows)
  if: matrix.os == 'windows-latest'
  run: |
    # ... existing copies ...
    copy "dist\your_engine_name_${{ matrix.os }}.exe" "release\your_engine_name_windows.exe"
```

#### 6.3. Add Linux Artifact (around line 79-89)
```yaml
- name: Prepare artifacts (Linux)
  if: matrix.os == 'ubuntu-latest'
  run: |
    # ... existing copies ...
    cp "dist/your_engine_name_${{ matrix.os }}" "release/your_engine_name_linux"
```

#### 6.4. Update Release Description (around line 186-193)
Add a bullet point describing your engine in the release notes section.

### 7. Update Test Workflow (Optional)
**Location**: `.github/workflows/test.yml`

Add import and instantiation tests for your engine (around line 35 and 60):

```python
from engines.your_engine_name import YourEngineClass
```

```python
YourEngineClass(),
```

### 8. Update README.md
**Location**: `README.md`

Add documentation for your engine in the "Available Engines" section (around line 70-180):

```markdown
### X. Your Engine Name
- **Weakness Level**: ⭐⭐⭐ (Weak/Moderate/etc)
- **Strategy**: Brief description of move selection strategy
- **Characteristics**: How it plays, what makes it unique
- **Good for**: What it's useful for testing or learning
```

## Summary: Files to Modify

When adding a new engine, you need to create/modify these files:

### Files to Create (2):
1. `src/engines/your_engine_name.py` - Engine implementation
2. `scripts/your_engine_name.py` - UCI launcher script

### Files to Modify (6):
1. `main.py` - Add to GUI (import, engine list, description)
2. `tournament.py` - Add to tournament (import, engines list)
3. `build.py` - Add to build script
4. `.github/workflows/build-release.yml` - Add to CI/CD pipeline
5. `.github/workflows/test.yml` - (Optional) Add to tests
6. `README.md` - Add documentation

## Testing Your New Engine

After adding your engine, test it:

1. **Direct Execution**:
   ```bash
   python scripts/your_engine_name.py
   ```

2. **GUI Testing**:
   ```bash
   python main.py
   ```
   - Select your engine from the dropdown
   - Play a game to verify it works

3. **Tournament Testing**:
   ```bash
   python tournament.py
   ```
   - Your engine will compete with all others

4. **Build Testing**:
   ```bash
   python build.py
   ```
   - Verify the executable is created

## Common Pitfalls

1. **Forgetting imports**: Make sure to add imports in ALL files that need them
2. **Name consistency**: Use the same naming convention across all files
3. **Rating stars**: Match the star rating format in GUI (⭐⭐⭐)
4. **UCI compliance**: Ensure your engine properly implements `get_best_move()`
5. **Error handling**: Add try-catch in `get_best_move()` for robustness

## Example: Adding a "Center-Loving" Engine

Here's a quick example of what you'd name things:

- Class: `CenterLovingEngine`
- File: `src/engines/center_loving_engine.py`
- Script: `scripts/center_loving_engine.py`
- Display name: `"Center Loving (⭐⭐)"`
- Tournament name: `"Center Loving"`
- Build name: `"center_loving_engine"`

Keep this naming consistent across all 8 files!
