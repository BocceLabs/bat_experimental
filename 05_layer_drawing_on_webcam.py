import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window
from kivy.graphics.texture import Texture
import cv2
import numpy as np
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class DrawingWidget(Widget):
    def __init__(self, **kwargs):
        super(DrawingWidget, self).__init__(**kwargs)
        self.strokes = []
        self.mouse_down = False

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False

        if touch.button == 'right':
            self.canvas.clear()
            self.strokes = []
            return True

        elif touch.button == 'left':
            with self.canvas:
                Color(1, 1, 1)
                touch.ud["line"] = Line(points=(touch.x, touch.y), width=5)
                self.strokes.append([(touch.x, touch.y)])

    def on_touch_move(self, touch):
        if touch.button == 'right':
            return

        if touch.button == 'left':
            touch.ud["line"].points += (touch.x, touch.y)
            self.strokes[-1].append((touch.x, touch.y))

class MainWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)

        # Create the drawing widget and add it to the layout
        self.drawing_widget = DrawingWidget()
        self.add_widget(self.drawing_widget)

        # Create the OpenCV capture object
        # NOTE!!!!!!!!!!!!!! Default ordinal for laptop webcam is 0, but mine is 3 since I use ManyCam
        self.capture = cv2.VideoCapture(3)
        self.texture = None

        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def update(self, dt):
        # Read the frame from the camera
        ret, frame = self.capture.read()
        if not ret:
            return

        # Convert the frame to RGB format and flip it vertically
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.flip(frame, axis=0)

        # Create a Kivy Texture object from the frame
        self.texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        self.texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

        # Draw the previous strokes and the new texture
        with self.drawing_widget.canvas:
            self.drawing_widget.canvas.clear()
            Color(1, 1, 1)
            Rectangle(texture=self.texture, pos=self.pos, size=self.size)
            for stroke in self.drawing_widget.strokes:
                points = []
                for point in stroke:
                    points.extend([point[0], point[1]])
                Color(1, 0, 0)
                Line(points=points, width=5)



class MyApp(App):
    def build(self):
        return MainWidget()


if __name__ == '__main__':
    MyApp().run()
