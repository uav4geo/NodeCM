import os
import shutil
from opendm import io
from opendm import log
from opendm import system
from opendm import progress
from opendm.stage import Stage

class TextureStage(Stage):
    def process(self, args, outputs):
        cm = outputs["cm"]

        texturing_dir = os.path.join(args.project_path, "odm_texturing")
        nvm_file = os.path.join(outputs["undistorted_dir"], "recon.nvm")

        # Export reconstruction to NVM
        if not os.path.exists(nvm_file) or self.rerun():
            cm.run("model_converter", input_path=outputs["georeconstruction_dir"],
                                      output_path=nvm_file,
                                      output_type="NVM")

        if not io.dir_exists(texturing_dir):
            system.mkdir_p(texturing_dir)

        textured_model_obj = os.path.join(texturing_dir, "odm_textured_model_geo.obj")

        if not io.file_exists(textured_model_obj) or self.rerun():
            log.ODM_INFO('Writing MVS Textured file in: %s'% textured_model_obj)

            # Format arguments to fit Mvs-Texturing app
            skipGeometricVisibilityTest = ""
            skipGlobalSeamLeveling = ""
            skipLocalSeamLeveling = ""
            skipHoleFilling = ""
            keepUnseenFaces = ""
            nadir = ""

            if (args.texturing_skip_visibility_test):
                skipGeometricVisibilityTest = "--skip_geometric_visibility_test"
            if (args.texturing_skip_global_seam_leveling):
                skipGlobalSeamLeveling = "--skip_global_seam_leveling"
            if (args.texturing_skip_local_seam_leveling):
                skipLocalSeamLeveling = "--skip_local_seam_leveling"
            if (args.texturing_skip_hole_filling):
                skipHoleFilling = "--skip_hole_filling"
            if (args.texturing_keep_unseen_faces):
                keepUnseenFaces = "--keep_unseen_faces"
            
            nadir = '--nadir_mode'

            # mvstex definitions
            kwargs = {
                'out_file': os.path.join(texturing_dir, "odm_textured_model_geo"),
                'model': outputs["mesh_file"],
                'dataTerm': args.texturing_data_term,
                'outlierRemovalType': args.texturing_outlier_removal_type,
                'skipGeometricVisibilityTest': skipGeometricVisibilityTest,
                'skipGlobalSeamLeveling': skipGlobalSeamLeveling,
                'skipLocalSeamLeveling': skipLocalSeamLeveling,
                'skipHoleFilling': skipHoleFilling,
                'keepUnseenFaces': keepUnseenFaces,
                'toneMapping': args.texturing_tone_mapping,
                'nadirMode': nadir,
                'nadirWeight': 2 ** args.texturing_nadir_weight - 1,
                'nvm_file': nvm_file
            }

            mvs_tmp_dir = os.path.join(texturing_dir, 'tmp')

            # Make sure tmp directory is empty
            if os.path.exists(mvs_tmp_dir):
                log.ODM_INFO("Removing old tmp directory {}".format(mvs_tmp_dir))
                shutil.rmtree(mvs_tmp_dir)

            # run texturing binary
            system.run('texrecon {nvm_file} {model} {out_file} '
                    '-d {dataTerm} -o {outlierRemovalType} '
                    '-t {toneMapping} '
                    '{skipGeometricVisibilityTest} '
                    '{skipGlobalSeamLeveling} '
                    '{skipLocalSeamLeveling} '
                    '{skipHoleFilling} '
                    '{keepUnseenFaces} '
                    '{nadirMode} '
                    '-n {nadirWeight}'.format(**kwargs))
                
        else:
            log.ODM_WARNING('Found a valid ODM Texture file in: %s' % textured_model_obj)
        
        outputs["textured_model_obj"] = textured_model_obj