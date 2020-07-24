import os
import glob
import json

from opendm import io
from opendm import log
from opendm import system
from opendm import progress
from opendm.stage import Stage
from opendm.photo import ODM_Photo
from opendm.location import extract_utm_coords

from app.colmap import ColmapContext
from app import fs

def save_images_database(photos, database_file):
    with open(database_file, 'w') as f:
        f.write(json.dumps(map(lambda p: p.__dict__, photos)))
    
    log.ODM_INFO("Wrote images database: %s" % database_file)

def load_images_database(database_file):
    # Empty is used to create ODM_Photo class
    # instances without calling __init__
    class Empty:
        pass

    result = []

    log.ODM_INFO("Loading images database: %s" % database_file)

    with open(database_file, 'r') as f:
        photos_json = json.load(f)
        for photo_json in photos_json:
            p = Empty()
            for k in photo_json:
                setattr(p, k, photo_json[k])
            p.__class__ = ODM_Photo
            result.append(p)

    return result

class DatasetStage(Stage):
    def process(self, args, outputs):
        log.ODM_INFO("Project path: %s" % args.project_path)

        outputs["project_path"] = args.project_path
        outputs["images_dir"] = os.path.join(args.project_path, 'images')
        outputs["image_list_file"] = os.path.join(outputs["project_path"], "image_list.txt")
        outputs["cm"] = ColmapContext(args.project_path)
        
        log.ODM_INFO("Images dir: %s" % outputs["images_dir"])

        if not os.path.exists(outputs["images_dir"]):
            log.ODM_ERROR("No images found in %s, exiting..." % outputs["images_dir"])
            exit(1)

        # create output directories (match ODM conventions for compatibility)
        odm_dirs = ['odm_orthophoto', 'odm_meshing', 'odm_texturing', 'odm_dem', 'odm_georeferencing']

        for odm_dir in odm_dirs:
            system.mkdir_p(os.path.join(args.project_path, odm_dir))

        images_database_file = io.join_paths(args.project_path, 'images.json')
        if not io.file_exists(images_database_file) or self.rerun():
            files = []
            for ext in ["JPG", "JPEG", "TIF", "TIFF", "jpg", "jpeg", "tif", "tiff"]:
                image_wildcard = '*.{}'.format(ext)
                files += glob.glob(os.path.join(outputs["images_dir"], image_wildcard))

            if files:
                photos = []
                with open(outputs["image_list_file"], 'w') as image_list:
                    log.ODM_INFO("Loading %s images" % len(files))
                    for f in files:
                        photos += [ODM_Photo(f)]
                        image_list.write(photos[-1].filename + '\n')

                # Save image database for faster restart
                save_images_database(photos, images_database_file)
            else:
                log.ODM_ERROR('Not enough supported images in %s' % images_dir)
                exit(1)
        else:
            # We have an images database, just load it
            photos = load_images_database(images_database_file)

        log.ODM_INFO('Found %s usable images' % len(photos))

        if len(photos) == 0:
            log.ODM_ERROR("No images found (JPG or TIFF). Check that you placed some images in the images/ directory.")
            exit(1)

        utm_coords_file = os.path.join(args.project_path, "utm_coords.txt")
        if not os.path.exists(utm_coords_file) or self.rerun():
            extract_utm_coords(photos, outputs["images_dir"], utm_coords_file)
        else:
            log.ODM_WARNING("Found existing %s" % utm_coords_file)

        outputs["photos"] = photos
        outputs["utm_coords_file"] = utm_coords_file







