import os
import json

from opendm import io
from opendm import log
from opendm import system
from opendm import progress
from opendm.stage import Stage
from opendm.gpu import has_gpus

from app import fs

class FeaturesStage(Stage):
    def process(self, args, outputs):
        cm = outputs["cm"]
        outputs["db_path"] = os.path.join(outputs["project_path"], "database.db")

        features_done = os.path.join(outputs["project_path"], "features_done.txt")

        if not os.path.exists(features_done) or self.rerun():
            kwargs = {}
            kwargs['SiftExtraction.max_image_size'] = args.resize_to
            kwargs['ImageReader.camera_model'] = args.camera_model.upper()
            
            if not has_gpus():
                log.ODM_WARNING("No GPUs detected, computing SIFT on CPU")
                kwargs['SiftExtraction.use_gpu'] = 'false'

            cm.run("feature_extractor", database_path=outputs["db_path"],
                                        image_path=outputs["images_dir"],
                                        image_list_path=outputs["image_list_file"],
                                        **kwargs)
            fs.touch(features_done)


class MatchingStage(Stage):
    def process(self, args, outputs):
        cm = outputs["cm"]

        matching_done = os.path.join(outputs["project_path"], "matching_done.txt")
        if not os.path.exists(matching_done) or self.rerun():
            kwargs = {}

            if args.matcher_neighbors <= 0 and args.matcher_distance <= 0:
                log.ODM_INFO("Using exhaustive matcher")
                matcher_type = "exhaustive_matcher"
            else:
                matcher_type = "spatial_matcher"
                kwargs["SpatialMatching.max_num_neighbors"] = args.matcher_neighbors if args.matcher_neighbors > 0 else 9999999
                kwargs["SpatialMatching.max_distance"] = args.matcher_distance if args.matcher_distance > 0 else 9999999
            
            if not has_gpus():
                log.ODM_WARNING("No GPUs detected, computing SIFT on CPU")
                kwargs['SiftMatching.use_gpu'] = 'false'

            cm.run(matcher_type, database_path=outputs["db_path"],
                                **kwargs)
            fs.touch(matching_done)