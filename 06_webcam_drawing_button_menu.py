import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget, Canvas
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import RenderContext, Rectangle
from kivy.core.image import Image as CoreImage
from kivy.graphics import ClearColor, ClearBuffers
from PIL import Image
from kivy.graphics.fbo import Fbo

import cv2
import numpy as np
from kivy.config import Config
import math

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')

# NOTE!!!!!!!!!! Default ordinal for laptop webcam is 0, but mine is 3 since I use ManyCam
CAMERA_ORDINAL = 3

PEN_COLORS = [
    [1,1,1,1],
    [1,0,0,1],
    [0,1,0,1],
    [0,0,1,1],
    [1,1,0,1],
    [0,1,1,1],
    [1,0,1,1]
]

def euclidean_distance(point1, point2):
    """
    Calculates the Euclidean distance between two points in two-dimensional space.
    The points should be given as tuples or lists of two numbers, representing the
    x and y coordinates of each point.
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx*dx + dy*dy)


class TargetZone(Widget):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.color = [1, 1, 1, 1]
        self.bind(pos=self.update_circle, size=self.update_circle)
        self.circle = None

    def on_touch_down(self, touch):
        with self.canvas:
            Color(*self.color)
            touch.ud['circle'] = Ellipse(pos=(touch.x, touch.y), size=(1, 1))
            touch.ud['center'] = (touch.x, touch.y)

    def on_touch_move(self, touch):
        circle = touch.ud['circle']
        center = touch.ud['center']
        radius = euclidean_distance((touch.x, touch.y), center)
        circle.pos = (center[0] - radius, center[1] - radius)
        circle.size = (radius*2, radius*2)

    def update_circle(self, *args):
        if self.circle:
            self.circle.pos = self.pos
            self.circle.size = self.size
        self.canvas.clear()
        with self.canvas:
            Color(*self.color)
            self.circle = Ellipse(pos=self.pos, size=self.size)


class PenWidget(Widget):
    def __init__(self, **kwargs):
        super(PenWidget, self).__init__(**kwargs)
        self.strokes = []
        self.stroke_colors = []  # new list to store the color for each stroke
        self.mouse_down = False
        self.color = [1, 1, 1, 1]

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False

        if touch.button == 'right':
            self.canvas.clear()
            self.strokes = []
            self.stroke_colors = []  # clear the list of stroke colors
            return True

        elif touch.button == 'left':
            with self.canvas:
                touch.ud["line"] = Line(points=(touch.x, touch.y), width=5)
                self.strokes.append([(touch.x, touch.y)])
                self.stroke_colors.append(self.color)  # store the current color for this stroke

    def on_touch_move(self, touch):
        if touch.button == 'right':
            return

        if touch.button == 'left':
            touch.ud["line"].points += (touch.x, touch.y)
            self.strokes[-1].append((touch.x, touch.y))

    def set_pen_color(self, color):
        self.color = color

    def clear(self):
        self.canvas.clear()
        self.strokes = []
        self.stroke_colors = []




class WebcamWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(WebcamWidget, self).__init__(**kwargs)

        # create the pen widget and add it to the layout
        self.pen_widget = PenWidget()
        self.add_widget(self.pen_widget)

        # create the target zone widget and add it to the layout
        # self.target_zone_widget = TargetZone(color=(1,0,0,1))
        # self.add_widget(self.target_zone_widget)

        # Create the OpenCV capture object
        self.capture = cv2.VideoCapture(CAMERA_ORDINAL)
        self.texture = None

        # pause boolean
        self.pause = False

        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def update(self, dt):
        if not self.pause:
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
            with self.pen_widget.canvas:
                self.pen_widget.canvas.clear()
                Color(1, 1, 1)
                c = Canvas()
                Rectangle(texture=self.texture, pos=self.pos, size=self.size)
                for stroke, color in zip(self.pen_widget.strokes,
                                         self.pen_widget.stroke_colors):
                    points = []
                    for point in stroke:
                        points.extend([point[0], point[1]])
                    Color(*color)  # set the color for this stroke
                    Line(points=points, width=5)

    def screenshot(self):
        self.texture.save("screenshot.png")


class MainWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # Create a horizontal BoxLayout and add it to the layout

        # top down box layout
        vbox = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(vbox)

        # left to right box layout
        hbox = BoxLayout(orientation='horizontal', spacing=10)

        # left button container
        left_button_container = BoxLayout(orientation='vertical', spacing=10, size_hint=(None, 1))
        hbox.add_widget(left_button_container)

        # left buttons
        self.pen_button = Button(text='Pen', on_press=self.toggle_pen)
        left_button_container.add_widget(self.pen_button)
        self.pen_color = 0
        self.pen_button.background_color = PEN_COLORS[self.pen_color]
        left_button_container.add_widget(Button(text='Zone'))
        left_button_container.add_widget(Button(text='Bocce'))
        left_button_container.add_widget(Button(text='Pallino'))
        left_button_container.add_widget(Button(text='Clear'))

        # top button container
        top_button_container = BoxLayout(orientation='horizontal', spacing=10,
                                         size_hint=(1, None))
        vbox.add_widget(top_button_container)
        vbox.add_widget(hbox)

        # top buttons
        self.pause_button = Button(text="Pause", on_press=self.activate_pause)
        self.pause_button.color = [1, 0, 0, 1]
        top_button_container.add_widget(self.pause_button)
        top_button_container.add_widget(Button(text="Screenshot",
                                               on_press=self.activate_screenshot))

        # Create the WebcamWidget and add it to the horizontal BoxLayout
        self.webcam_widget = WebcamWidget()
        hbox.add_widget(self.webcam_widget)

    def toggle_pen(self, instance):
        self.pen_color += 1
        if self.pen_color >= len(PEN_COLORS):
            self.pen_color = 0
        self.webcam_widget.pen_widget.set_pen_color(PEN_COLORS[self.pen_color])

        # set the color of the button
        self.pen_button.background_color = PEN_COLORS[self.pen_color]

    def activate_pause(self, instance):
        # toggle pausing/playing
        self.webcam_widget.pause = not self.webcam_widget.pause

        # toggle the button text and font color
        if self.webcam_widget.pause:
            self.pause_button.text = "Play"
            self.pause_button.color = [0, 1, 0, 1]
        else:
            self.pause_button.text = "Pause"
            self.pause_button.color = [1, 0, 0, 1]

    def activate_screenshot(self, instance):
        self.webcam_widget.screenshot()



class MyApp(App):
    def build(self):
        return MainWidget()


if __name__ == '__main__':
    MyApp().run()
