import os
from opendm import io
from opendm import log
from opendm import system
from opendm import progress
from opendm.stage import Stage

from pipes import quote

class DEMStage(Stage):
    def process(self, args, outputs):
        cm = outputs["cm"]
        
        # TODO: port DEM interpolation code from ODM
        dsm_file = os.path.join(args.project_path, 'odm_dem', 'dsm.tif')

        if not os.path.exists(dsm_file) or self.rerun():
            kwargs = {
                'input': quote(outputs["georeferenced_point_cloud_file"]),
                'output': quote(dsm_file),
                'resolution': args.dem_resolution / 100.0
            }
            system.run('pdal translate --input {input} --output {output} '
                       '--writers.gdal.output_type="idw" '
                       '--writers.gdal.resolution={resolution}'.format(**kwargs))
        else:
            log.ODM_WARNING("Found existing DSM: %s" % dsm_file)
