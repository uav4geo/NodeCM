import os

from opendm import log
from opendm import io
from opendm import system
from opendm import types
from opendm.osfm import OSFMContext
from opendm.gpu import has_gpus

class ODMColmapDenseStage(types.ODM_Stage):
    def process(self, args, outputs):
        # get inputs
        tree = outputs['tree']
        reconstruction = outputs['reconstruction']
        photos = reconstruction.photos

        if not has_gpus():
            log.ODM_ERROR("Cannot execute colmap dense without GPUs")
            exit(1)

        if not photos:
            log.ODM_ERROR('Not enough photos in photos array to start colmap')
            exit(1)

        # check if reconstruction was done before
        # if not io.file_exists(tree.mve_model) or self.rerun():
            
            self.update_progress(90)

            
            # if args.optimize_disk_space:
            #     shutil.rmtree(tree.mve_views)
        # else:
        #     log.ODM_WARNING('Found a valid colmap reconstruction file in: %s' %
        #                     tree.mve_model)
