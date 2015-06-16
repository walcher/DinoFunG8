import tornado.ioloop
import tornado.web
import os
import pandas as pd
import numpy as np

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_map.html")

class HomeMainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_velocity.html")

class DinoFilter(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_filter.html")

class FilterData(tornado.web.RequestHandler):
    def get(self):
        x_min = float(self.get_argument("x_min"))
        x_max = float(self.get_argument("x_max"))
        y_min = float(self.get_argument("y_min"))
        y_max = float(self.get_argument("y_max"))
        t_min = np.datetime64(int(self.get_argument("t_min")),"ms")
        t_max = np.datetime64(int(self.get_argument("t_max")),"ms")

        df = self.df
        area = (df["X"]<=x_max) & (df["X"]>=x_min) & (df["Y"]<=y_max) & (df["Y"]>=y_min)
        time = (df["time"] >= t_min) & (df["time"] <= t_max)
        # as int
        guests = sorted(df.loc[area & time,"id"].unique().tolist())
        self.write({"guests" : guests})

    def initialize(self, df):
        self.df = df


class DataHandler(tornado.web.RequestHandler):
    def get(self):
        df = self.df
        guest_id = self.get_argument("id", None)
        if guest_id is None:
            guest_id = np.random.choice(df["id"])
        else:
            guest_id = int(guest_id)
        guest_df = df.loc[df["id"]==guest_id]
        guest_df_list = guest_df.to_dict("records")        
        self.write({"array" :guest_df_list})

    def initialize(self, df):
        self.df = df[["X","Y","id","Timestamp","type"]]

class VelocityDataHandler(tornado.web.RequestHandler):
    def get(self):
        dos = self.dos

        data = dos.to_dict("records")

        self.write({"array" :data})

    def initialize(self, dos):
        self.dos = dos[["id", "hora", "velocidad"]]

settings = {"template_path" : os.path.dirname(__file__),
            "static_path" : os.path.join(os.path.dirname(__file__),"static"),
            "debug" : True
            } 

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "park-movement-Fri.csv")
    print('loading...')
    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df.Timestamp, format="%Y-%m-%d %H:%M:%S")
    df["hora"] = pd.to_datetime(df.Timestamp, format="%Y-%m-%d %H:%M:%S").dt.hour

    def get_velocity(uno):
        uno = uno.reset_index()
        uno["distx"] = uno["X"].diff()
        uno["disty"] = uno["Y"].diff()
        uno["distancia"] =  np.sqrt( (uno["distx"]*5)**2 + (uno["disty"]*5)**2 )
        uno["dtime"] = uno["time"].diff()
        uno["velocidad"] = uno["distancia"]/(uno.dtime/np.timedelta64(1, 's'))

        return uno

    def get_mean_velocity(uno):
        uno["velocidadpromedio"] = uno["velocidad"].mean()
        return uno

    newdf = df.sample(frac=0.25)

    dos = newdf.groupby(["id","hora"]).apply(get_velocity)


    dos = dos.groupby(["id","hora"], as_index=False)["velocidad"].mean()
    dos[np.isnan(dos)]=0
    dos = pd.DataFrame(dos)

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/home", HomeMainHandler),
        (r"/data", DataHandler,{"df":df}),
        (r"/velocitydata", VelocityDataHandler,{"dos":dos}),
        (r"/filter", DinoFilter),
        (r"/filter_data", FilterData,{"df":df}),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
            {"path": settings["static_path"]})

    ], **settings)
    application.listen(8100)
    print("ready")
    tornado.ioloop.IOLoop.current().start()

