from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToJson
import requests
import json
from datetime import datetime


direction_lookup = {1: "West",
                    5: "Counterclockwise",
                    6: "North",
                    7: "South",
                    8: "Spec"}


def get_feed(force_update=False, save_cache=False):
    if force_update:
        feed = gtfs_realtime_pb2.FeedMessage()
        response = requests.get(
            "https://gtfs.edmonton.ca/TMGTFSRealTimeWebService/TripUpdate/TripUpdates.pb")

        feed.ParseFromString(response.content)
        serialized = MessageToJson(feed)

        if save_cache:
            with open("tu.json", "w+") as f:
                f.write(serialized)

        return json.loads(serialized)
    else:
        with open("tu.json", "r") as f:
            return json.loads(f.read())
        return {}


def get_vehicle_rt(force_update=False, save_cache=False):
    if force_update:
        feed = gtfs_realtime_pb2.FeedMessage()
        response = requests.get(
            "https://gtfs.edmonton.ca/TMGTFSRealTimeWebService/Vehicle/VehiclePositions.pb")

        feed.ParseFromString(response.content)
        serialized = MessageToJson(feed)

        if save_cache:
            with open("vehicle.json", "w+") as f:
                f.write(serialized)

        return json.loads(serialized)
    else:
        with open("vehicle.json", "r") as f:
            return json.loads(f.read())
        return {}


def get_stop(force_update=False, save_cache=False):
    if force_update:
        stops = requests.get(
            "https://data.edmonton.ca/api/views/4vt2-8zrq/rows.json?accessType=DOWNLOAD")
        json_stops = stops.json()

        if save_cache:
            with open("stops.json", "w+") as f:
                f.write(json_stops)

        return json_stops
    else:
        with open("stops.json", "r") as f:
            return json.loads(f.read())
        return {}


def get_stop_name(stops, stopId):
    data = stops["data"]
    for stop in data:
        if stop[8] == stopId:
            return stop[10]
    return "Unknown"


def stop_info(feed, stopId):
    data_time = (int(feed["header"]["timestamp"]))
    res = []
    for ent in feed['entity']:
        tu = ent.get("tripUpdate")
        if tu:
            for stop in tu.get("stopTimeUpdate"):
                if stop.get("stopId") == stopId:
                    trip = {
                        "id": tu["trip"]["tripId"],
                        "route": tu["trip"]["routeId"],
                        "vehicle": tu["vehicle"]["label"],
                        "direction": direction_lookup.get(tu["trip"].get("directionId"), "Unknown"),
                        "time": None,
                        "delay": None
                    }

                    if stop.get("departure"):
                        ref = stop["departure"]
                    elif stop.get("arrival"):
                        ref = stop["arrival"]
                    else:
                        ref = {"time": "Unknown"}

                    trip["time"] = int(ref["time"])
                    trip["delay"] = ref.get("delay")

                    res.append(trip)
    res.sort(key=lambda x: x.get("time"))
    return res


def format_stop_info(stop_info):
    t = ""
    time_now = datetime.now().timestamp()
    for trip in stop_info:
        t += "[{id}]{route:^6}<{direction:^12}> ({vehicle:^4}): {time_f:5} ({time_e})".format(
            **trip,
            time_f=datetime.fromtimestamp(trip["time"]).strftime("%H:%M"),
            time_e="past" if time_now > trip["time"] else "in {time_d:.1f} min{delay_f}".format(
                time_d=(trip["time"] - datetime.now().timestamp()) / 60,
                delay_f="" if not trip["delay"] else ", {:.1f} min {}".format(abs(trip["delay"] / 60),
                                                                              ("early" if trip[
                                                                                  "delay"] < 0 else "late"))
            )
        ) + "\n"
    return t
