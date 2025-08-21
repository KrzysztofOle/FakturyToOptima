#!/bin/bash
# Aktywacja środowiska wirtualnego venv312 w bieżącym katalogu

if [ -d ".venv" ]; then
    source venv312/bin/activate
    echo "Środowisko venv312 zostało aktywowane."
else
    echo "Brak katalogu venv312 – najpierw utwórz środowisko:"
    # echo "python3 -m venv venv312"
fi