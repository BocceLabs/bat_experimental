import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock


import cv2

# NOTE: your camera ordinal should likely be 0.  Mine is 3 since I have "ManyCam" installed
CAMERA_ORDINAL = 3

from kivy.graphics import Rectangle


class CameraWidget(Widget):

    def __init__(self, **kwargs):
        super(CameraWidget, self).__init__(**kwargs)
        self.capture = cv2.VideoCapture(CAMERA_ORDINAL)
        # set video resolution
        #self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        #self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def update(self, dt):
        # read frame from camera
        ret, frame = self.capture.read()
        if ret:
            # convert to texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            # add texture pixels
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # create rectangle instruction with texture
            self.rect = Rectangle(texture=texture, pos=self.pos, size=self.size)
            # display image from the texture
            self.canvas.ask_update()
            self.canvas.clear()
            self.canvas.add(self.rect)

    def on_stop(self):
        # release camera when app is closed
        self.capture.release()


class MainWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.camera = CameraWidget()
        self.add_widget(self.camera)

    def update(self, dt):
        self.camera.update(dt)


class MyApp(App):

    def build(self):
        main_widget = MainWidget()
        Clock.schedule_interval(main_widget.update, 1.0/60.0)
        return main_widget


# run Kivy App
if __name__ == '__main__':
    MyApp().run()
