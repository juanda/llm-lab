# Modelos inspeccionados

Esta carpeta guarda salidas reproducibles de inspección de modelos locales en Ollama.

Comandos:

```bash
python3 scripts/show_model_info.py qwen2.5-coder:3b llama3.2:3b
python3 scripts/export_modelfile.py qwen2.5-coder:3b llama3.2:3b
```

Archivos esperados:

```text
qwen2.5-coder-3b.show.txt
qwen2.5-coder-3b.modelfile
llama3.2-3b.show.txt
llama3.2-3b.modelfile
```

No se versionan necesariamente todos los ficheros generados. Cuando se usen como evidencia en un experimento, registrar fecha, versión de Ollama y modelo exacto.
