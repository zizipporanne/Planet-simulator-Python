# Earth Simulator Enhanced

Interactive 3D Earth simulator built with Pygame and OpenGL.

## Run

Install dependencies and start the application:

```bash
pip install -r requirements.txt
python main.py
```

`earth_simulator_enhanced.py` remains available as a compatibility launcher.

## Controls

- Drag with the left mouse button to rotate the globe.
- Use the mouse wheel to zoom.
- Double-click to reset the view.
- `M` toggles the side panel; `L` cycles Earth textures.
- `R` resets the view; `V` cycles Normal, Wireframe, Points, and Night modes.
- `A`, `S`, `E`, and `T` toggle animation, statistics, effects, and screenshots.
- `Escape` saves the current state and exits.

The top bar offers view and feature actions, plus settings, help, sound, and
exit. The side panel provides About, Instructions, Settings, Save State,
Load State, Reset View, and Exit actions. Notifications are non-blocking.

## Project layout

- `core/`: application state, JSON configuration, and input dispatch.
- `render/`: OpenGL camera, Earth display list, and texture loading.
- `ui/`: top bar, buttons, side panel, and transient notifications.
- `main.py`: application composition and event loop.
- `earth_simulator_enhanced.py`: compatibility entry point.

The required textures are loaded from the script directory:
`earth_texture.png`, `earth_political.png`, and `earth_detailed.jpg`.
Configuration continues to use `simulator_config.json`.

## Tests

Run the window-independent state and configuration tests with:

```bash
python -m unittest discover -s tests
```
