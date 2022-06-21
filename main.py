# encoding: utf-8
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
import pyodbc

class MainApp(MDApp):
    """r_call_data = [('3100','20.5')]
    c_call_data = [('Strike Price',dp(40)),('Price',dp(30))]

    r_put_data = [('3100','20.5')]
    c_put_data = [('Strike Price',dp(40)),('Price',dp(30))]
    i = 0
"""
    myData=''


    connection_data = ("Driver={SQL Server};""Server=LAPTOP-DU1INKAP\SQLEXPRESS;""Database=testDB;")

    #     "password = 'Consultas';"
    #   "username = dbo;"
    connection = pyodbc.connect(connection_data)
    cursor = connection.cursor()

    def on_start(self):
        try:
            #Clock.schedule_interval(self.update_table,1.5)
            self.create_table()
        except:
            pass
    def build(self):
        layout = MDBoxLayout(orientation='vertical')
        self.image = Image()
        layout.add_widget(self.image)
        """
        self.save_img_button = MDRaisedButton(
            text='CLICK HERE',
            pos_hint={'center_x': .5, 'center_y': .5},
            size_hint=(None, None))
        self.save_img_button.bind(on_press=self.take_picture)
        layout.add_widget(self.save_img_button)
        
        self.set_table(
            [
                (f"{i + 1}", "2.23", "3.65")
                for i in range(50)
            ]
        )
        """
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.load_video, 1.0/30.0)
        self.card = MDCard(
            size_hint=(1, .7),
            #size=("100dp", "1000dp"),
            pos_hint= {"center_x": .5, "center_y": 0},
            ripple_behavior= True,
            elevation=15
        )
        layout.add_widget(self.card)
        return layout

    def set_table(self, data):
        self.data_tables = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            #check=True,
            column_data=[
                ("Quant.", dp(20)),
                ("Artigo", dp(20)),
                ("Descrição", dp(60))
            ],
            row_data=data,
        )

    def on_start(self):
        #self.card.add_widget(self.data_tables)
        pass

    def load_video(self, *args):
        with open('myDataFile.text') as f:
            myDataList = f.read().splitlines()

        ret, frame = self.capture.read()
        for barcode in decode(frame):
            self.myData = barcode.data.decode('utf-8')
            print(self.myData)

            if self.myData in myDataList:
                myOutput = 'OK'
                myColor = (0, 255, 0)
                self.update_table()
            else:
                myOutput = 'Desconhecido'
                myColor = (0, 0, 255)

            pts = np.array([barcode.polygon], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, myColor, 5)
            pts2 = barcode.rect
            cv2.putText(frame, myOutput, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_COMPLEX,
                        0.9, myColor, 2)

        # Frame initialize
        self.image_frame = frame
        buffer = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture

    def take_picture(self, *args):
        image_name = "picture_at_2_02.png"
        cv2.imwrite(image_name, self.image_frame)

    def create_table(self):

        self.data_tables = MDDataTable(
            id='table',
            size_hint=(0.9, 0.6),
            use_pagination=True,
            check=True,
            column_data=self.c_data,
            row_data=self.r_data,
        )
        # self.datatable.bind(on_row_press=self.on_row_press)
        # self.datatable.bind(on_check_press=self.on_check_press)
        self.root.ids.card.add_widget(self.data_tables)

    def update_table(self, *args):
        #self.data_tables.cls
        self.card.clear_widgets()
        comand = """SELECT Localizacoes.artigo, Artigos.descricao, Localizacoes.quantidade FROM Artigos INNER JOIN Localizacoes ON Artigos.artigo = Localizacoes.artigo WHERE (Localizacoes.localizacao = N'""" + """SV.A311""" + """')"""
        self.cursor.execute(comand)
        row = self.cursor.fetchone()
        strW=[]
        while row:
            strW.append((str(row[2]), row[0], row[1]))
            row = self.cursor.fetchone()
        self.set_table(
            strW
        )
        self.card.add_widget(self.data_tables)


if __name__ == '__main__' :
    MainApp().run()
