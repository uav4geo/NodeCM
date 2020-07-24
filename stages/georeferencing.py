import os
from opendm import io
from opendm import log
from opendm import system
from opendm import progress
from opendm.location import parse_srs_header
from opendm.stage import Stage
from pipes import quote


class GeoreferencingStage(Stage):
    def process(self, args, outputs):
        
        georeferenced_point_cloud_file = os.path.join(args.project_path, 'odm_georeferencing', 'odm_georeferenced_model.laz')
        
        with open(outputs["utm_coords_file"], 'r') as f:
            srs_header = f.readline()
            outputs["utm_offset"] = list(map(float, f.readline().split(" ")))
            outputs["utm_srs"] = parse_srs_header(srs_header)

        if not os.path.exists(georeferenced_point_cloud_file) or self.rerun():
            # Easy-peasy with PDAL
            # Point cloud is already georegistered, but it's just offset
            offset_x, offset_y = outputs["utm_offset"]

            kwargs = {
                'input': quote(outputs["point_cloud_ply_file"]),
                'output': quote(georeferenced_point_cloud_file),
                'a_srs': "EPSG:%s" % outputs["utm_srs"].to_epsg(),
                'offset_x': offset_x,
                'offset_y': offset_y,
                'offset_z': 0,
            }

            system.run('pdal translate --input {input} --output {output} '
                       '--writers.las.offset_x={offset_x} '
                       '--writers.las.offset_y={offset_y} '
                       '--writers.las.offset_z={offset_z} '
                       '--writers.las.a_srs="{a_srs}" '
                       '--filters.transformation.matrix="1 0 0 {offset_x} 0 1 0 {offset_y} 0 0 1 {offset_z} 0 0 0 1" '
                       'transformation'.format(**kwargs))
        else:
            log.ODM_WARNING("Found existing georeferenced point cloud: %s" % georeferenced_point_cloud_file)

        outputs["georeferenced_point_cloud_file"] = georeferenced_point_cloud_file
