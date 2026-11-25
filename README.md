# Gedämpfte Schwingung

Interaktives [marimo](https://marimo.io)-Notebook zur Vorlesung [Experimentalphysik für Elektrotechnik](https://moodle.ruhr-uni-bochum.de/course/view.php?id=73123), [Übungsblatt 06](https://moodle.ruhr-uni-bochum.de/mod/resource/view.php?id=3872721), Aufgabe 3. Durch Ziehen an der Abklingkonstante $\delta$ und der Eigenkreisfrequenz $\omega_0$ in der Bewegungsgleichung lassen sich Schwingfall, aperiodischer Grenzfall und Kriechfall der gedämpften harmonischen Schwingung vergleichen. Das Notebook wird als statische WebAssembly-Seite exportiert und auf GitHub Pages veröffentlicht, sodass es ohne Installation im Browser läuft.

## Lokal ausführen

Benötigt wird nur [uv](https://docs.astral.sh/uv/). `uvx` lädt marimo bei Bedarf herunter, und `--sandbox` installiert die übrigen Pakete aus dem PEP-723-Kopf des Notebooks in eine eigene Umgebung.

Falls uv noch nicht installiert ist, geht das unter Linux und macOS mit

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

und unter Windows mit

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Weitere Möglichkeiten beschreibt die [Installationsanleitung](https://docs.astral.sh/uv/getting-started/installation/). Danach startet das Notebook mit:

```bash
uvx marimo edit --sandbox apps/gedaempfte_schwingung.py
```

Neue Abhängigkeiten werden in diesem Kopf eingetragen; der WebAssembly-Export bestimmt daraus auch die Pakete für Pyodide.

## WebAssembly-Build lokal testen

```bash
uvx marimo export html-wasm apps/gedaempfte_schwingung.py -o dist --mode run --no-show-code --no-sandbox --force
uv run python -m http.server -d dist
```

Danach die ausgegebene Adresse im Browser öffnen. Ein direktes Öffnen von `dist/index.html` über `file://` funktioniert nicht.