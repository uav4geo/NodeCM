import argparse
import json
import sys
import os
from opendm import io
from opendm import log

with open(os.path.join(os.path.dirname(__file__), '..', 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

# parse arguments
processopts = ['dataset', 'features', 'matching', 'sparse', 'georegister', 'dense', 'georeferencing', 'dem', 'mesh', 'texture', 'ortho']

class RerunFrom(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, processopts[processopts.index(values):])
        setattr(namespace, self.dest + '_is_set', True)

class StoreTrue(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)
        setattr(namespace, self.dest + '_is_set', True)

class StoreValue(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest + '_is_set', True)

parser = argparse.ArgumentParser(prog='run.py',
                        usage='%(prog)s [options] <project>')
args = None

def config(argv=None):
    global args

    if args is not None and argv is None:
        return args
    
    parser.add_argument('project',
                        metavar='<path>',
                        action=StoreValue,
                        nargs='?',
                        help='Path to the project folder or name of the project in a workspace (when using --project-path)')

    parser.add_argument('--project-path',
                        metavar='<path>',
                        action=StoreValue,
                        help='Path to the workspace folder (for compatibility with ODM)')

    parser.add_argument('--resize-to',
                        metavar='<integer>',
                        action=StoreValue,
                        default=2048,
                        type=int,
                        help='Resizes images by the largest side for feature extraction purposes only. '
                             'Set to -1 to disable. This does not affect the final orthophoto '
                             ' resolution quality and will not resize the original images. Default:  %(default)s')

    parser.add_argument('--mesh-octree-depth',
                    metavar='<positive integer>',
                    action=StoreValue,
                    default=10,
                    type=int,
                    help=('Oct-tree depth used in the mesh reconstruction, '
                            'increase to get more vertices, recommended '
                            'values are 8-12. Default: %(default)s'))

    parser.add_argument('--mesh-size',
                        metavar='<positive integer>',
                        action=StoreValue,
                        default=200000,
                        type=int,
                        help=('The maximum vertex count of the output mesh. '
                              'Default: %(default)s'))

    parser.add_argument('--matcher-neighbors',
                        metavar='<integer>',
                        action=StoreValue,
                        default=8,
                        type=int,
                        help='Number of nearest images to pre-match based on GPS '
                             'exif data. Set to 0 to skip pre-matching. '
                             'Neighbors works together with Distance parameter, '
                             'set both to 0 to not use pre-matching. OpenSFM '
                             'uses both parameters at the same time, Bundler '
                             'uses only one which has value, prefering the '
                             'Neighbors parameter. Default: %(default)s')

    parser.add_argument('--matcher-distance',
                        metavar='<integer>',
                        action=StoreValue,
                        default=0,
                        type=int,
                        help='Distance threshold in meters to find pre-matching '
                             'images based on GPS exif data. Set both '
                             'matcher-neighbors and this to 0 to skip '
                             'pre-matching. Default: %(default)s')

    parser.add_argument('--depthmap-resolution',
                        metavar='<positive float>',
                        action=StoreValue,
                        type=float,
                        default=640,
                        help=('Controls the density of the point cloud by setting the resolution of the depthmap images. Higher values take longer to compute '
                              'but produce denser point clouds. '
                              'Default: %(default)s'))

    parser.add_argument('--end-with', '-e',
                        metavar='<string>',
                        action=StoreValue,
                        default='odm_report',
                        choices=processopts,
                        help=('Can be one of:' + ' | '.join(processopts)))

    rerun = parser.add_mutually_exclusive_group()

    rerun.add_argument('--rerun', '-r',
                       metavar='<string>',
                       action=StoreValue,
                       choices=processopts,
                       help=('Can be one of:' + ' | '.join(processopts)))

    rerun.add_argument('--rerun-all',
                       action=StoreTrue,
                       nargs=0,
                       default=False,
                       help='force rerun of all tasks')

    rerun.add_argument('--rerun-from',
                       action=RerunFrom,
                       metavar='<string>',
                       choices=processopts,
                       help=('Can be one of:' + ' | '.join(processopts)))

    # parser.add_argument('--min-num-features',
    #                     metavar='<integer>',
    #                     action=StoreValue,
    #                     default=8000,
    #                     type=int,
    #                     help=('Minimum number of features to extract per image. '
    #                           'More features leads to better results but slower '
    #                           'execution. Default: %(default)s'))
    
    # parser.add_argument('--crop',
    #                 metavar='<positive float>',
    #                 action=StoreValue,
    #                 default=3,
    #                 type=float,
    #                 help=('Automatically crop image outputs by creating a smooth buffer '
    #                       'around the dataset boundaries, shrinked by N meters. '
    #                       'Use 0 to disable cropping. '
    #                       'Default: %(default)s'))

    
    parser.add_argument('--camera-model',
                        metavar='<string>',
                        action=StoreValue,
                        default='simple_radial',
                        choices=['simple_radial', 'radial', 'simple_pinhole', 'pinhole', 'opencv', 'full_opencv', 'simple_radial_fisheye', 'radial_fisheye', 'opencv_fisheye', 'fov', 'thin_prism_fisheye'],
                        help=('Camera model: [simple_radial, radial, simple_pinhole, pinhole, opencv, full_opencv, simple_radial_fisheye, radial_fisheye, opencv_fisheye, fov, thin_prism_fisheye]. default: '
                              '%(default)s'))

    parser.add_argument('--mesher',
                        metavar='<string>',
                        action=StoreValue,
                        default='poisson',
                        choices=['poisson'], #TODO: add delaunay
                        help=('Mesher to use: [poisson]. default: '
                              '%(default)s'))

    parser.add_argument('--mve-confidence',
                    metavar='<float: 0 <= x <= 1>',
                    action=StoreValue,
                    type=float,
                    default=0.60,
                    help=('Discard points that have less than a certain confidence threshold. '
                            'This only affects dense reconstructions performed with MVE. '
                            'Higher values discard more points. '
                            'Default: %(default)s'))

    parser.add_argument('--texturing-data-term',
                        metavar='<string>',
                        action=StoreValue,
                        default='gmi',
                        choices=['gmi', 'area'],
                        help=('Data term: [area, gmi]. Default: '
                              '%(default)s'))

    parser.add_argument('--texturing-nadir-weight',
                        metavar='<integer: 0 <= x <= 32>',
                        action=StoreValue,
                        default=16,
                        type=int,
                        help=('Affects orthophotos only. '
                              'Higher values result in sharper corners, but can affect color distribution and blurriness. '
                              'Use lower values for planar areas and higher values for urban areas. '
                              'The default value works well for most scenarios. Default: '
                              '%(default)s'))

    parser.add_argument('--texturing-outlier-removal-type',
                        metavar='<string>',
                        action=StoreValue,
                        default='gauss_clamping',
                        choices=['none', 'gauss_clamping', 'gauss_damping'],
                        help=('Type of photometric outlier removal method: '
                              '[none, gauss_damping, gauss_clamping]. Default: '
                              '%(default)s'))

    parser.add_argument('--texturing-skip-visibility-test',
                        action=StoreTrue,
                        nargs=0,
                        default=False,
                        help=('Skip geometric visibility test. Default: '
                              ' %(default)s'))

    parser.add_argument('--texturing-skip-global-seam-leveling',
                        action=StoreTrue,
                        nargs=0,
                        default=False,
                        help=('Skip global seam leveling. Useful for IR data.'
                              'Default: %(default)s'))

    parser.add_argument('--texturing-skip-local-seam-leveling',
                        action=StoreTrue,
                        nargs=0,
                        default=False,
                        help='Skip local seam blending. Default:  %(default)s')

    parser.add_argument('--texturing-skip-hole-filling',
                        action=StoreTrue,
                        nargs=0,
                        default=False,
                        help=('Skip filling of holes in the mesh. Default: '
                              ' %(default)s'))

    parser.add_argument('--texturing-keep-unseen-faces',
                        action=StoreTrue,
                        nargs=0,
                        default=False,
                        help=('Keep faces in the mesh that are not seen in any camera. '
                              'Default:  %(default)s'))

    parser.add_argument('--texturing-tone-mapping',
                        metavar='<string>',
                        action=StoreValue,
                        choices=['none', 'gamma'],
                        default='none',
                        help='Turn on gamma tone mapping or none for no tone '
                             'mapping. Choices are  \'gamma\' or \'none\'. '
                             'Default: %(default)s ')

    # parser.add_argument('--gcp',
    #                     metavar='<path string>',
    #                     action=StoreValue,
    #                     default=None,
    #                     help=('path to the file containing the ground control '
    #                           'points used for georeferencing.  Default: '
    #                           '%(default)s. The file needs to '
    #                           'be on the following line format: \neasting '
    #                           'northing height pixelrow pixelcol imagename'))


    # parser.add_argument('--dtm',
    #                     action=StoreTrue,
    #                     nargs=0,
    #                     default=False,
    #                     help='Use this tag to build a DTM (Digital Terrain Model, ground only) using a simple '
    #                          'morphological filter. Check the --dem* and --smrf* parameters for finer tuning.')

    # parser.add_argument('--dsm',
    #                     action=StoreTrue,
    #                     nargs=0,
    #                     default=False,
    #                     help='Use this tag to build a DSM (Digital Surface Model, ground + objects) using a progressive '
    #                          'morphological filter. Check the --dem* parameters for finer tuning.')

    # parser.add_argument('--dem-gapfill-steps',
    #                     metavar='<positive integer>',
    #                     action=StoreValue,
    #                     default=3,
    #                     type=int,
    #                     help='Number of steps used to fill areas with gaps. Set to 0 to disable gap filling. '
    #                          'Starting with a radius equal to the output resolution, N different DEMs are generated with '
    #                          'progressively bigger radius using the inverse distance weighted (IDW) algorithm '
    #                          'and merged together. Remaining gaps are then merged using nearest neighbor interpolation. '
    #                          '\nDefault=%(default)s')

    parser.add_argument('--dem-resolution',
                        metavar='<float>',
                        action=StoreValue,
                        type=float,
                        default=5,
                        help='DSM resolution in cm / pixel. '
                             '\nDefault: %(default)s')

    # parser.add_argument('--dem-decimation',
    #                     metavar='<positive integer>',
    #                     action=StoreValue,
    #                     default=1,
    #                     type=int,
    #                     help='Decimate the points before generating the DEM. 1 is no decimation (full quality). '
    #                          '100 decimates ~99%% of the points. Useful for speeding up '
    #                          'generation.\nDefault=%(default)s')
    
    parser.add_argument('--orthophoto-resolution',
                        metavar='<float > 0.0>',
                        action=StoreValue,
                        default=5,
                        type=float,
                        help=('Orthophoto resolution in cm / pixel. Note that this value is capped by a ground sampling distance (GSD) estimate. To remove the cap, check --ignore-gsd also.\n'
                              'Default: %(default)s'))
    
    parser.add_argument('--orthophoto-png',
                    action=StoreTrue,
                    nargs=0,
                    default=False,
                    help='Set this parameter if you want to generate a PNG rendering of the orthophoto.\n'
                            'Default: %(default)s')

    parser.add_argument('--build-overviews',
                    action=StoreTrue,
                    nargs=0,
                    default=False,
                    help='Build orthophoto overviews using gdaladdo.')

    parser.add_argument('--verbose', '-v',
                        action=StoreTrue,
                        nargs=0,
                        default=False,
                        help='Print additional messages to the console\n'
                             'Default: %(default)s')

    parser.add_argument('--time',
                    action=StoreTrue,
                    nargs=0,
                    default=False,
                    help='Generates a benchmark file with runtime info\n'
                            'Default: %(default)s')

    parser.add_argument('--version',
                        action='version',
                        version='NodeCOLMAP {0}'.format(__version__),
                        help='Displays version number and exits. ')

    args = parser.parse_args(argv)

    if not args.project:
        parser.print_help()
        exit(1)

    if args.project_path:
        args.project_path = os.path.join(args.project_path, args.project)
    else:
        args.project_path = args.project
        
    return args
