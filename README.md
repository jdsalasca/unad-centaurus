# Centaurus – Simulador de la Batalla por Centauro

Centaurus es un proyecto académico que simula la batalla entre los ejércitos del Bien y del Mal en el universo de Centauro. Incluye una interfaz de consola, una interfaz gráfica basada en Tkinter y una banda sonora retro generada procedimentalmente en tiempo real mediante `pygame`.

## Requisitos previos

- Python 3.11 o superior (se recomienda la misma versión utilizada para el desarrollo, 3.12).
- `pip` para instalar dependencias.
- (Opcional) [Tkinter](https://docs.python.org/3/library/tkinter.html) para habilitar la interfaz gráfica. En la mayoría de distribuciones viene incluido, pero si no está disponible:
  - **Windows**: instala Python desde [python.org](https://www.python.org/downloads/) asegurándote de marcar la opción *tcl/tk and IDLE* durante la instalación.
  - **macOS**: `brew install python-tk`
  - **Debian/Ubuntu**: `sudo apt install python3-tk`
  - **Fedora/RHEL**: `sudo dnf install python3-tkinter`
- (Opcional) [pygame](https://www.pygame.org/) para activar la música retro (`pip install pygame`). El programa intentará instalarla automáticamente si detecta que falta.

## Puesta en marcha

1. Clona este repositorio o descárgalo en tu equipo.
2. Desde la raíz del proyecto (`centaurus/`) crea y activa un entorno virtual (opcional pero recomendado):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # En Windows usa: .venv\Scripts\activate
   ```

3. Instala las dependencias opcionales necesarias:

   ```bash
   pip install pygame
   ```

   Si no deseas música retro, puedes omitir este paso. No existe ningún otro requisito externo: el resto del código usa únicamente la biblioteca estándar de Python.

## Cómo ejecutar el simulador

Desde la raíz del proyecto (`centaurus/`) puedes iniciar el juego con:

```bash
python main.py
```

Por defecto se mostrará un menú en consola que te permite elegir entre la interfaz de consola o la interfaz gráfica (si Tkinter está disponible). También puedes forzar el modo deseado mediante argumentos:

- **Modo consola**: `python main.py --mode console`
- **Modo gráfico (Tkinter)**: `python main.py --mode gui`
- **Menú interactivo**: `python main.py --mode menu` (valor por defecto)

### Música retro opcional

El parámetro `--no-music` evita cargar el reproductor de música retro, útil si no instalaste `pygame` o si tu entorno no puede reproducir audio:

```bash
python main.py --mode gui --no-music
```

Cuando `pygame` está instalado, el juego sintetiza automáticamente un tema de 8 bits cada vez que arranca. Puedes desactivar o activar la música tanto en la interfaz gráfica como en la consola. Si prefieres usar tu propia pista, coloca un archivo de audio compatible (por ejemplo MP3 u OGG) en `assets/retro_theme.mp3` y el reproductor lo utilizará en lugar del tema procedimental.

### Persistencia de ejércitos

Las configuraciones de tropas se guardan automáticamente en `data/armies.json`. Puedes eliminar este archivo para reiniciar por completo los ejércitos guardados.

## Ejecutar las pruebas automatizadas

El proyecto incluye un pequeño conjunto de pruebas basadas en `unittest`. Para ejecutarlas:

```bash
python -m unittest
```

Se recomienda correr las pruebas después de realizar cambios en la lógica de batalla o en las razas.

## Estructura principal del proyecto

- `main.py`: punto de entrada que inicializa controladores, dependencias y la interfaz elegida.
- `app/`: código fuente principal.
  - `controllers/`: orquestadores de la aplicación.
  - `domain/`: entidades y lógica del dominio de la batalla.
  - `infrastructure/`: persistencia en JSON y reproducción de música.
  - `services/`: reglas de negocio, cálculo de resultados de batallas y catálogo de razas.
  - `ui/`: implementaciones de la interfaz de consola y GUI.
  - `utils/`: utilidades varias (p. ej. instalación de dependencias opcionales).
- `assets/`: carpeta opcional para recursos personalizados (por ejemplo `retro_theme.mp3` si quieres sobrescribir la música procedimental).
- `data/armies.json`: archivo JSON donde se persisten los ejércitos configurados.
- `tests/`: pruebas automatizadas.

## Problemas comunes

- **Tkinter no disponible**: el programa continuará automáticamente en modo consola e imprimirá instrucciones para instalarlo. Consulta la sección de requisitos para activarlo manualmente.
- **pygame no se instala**: la aplicación seguirá funcionando, pero no habrá música retro. Revisa los mensajes en consola para conocer el error concreto.
- **Error de importaciones**: asegúrate de estar ejecutando los comandos desde la carpeta raíz `centaurus/` o de que tu entorno virtual esté activo.

¡Disfruta recreando la batalla por Centauro!
