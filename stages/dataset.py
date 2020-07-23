import os
import glob

from opendm import io
from opendm import log
from opendm import system
from opendm import progress
from opendm.stage import Stage

from app.colmap import ColmapContext
from app import fs

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
        odm_dirs = ['odm_orthophoto', 'odm_dem', 'odm_georeferencing']

        for odm_dir in odm_dirs:
            system.mkdir_p(os.path.join(args.project_path, odm_dir))

        if not os.path.exists(outputs["image_list_file"]) or self.rerun():
            image_files = []

            # Create image list
            for ext in ["JPG", "JPEG", "TIF", "TIFF", "jpg", "jpeg", "tif", "tiff"]:
                image_wildcard = '*.{}'.format(ext)
                image_files += map(os.path.basename, glob.glob(os.path.join(outputs["images_dir"], image_wildcard)))

            with open(outputs["image_list_file"], "w") as f:
                for image in image_files:
                    f.write(image + "\n")
