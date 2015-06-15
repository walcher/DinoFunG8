import tornado.ioloop
import tornado.web
import os
import pandas as pd
import numpy as np

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_map.html")

class DinoFilter(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_filter.html")

class HeatMapFilter(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_heat_map.html")


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


class HeatMapDataHandler(tornado.web.RequestHandler):
    def get(self):
        df = self.df
        #data_list = self.data_list



        #data_list["Time"] = pd.to_datetime(data_list.Timestamp, format="%Y-%m-%d %H:%M:%S")

        endhour = self.get_argument("endhour", None)

        print(endhour)
        '''
        hour_id = self.get_argument("hour", None)

        minute_id = self.get_argument("minute", None)
        if hour_id is None:
            hour_id = 8
        if minute_id is None:
            minute_id = 0

        starthour = repr(int(hour_id)) + ":" + repr(int(minute_id))

        if((int(minute_id) + 5) >= 60):
            hour_id = int(hour_id) + 1

        minute_id = (int(minute_id) + 5) % 60

        endhour = repr(int(hour_id)) + ":" + repr(minute_id)

        print(starthour)
        print(endhour)

        data_filtered = df.loc[df.Time.between_time("8:00",endhour)]

        '''

        data_filtered = df.loc[df.Time.between_time("8:00",endhour)]

        if not data_filtered.empty:
            data_times = data_filtered.groupby("id")["type","Time","Timestamp","X","Y","id"]
            print(data_times.__class__)
            data_times = data_times.max()
            del data_times["Time"]
            data = data_times.to_dict("records")
            print(data_times.count())
            self.write({"array" :data})

    def initialize(self, df):
        self.df = df[["X","Y","id","Timestamp","type","Time"]]
        #self.data_list = data_list[["Timestamp","type","X","Y","id"]]



settings = {"template_path" : os.path.dirname(__file__),
            "static_path" : os.path.join(os.path.dirname(__file__),"static"),
            "debug" : True
            } 

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "park-movement-Fri.csv")
    print('loading...')
    df = pd.read_csv(path)


    df["Time"] = pd.to_datetime(df.Timestamp, format="%Y-%m-%d %H:%M:%S")
    df.reset_index(inplace=True)
    index = pd.DatetimeIndex(df.Time)
    df = df.set_index(index)

    print('loaded')
    #heat_map_data = df.groupby(["X","Y","Timestamp","type"]).count()
    #heat_map_data.reset_index(inplace=True)

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/data", DataHandler,{"df":df}),
        (r"/heatmapdata", HeatMapDataHandler,{"df":df}),
        (r"/filter", DinoFilter),
        (r"/heatmap", HeatMapFilter),
        (r"/filter_data", FilterData,{"df":df}),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
            {"path": settings["static_path"]})

    ], **settings)
    application.listen(8100)
    print("ready")
    tornado.ioloop.IOLoop.current().start()

