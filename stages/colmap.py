import os
import json
import shutil
import math

from opendm import io
from opendm import log
from opendm import system
from opendm import progress
from opendm.stage import Stage
from opendm.gpu import has_gpus

from app.get_image_size import get_image_size
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


class SparseStage(Stage):
    def process(self, args, outputs):
        cm = outputs["cm"]
        outputs["sparse_dir"] = os.path.join(outputs["project_path"], "sparse")
        if not os.path.exists(outputs["sparse_dir"]):
            system.mkdir_p(outputs["sparse_dir"])

        sparse_dir_empty = len(os.listdir(outputs["sparse_dir"])) == 0
        if sparse_dir_empty or self.rerun():
            kwargs = {}

            # TODO: Expose some useful parameters here...

            # TODO: use hierarchical_mapper for larger datasets

            cm.run("mapper", database_path=outputs["db_path"],
                             image_path=outputs["images_dir"],
                             output_path=outputs["sparse_dir"],
                             log_level=1,
                             **kwargs)

        outputs["sparse_reconstruction_dirs"] = list(map(lambda p: os.path.join(outputs["sparse_dir"], p), os.listdir(outputs["sparse_dir"])))

        if len(outputs["sparse_reconstruction_dirs"]) == 0:
            log.ODM_ERROR("The program could not process this dataset using the current settings. "
                            "Check that the images have enough overlap, "
                            "that there are enough recognizable features "
                            "and that the images are in focus. "
                            "The program will now exit.")
            exit(1)

