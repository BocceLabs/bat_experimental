import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line


class DrawingWidget(Widget):
    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 1, 0)
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=2)

    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]


class MainWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)

        # Load the image
        img = Image(source='alpaca.png')
        self.add_widget(img)

        # Add the drawing widget on top of the image
        drawing_widget = DrawingWidget()
        self.add_widget(drawing_widget)


class MyApp(App):
    def build(self):
        return MainWidget()


if __name__ == '__main__':
    MyApp().run()
