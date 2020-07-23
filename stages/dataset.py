import os
import json

from opendm import io
from opendm import log
from opendm import system
from opendm import progress
from opendm.stage import Stage


class DatasetStage(Stage):
    def process(self, args, outputs):
        log.ODM_INFO("Project path: %s" % args.project_path)

        images_dir = io.join_paths(args.project_path, 'images')
        log.ODM_INFO("Images dir: %s" % images_dir)

        if not os.path.exists(images_dir):
            log.ODM_ERROR("No images found in %s, exiting..." % images_dir)
            exit(1)

        # create output directories (match ODM conventions for compatibility)
        odm_dirs = ['odm_orthophoto', 'odm_dem', 'odm_georeferencing']

        for odm_dir in odm_dirs:
            system.mkdir_p(io.join_paths(project_dir, odm_dir))

        # for ext in ["JPG", "jpg", "TIFF", "tif"]:
        # image_wildcard = '*.{}'.format(image_ext)
        # image_files = glob.glob(io.join_paths(images_dir, image_wildcard))
        # image_files.sort(key=lambda f: int(filter(str.isdigit, f)))


            # image_ext = get_image_type()
            # projection = get_projection(image_ext)

            # log.ODM_INFO(image_ext)
            # log.ODM_INFO(projection)

            # apply srs and geo projection to DEM (UTM) and write to odm_dem/
            # gdal_translate(proj_str,
            #                io.join_paths(images_dir, get_last_etape('MEC-Malt/Z_Num*_DeZoom{}*.tif'.format(args.zoom))),
            #                io.join_paths(project_dir, 'odm_dem/dsm.tif'))
            
            # progressbc.send_update(100)

            exit(0)



        #outputs['images'] = images



# def get_projection(image_type):
#     '''
#     Generate EXIF data, utm zone and hemisphere.
#     :param image_type:
#     :return: utm_zone, hemisphere
#     '''
#     Image = namedtuple('Image', ['image', 'point', 'altitude'])

#     kwargs = {
#         'image_type': image_type
#     }

#     system.run('exiftool -filename -gpslongitude -gpslatitude -gpsaltitude '
#                '-T -n *.{image_type} > imageEXIF.txt'.format(**kwargs))

#     with open('imageEXIF.txt', 'r') as f:
#         lines = (l.split('\t') for l in f.readlines())
#         coords = [Image(image=l[0].strip(),
#                         point=Point(float(l[1]), float(l[2])),
#                         altitude=l[3].strip())
#                   for l in lines]

#     p = Point(coords[0][1])
#     u = utm.from_latlon(p.y, p.x)
#     utm_zone = u[2]
#     hemisphere = "north" if p.y > 0 else "south"

#     log.ODM_INFO('UTM - %s' % utm_zone)
#     log.ODM_INFO('Hemisphere - %s' % hemisphere)

#     return {'utm_zone': utm_zone, 'hemisphere': hemisphere}


# def gdal_translate(proj_str, src, dst):
#     '''
#     Execute gdal_translate
#     :param proj_str: projection string
#     :param src: input tif
#     :param dst: output tif
#     :return:
#     '''
#     kwargs = {
#         'tiled': '-co TILED=yes',
#         'compress': 'LZW',
#         'predictor': '-co PREDICTOR=2',
#         'proj': proj_str,
#         'bigtiff': 'YES',
#         'src': src,
#         'dst': dst,
#         'max_memory': 2048,
#         'threads': args.max_concurrency
#     }

#     system.run('gdal_translate '
#         '{tiled} '
#         '-co BIGTIFF={bigtiff} '
#         '-co COMPRESS={compress} '
#         '{predictor} '
#         '-co BLOCKXSIZE=512 '
#         '-co BLOCKYSIZE=512 '
#         '-co NUM_THREADS={threads} '
#         '-a_srs \"{proj}\" '
#         '--config GDAL_CACHEMAX {max_memory} '
#         '{src} {dst}'.format(**kwargs))