class DenseStage(Stage):
    def process(self, args, outputs):
        cm = outputs["cm"]

        # TODO: handle multiple reconstructions
        if len(outputs["sparse_reconstruction_dirs"]) > 1:
            log.ODM_WARNING("Multiple reconstructions found. We will only reconstruct the first. "
                            "Part of your dataset might not be reconstructed")
        
        reconstruction_dir = outputs["sparse_reconstruction_dirs"][0]
        
        # Create dense dir
        outputs["dense_dir"] = os.path.join(outputs["project_path"], "dense")
        if not os.path.exists(outputs["dense_dir"]):
            system.mkdir_p(outputs["dense_dir"])

        if not has_gpus():
            output_type = "PMVS"
            outputs["dense_workspace_dir"] = os.path.join(outputs["dense_dir"], "pmvs")
        else:
            output_type = "COLMAP"
            raise Error("TODO!")
            outputs["dense_workspace_dir"] = os.path.join(outputs["dense_dir"], "colmap")  #?

        if not os.path.exists(outputs["dense_workspace_dir"]) or self.rerun():
            log.ODM_INFO("Undistorting images using a %s workspace" % output_type.lower())

            # Undistort images
            # cm.run("image_undistorter", image_path=outputs["images_dir"],
            #                             input_path=reconstruction_dir,
            #                             output_path=outputs["dense_dir"],
            #                             output_type=output_type)

        if output_type == "COLMAP":
            outputs["point_cloud_ply_file"] = "TODO"
        else:
            outputs["dense_mve_dir"] = os.path.join(outputs["dense_workspace_dir"], "mve")
            outputs["point_cloud_ply_file"] = os.path.join(outputs["dense_mve_dir"], "TODO!")

        if not os.path.exists(outputs["point_cloud_ply_file"]) or self.rerun():
            if output_type == "COLMAP":
                kwargs = {
                    'PatchMatchStereo.geom_consistency': 'true'
                }

                cm.run("patch_match_stereo", workspace_path=outputs["dense_workspace_dir"],
                                            workspace_format="COLMAP",
                                            **kwargs)
            else:
                # Use MVE

                # 1. Create directory structure so makescene is happy...
                if os.path.exists(outputs["dense_mve_dir"]) and self.rerun():
                    log.ODM_WARNING("Removing %s" % outputs["dense_mve_dir"])
                    shutil.rmtree(outputs["dense_mve_dir"])

                bundler_dir = os.path.join(outputs["dense_workspace_dir"], "bundler")
                bundle_dir = os.path.join(bundler_dir, "bundle")
                if os.path.exists(outputs["dense_mve_dir"]) and self.rerun():
                    log.ODM_WARNING("Removing %s" % bundle_dir)
                    shutil.rmtree(bundle_dir)
                
                # Create dense/pmvs/bundle
                system.mkdir_p(bundle_dir)

                bundle_rd_out_file = os.path.join(outputs["dense_workspace_dir"], "bundle.rd.out")
                bundle_image_list = os.path.join(outputs["dense_workspace_dir"], "bundle.rd.out.list.txt")

                # Copy bundle.rd.out --> bundler/bundle/bundle.out
                shutil.copy(bundle_rd_out_file, os.path.join(bundle_dir, "bundle.out"))

                # Read image list
                with open(bundle_image_list, "r") as f:
                    images = filter(len, map(str.strip, f.read().split("\n")))
                
                visualize = os.listdir(os.path.join(outputs["dense_workspace_dir"], "visualize"))
                visualize.sort()
                visualize = [os.path.join(outputs["dense_workspace_dir"], "visualize", v) for v in visualize]

                # Copy each image from visualize/########N{8}.jpg to bundle/images[N]
                # TODO: check tiff extensions?
                for i, src in enumerate(visualize):
                    dst = os.path.join(bundler_dir, images[i])
                    log.ODM_INFO("Copying %s --> %s" % (os.path.basename(src), os.path.basename(dst)))

                    # Could make it faster by moving, but then we mess up the structure...
                    shutil.copy(src, dst)
                
                # Copy image list (bundle.rd.out.list.txt --> bundler/list.txt)
                shutil.copy(bundle_image_list, os.path.join(bundler_dir, "list.txt"))

                # Run makescene
                if os.path.exists(outputs["dense_mve_dir"]):
                    log.ODM_WARNING("Removing %s" % outputs["dense_mve_dir"])
                    shutil.rmtree(outputs["dense_mve_dir"])

                system.run("makescene \"{}\" \"{}\"".format(bundler_dir, outputs["dense_mve_dir"]))

                # Read image dimension
                # TODO: this can be improved, see below
                width, height = get_image_size(os.path.join(bundler_dir, images[0]))
                log.ODM_INFO("Image dimensions: (%s, %s)" % (width, height))
                size = max(width, height)

                max_pixels = args.depthmap_resolution * args.depthmap_resolution
                if size * size <= max_pixels:
                    mve_output_scale = 0
                else:
                    ratio = float(size* size) / float(max_pixels)
                    mve_output_scale = int(math.ceil(math.log(ratio) / math.log(4.0)))

                # TODO: we don't have a limit on undistortion dimensions
                # Compute mve output scale based on depthmap_resolution
                #max_pixels = args.depthmap_resolution * args.depthmap_resolution
                # if outputs['undist_image_max_size'] * outputs['undist_image_max_size'] <= max_pixels:
                #     mve_output_scale = 0
                # else:
                #     ratio = float(outputs['undist_image_max_size'] * outputs['undist_image_max_size']) / float(max_pixels)
                #     mve_output_scale = int(math.ceil(math.log(ratio) / math.log(4.0)))

                dmrecon_config = [
                    "-s%s" % mve_output_scale,
                    "--progress=fancy",
                    "--local-neighbors=2",
                ]

                # Run MVE's dmrecon
                log.ODM_INFO("Running dense reconstruction. This might take a while.")
            
                # TODO: find out why MVE is crashing at random
                # MVE *seems* to have a race condition, triggered randomly, regardless of dataset
                # https://gist.github.com/pierotofy/6c9ce93194ba510b61e42e3698cfbb89
                # Temporary workaround is to retry the reconstruction until we get it right
                # (up to a certain number of retries).
                retry_count = 1
                while retry_count < 10:
                    try:
                        system.run('dmrecon %s "%s"' % (' '.join(dmrecon_config), outputs["dense_mve_dir"]))
                        break
                    except Exception as e:
                        if str(e) == "Child returned 134" or str(e) == "Child returned 1":
                            retry_count += 1
                            log.ODM_WARNING("Caught error code, retrying attempt #%s" % retry_count)
                        else:
                            raise e

            # TODO: stereo fusion

            
            # cm.run("mapper", database_path=outputs["db_path"],
            #                  image_path=outputs["images_dir"],
            #                  output_path=outputs["sparse_dir"],
            #                  log_level=1,
            #                  **kwargs)

            # fs.touch(sparse_done)