import os
import math
from opendm import io
from opendm import log
from opendm import system
from pipes import quote
from opendm.location import get_utm_zone_and_hemisphere_from, convert_to_utm

def extract_georegistration(photos, georegistration_file):
    if len(photos) == 0:
        raise Exception("No input images, cannot create coordinates file of GPS positions")
    
    utm_zone = None
    hemisphere = None
    coords = []
    reference_photo = None
    for photo in photos:
        if photo.latitude is None or photo.longitude is None or photo.altitude is None:
            log.ODM_ERROR("Failed parsing GPS position for %s, skipping" % photo.filename)
            continue
        
        if utm_zone is None:
            utm_zone, hemisphere = get_utm_zone_and_hemisphere_from(photo.longitude, photo.latitude)

        try:
            coord = convert_to_utm(photo.longitude, photo.latitude, photo.altitude, utm_zone, hemisphere)
        except:
            raise Exception("Failed to convert GPS position to UTM for %s" % photo.filename)
        
        coords.append((photo.filename, coord))

    if utm_zone is None:
        raise Exception("No images seem to have GPS information")
        
    # Calculate average
    dx = 0.0
    dy = 0.0
    num = float(len(coords))
    for _, coord in coords:
        dx += coord[0] / num
        dy += coord[1] / num

    dx = int(math.floor(dx))
    dy = int(math.floor(dy))

    # Open output file
    with open(georegistration_file, "w") as f:
        for fname, coord in coords:
            f.write("%s %s %s %s\n" % (fname, coord[0] - dx, coord[1] - dy, coord[2]))


class ColmapContext:
    def __init__(self, project_path):
        self.project_path = project_path

    def run(self, command, **kwargs):
        params = ["--{} {}".format(k, quote(str(v))) for (k,v) in kwargs.items()]
        system.run("colmap {} {}".format(command, " ".join(params)))
