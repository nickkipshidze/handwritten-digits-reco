import pyglet
from pyglet.window import key

import model
from model import TinyVGG

class MainWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixels = []
        self.grid_size = (28, 28)
        self.grid_offsets = (30, 30)
        self.grid_cell_size = 15
        self.cells = [[0 for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

        self.notes = [
            pyglet.text.Label(x=self.width-320, y=self.height-30, text="Made by Nick Kipshidze", font_name="monospace", font_size=18, bold=True),
            pyglet.text.Label(x=10, y=self.height-30, text="Press C to clear the grid", font_name="monospace", font_size=16)
        ]
        self.prediction_label = pyglet.text.Label(x=500, y=200, text="Model prediction", font_name="monospace", font_size=18)
        self.prediction_prob = pyglet.text.Label(x=500, y=250, text="Model prediction", font_name="monospace", font_size=18)

        self.model = model.Model("tinyvgg-trained.pth")

        pyglet.clock.schedule_interval(self.predict_model, 1/30)
    
    def draw_grid(self, size=(28, 28), offsets=(0, 0), step=20, color=(255, 255, 255, 125)):
        gridbatch = pyglet.shapes.Batch()
        lines = []
        ox, oy = offsets
        w, h = size
        for x in range(0, w * step, step):
            lines.append(pyglet.shapes.Line(x+ox, oy, x+ox, h*step+oy, 1, color=color, batch=gridbatch))
        lines.append(pyglet.shapes.Line(x+ox+step, oy, x+ox+step, h*step+oy, 1, color=color, batch=gridbatch))
        lines.append(pyglet.shapes.Line(ox, oy+(h*step), w*step+ox, oy+(h*step), 1, color=color, batch=gridbatch))
        for y in range(0, h * step, step):
            lines.append(pyglet.shapes.Line(ox, y+oy, w*step+ox, y+oy, 1, color=color, batch=gridbatch))
        gridbatch.draw()
    
    def grid_coords(self, absolute=(0, 0)):
        relative = [absolute[0] - self.grid_offsets[0], absolute[1] - self.grid_offsets[1]]
        relative[0] //= self.grid_cell_size
        relative[1] //= self.grid_cell_size
        if self.grid_size[0] > relative[0] >= 0 and self.grid_size[1] > relative[1] >= 0:
            return relative
        else:
            return None
    
    def draw_cells(self):
        cellsbatch = pyglet.shapes.Batch()
        cells = []
        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                cells.append(
                    pyglet.shapes.Rectangle((x*self.grid_cell_size)+self.grid_offsets[0], (y*self.grid_cell_size)+self.grid_offsets[1], self.grid_cell_size, self.grid_cell_size, color=(255, 255, 255, self.cells[y][x]), batch=cellsbatch)
                )
        cellsbatch.draw()
    
    def fill_cell(self, coords, step=80):
        if self.grid_size[0] > coords[0] >= 0 and self.grid_size[1] > coords[1] >= 0:
            self.cells[coords[1]][coords[0]] += step
            self.cells[coords[1]][coords[0]] = min(255, self.cells[coords[1]][coords[0]])
    
    def on_draw(self):
        self.clear()

        for pixel in self.pixels:
            pixel.draw()
        self.draw_grid(self.grid_size, self.grid_offsets, self.grid_cell_size)
        self.draw_cells()

        self.prediction_label.draw()
        self.prediction_prob.draw()
        for note in self.notes:
            note.draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        relative = self.grid_coords((x, y))
        if relative != None:
            x, y = relative
            self.fill_cell((x, y))
            self.fill_cell((x+1, y+1))
            self.fill_cell((x, y+1))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.C:
            self.cells = [[0 for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

    def predict_model(self, dt):
        pred_label, pred_prob = self.model.predict(self.cells)
        self.prediction_label.text = f"Prediction: {pred_label}"
        self.prediction_prob.text = f"Certainty: {pred_prob:.2f}%"

window = MainWindow(
    width=1024,
    height=512
)

pyglet.app.run()