# Centaurus - Simulador de la Batalla por Centauro

Centaurus es una implementacion en Python que resuelve el **Problema 3** de la Fase 2 del curso Fundamentos de Programacion (codigo 213022) de la UNAD. El programa permite configurar ejercitos benevolos y malvados, calcular la fuerza total de cada bando y determinar el resultado de la batalla. Incluye interfaz de consola, interfaz grafica basada en Tkinter, generacion musical procedimental de 8 bits y un panel de creditos integrado.

## 1. Requisitos

- Python 3.11 o superior.
- `pip` para instalar dependencias opcionales.
- Tkinter (incluido en la mayoria de distribuciones de Python). Si no esta disponible:
  - Windows: instalar Python desde [python.org](https://www.python.org/downloads/) marcando la opcion *tcl/tk and IDLE*.
  - macOS: `brew install python-tk`
  - Debian/Ubuntu: `sudo apt install python3-tk`
  - Fedora/RHEL: `sudo dnf install python3-tkinter`
- (Opcional) `pygame` para activar la musica procedimental (`pip install pygame`). El programa intentara instalarlo automaticamente si detecta que falta.

## 2. Puesta en marcha rapida

1. Clonar o descomprimir el repositorio.
2. (Opcional) Crear un entorno virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   source .venv/bin/activate # Linux o macOS
   ```
3. Instalar dependencias opcionales:
   ```bash
   pip install pygame
   ```
4. Ejecutar el simulador:
   ```bash
   python main.py
   ```

## 3. Modos de ejecucion

| Modo | Comando | Descripcion |
|------|---------|-------------|
| Menu interactivo (por defecto) | `python main.py` | Pregunta si se desea interfaz de consola o GUI. |
| Consola | `python main.py --mode console` | Despliega un menu textual con opciones para ejercitos, musica y creditos. |
| GUI (Tkinter) | `python main.py --mode gui` | Abre una ventana con controles graficos, musica activa por defecto y boton de creditos. |
| Sin musica | Agregar `--no-music` | Evita inicializar el generador musical (util si no hay audio disponible). |

La configuracion de tropas se guarda automaticamente en `data/armies.json`. Para reiniciar el progreso basta con eliminar ese archivo.

## 4. Caracteristicas principales

- **Simulacion del Problema 3:** modela las razas y valores indicados en la guia academica.
- **Persistencia en JSON:** los ejercitos quedan almacenados entre sesiones.
- **Interfaz dual:** consola y Tkinter comparten la misma logica central.
- **Musica procedimental:** generador 8 bits inspirado en RPG clasicos y proporciones aureas.
- **Creditos integrados:** disponibles desde el menu de consola y mediante boton en la GUI.

## 5. Creditos

Dentro de la aplicacion:
- Consola: opcion `7) Ver creditos`.
- GUI: boton **Creditos** en la barra inferior.

Tambien estan disponibles en el documento `Informe_Fase2.md`.

## 6. Pruebas automatizadas

```bash
python -m unittest
```

## 7. Entregables academicos

El repositorio incluye el documento `Informe_Fase2.md`, el cual contiene:
- Portada con los datos institucionales solicitados.
- Identificacion del problema elegido (Problema 3 del Anexo 1).
- Tabla de requerimientos funcionales.
- Descripcion de la solucion implementada.
- Referencia al codigo fuente y conclusiones.
- Listado de referencias bibliograficas.

El diagrama de flujo se agregara posteriormente de acuerdo con la guia.

---

Disfruta recreando la batalla por Centauro y ajusta los ejercitos hasta encontrar la estrategia perfecta. Si deseas personalizar la musica, coloca un archivo `assets/retro_theme.mp3`; el sistema lo reproducira en lugar del tema procedimental.
