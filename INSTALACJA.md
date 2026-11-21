# 🚀 Instrukcje Instalacji - Earth Simulator Enhanced v2.0

## 📋 Wymagania Systemowe

### Minimalne Wymagania
- **System operacyjny**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.8 lub nowszy
- **Pamięć RAM**: 2GB
- **Miejsce na dysku**: 100MB
- **Karta graficzna**: Obsługa OpenGL 3.0+

### Zalecane Wymagania
- **System operacyjny**: Windows 11, Ubuntu 20.04+, macOS 12+
- **Python**: 3.9 lub nowszy
- **Pamięć RAM**: 4GB
- **Miejsce na dysku**: 200MB
- **Karta graficzna**: Dedykowana karta z obsługą OpenGL 4.0+

## 🔧 Instalacja Krok po Kroku

### 1. Sprawdzenie Wersji Python

```bash
# Windows
python --version

# Linux/macOS
python3 --version
```

**Wymagana wersja**: Python 3.8+

### 2. Aktualizacja pip

```bash
# Windows
python -m pip install --upgrade pip

# Linux/macOS
python3 -m pip install --upgrade pip
```

### 3. Instalacja Zależności

```bash
# Windows
pip install -r requirements.txt

# Linux/macOS
pip3 install -r requirements.txt
```

### 4. Sprawdzenie Plików Tekstur

Upewnij się, że w katalogu programu znajdują się pliki:
- `earth_texture.png`
- `earth_political.jpg`
- `earth_detailed.jpg`

### 5. Test Instalacji

```bash
# Uruchom test
python test_enhanced.py

# Lub uruchom główny program
python earth_simulator_enhanced.py
```

## 🐛 Rozwiązywanie Problemów

### Problem: "ModuleNotFoundError: No module named 'pygame'"

**Rozwiązanie:**
```bash
pip install pygame
```

### Problem: "ModuleNotFoundError: No module named 'OpenGL'"

**Rozwiązanie:**
```bash
pip install PyOpenGL PyOpenGL_accelerate
```

### Problem: "ModuleNotFoundError: No module named 'numpy'"

**Rozwiązanie:**
```bash
pip install numpy
```

### Problem: "ModuleNotFoundError: No module named 'PIL'"

**Rozwiązanie:**
```bash
pip install Pillow
```

### Problem: Błędy OpenGL na Windows

**Rozwiązanie:**
1. Zaktualizuj sterowniki karty graficznej
2. Sprawdź czy karta obsługuje OpenGL 3.0+
3. Spróbuj uruchomić jako administrator

### Problem: Błędy OpenGL na Linux

**Rozwiązanie:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-opengl

# Fedora
sudo dnf install python3-opengl

# Arch Linux
sudo pacman -S python-opengl
```

### Problem: Błędy OpenGL na macOS

**Rozwiązanie:**
```bash
# Zainstaluj przez Homebrew
brew install python3
pip3 install PyOpenGL
```

## 🔍 Diagnostyka

### Sprawdzenie Zależności

```bash
python -c "
import pygame
import OpenGL
import numpy
from PIL import Image
print('✅ Wszystkie zależności są dostępne')
"
```

### Sprawdzenie OpenGL

```bash
python -c "
from OpenGL.GL import *
from OpenGL.GLU import *
print('✅ OpenGL jest dostępny')
"
```

### Sprawdzenie Plików

```bash
# Windows
dir *.jpg

# Linux/macOS
ls -la *.jpg
```

## 📊 Testy Wydajności

### Test FPS
Program powinien działać z 60 FPS na nowoczesnych systemach.

### Test Pamięci
Program używa około 100-200MB RAM.

### Test CPU
Program używa około 10-20% CPU podczas normalnej pracy.

## 🔧 Konfiguracja Zaawansowana

### Zmiana Rozdzielczości
Edytuj plik `simulator_config.json`:
```json
{
  "resolution": [1920, 1080]
}
```

### Zmiana Czułości Mysz
```json
{
  "mouse_sensitivity": 0.3
}
```

### Wyłączenie Auto-rotacji
```json
{
  "auto_rotate": false
}
```

## 📝 Logi

### Lokalizacja Plików Logów
- `earth_simulator.log` - główne logi programu
- `simulator_config.json` - konfiguracja
- `user_preferences.json` - preferencje użytkownika

### Poziomy Logowania
- **INFO** - informacje o działaniu programu
- **WARNING** - ostrzeżenia
- **ERROR** - błędy krytyczne

## 🆘 Wsparcie

### Jeśli Program Nie Uruchamia Się

1. **Sprawdź logi**:
   ```bash
   cat earth_simulator.log
   ```

2. **Uruchom w trybie debug**:
   ```bash
   python -u earth_simulator_enhanced.py
   ```

3. **Sprawdź zależności**:
   ```bash
   python test_enhanced.py
   ```

### Kontakt
- **Autor**: Adrian Lesniak
- **Wersja**: 2.0
- **Data**: 2024

## ✅ Lista Kontrolna Instalacji

- [ ] Python 3.8+ zainstalowany
- [ ] pip zaktualizowany
- [ ] Zależności zainstalowane
- [ ] Pliki tekstur obecne
- [ ] Test przechodzi pomyślnie
- [ ] Program uruchamia się
- [ ] Interfejs działa poprawnie
- [ ] Sterowanie myszą działa
- [ ] Menu działa
- [ ] Zapisywanie/odczytywanie działa

---

**🌟 Instalacja zakończona pomyślnie! 🌟**

Możesz teraz uruchomić program:
```bash
python earth_simulator_enhanced.py
``` 