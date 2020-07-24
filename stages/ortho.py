import os

from opendm import io
from opendm import log
from opendm import system
from opendm.location import parse_srs_header
from opendm.concurrency import get_max_memory
from opendm.stage import Stage

from pipes import quote

from app import orthophoto

class OrthoStage(Stage):
    def process(self, args, outputs):
        orthophoto_file = os.path.join(args.project_path, "odm_orthophoto", "odm_orthophoto.tif")
        orthophoto_render_file = os.path.join(args.project_path, "odm_orthophoto", "odm_orthophoto_render.tif")
        orthophoto_corners_file = os.path.join(args.project_path, "odm_orthophoto", "odm_orthophoto_corners.txt")
        
        if not io.file_exists(orthophoto_file) or self.rerun():
            kwargs = {
                'ortho': orthophoto_render_file,
                'corners': orthophoto_corners_file,
                'res': 100.0 / args.orthophoto_resolution,
                'verbose': '--verbose' if args.verbose else '',
                'models': outputs["textured_model_obj"]
            }

            system.run('odm_orthophoto -inputFiles {models} '
                       '-outputFile {ortho} -resolution {res} {verbose} '
                       '-outputCornerFile {corners}'.format(**kwargs))

            utm_east_offset, utm_north_offset = outputs["utm_offset"]
            proj4_srs = outputs["utm_srs"].to_proj4()

            ulx = uly = lrx = lry = 0.0
            with open(orthophoto_corners_file) as f:
                for lineNumber, line in enumerate(f):
                    if lineNumber == 0:
                        tokens = line.split(' ')
                        if len(tokens) == 4:
                            ulx = float(tokens[0]) + utm_east_offset
                            lry = float(tokens[1]) + utm_north_offset
                            lrx = float(tokens[2]) + utm_east_offset
                            uly = float(tokens[3]) + utm_north_offset
                log.ODM_INFO('Creating GeoTIFF')

                orthophoto_vars = orthophoto.get_orthophoto_vars(args)

                kwargs = {
                    'ulx': ulx,
                    'uly': uly,
                    'lrx': lrx,
                    'lry': lry,
                    'vars': ' '.join(['-co %s=%s' % (k, orthophoto_vars[k]) for k in orthophoto_vars]),
                    'proj': proj4_srs,
                    'input': orthophoto_render_file,
                    'output': orthophoto_file,
                    'max_memory': get_max_memory(),
                }

                system.run('gdal_translate -a_ullr {ulx} {uly} {lrx} {lry} '
                           '{vars} '
                           '-a_srs \"{proj}\" '
                           '--config GDAL_CACHEMAX {max_memory}% '
                           '--config GDAL_TIFF_INTERNAL_MASK YES '
                           '{input} {output}'.format(**kwargs))

                #orthophoto.post_orthophoto_steps(args, bounds_file_path, tree.odm_orthophoto_tif)
        else:
            log.ODM_WARNING('Found a valid orthophoto in: %s' % orthophoto_file)

