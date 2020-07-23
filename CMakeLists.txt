cmake_minimum_required(VERSION 3.0)
project(nodecolmap)

include(ExternalProject)

ExternalProject_Add(ceres
  URL               http://ceres-solver.org/ceres-solver-1.14.0.tar.gz
  UPDATE_COMMAND    ""
  CMAKE_ARGS
    -DCMAKE_C_FLAGS=-fPIC
    -DCMAKE_CXX_FLAGS=-fPIC
    -DBUILD_EXAMPLES=OFF
    -DBUILD_TESTING=OFF
)

ExternalProject_Add(colmap
  DEPENDS           ceres
  GIT_REPOSITORY    https://github.com/colmap/colmap/
  GIT_TAG           f2ce5f58e1593ceef8912b55c30a049bd4d24b33
  UPDATE_COMMAND    ""
  CMAKE_ARGS -DCGAL_ENABLED=OFF
             -DCUDA_ENABLED=ON
)

ExternalProject_Add(dem2mesh
    GIT_REPOSITORY    https://github.com/OpenDroneMap/dem2mesh.git
    GIT_TAG           master
    SOURCE_DIR        ${SB_SOURCE_DIR}/dem2mesh
    UPDATE_COMMAND    ""
    BUILD_IN_SOURCE 1
    BUILD_COMMAND     make -j8
    INSTALL_COMMAND   ""
)

ExternalProject_Add(mvs-texturing
  GIT_REPOSITORY    https://github.com/OpenDroneMap/mvs-texturing
  GIT_TAG           099
  UPDATE_COMMAND    ""
  CMAKE_ARGS
    -DRESEARCH=OFF
    -DCMAKE_BUILD_TYPE:STRING=Release
)

ExternalProject_Add(zstd
  GIT_REPOSITORY  https://github.com/facebook/zstd
  GIT_TAG         b84274da0f641907dfe472d5da132d872202e9b8
  CONFIGURE_COMMAND ${CMAKE_COMMAND} -DZSTD_BUILD_PROGRAMS=OFF -DCMAKE_BUILD_TYPE:STRING=Release
        <SOURCE_DIR>/build/cmake
)

ExternalProject_Add(hexer
  URL               https://github.com/hobu/hexer/archive/bc748fc16b51c562f68f6641574b7af4244adfa2.tar.gz
  UPDATE_COMMAND    ""
)

set(_proj_name laszip)
set(_SB_BINARY_DIR "${SB_BINARY_DIR}/${_proj_name}")

ExternalProject_Add(laszip
  URL               https://github.com/LASzip/LASzip/archive/0069c42307183c49744f1eb170f7032a8cf6a9db.zip
  UPDATE_COMMAND    ""
  CMAKE_ARGS
    -DBUILD_SHARED_LIBS=ON
    -DBUILD_STATIC_LIBS=OFF
    -DCMAKE_INSTALL_LIBDIR=lib
)

ExternalProject_Add(pdal
  DEPENDS           zstd hexer laszip
  URL               https://github.com/PDAL/PDAL/archive/2.1.0.zip
  CMAKE_ARGS
    -DBUILD_PGPOINTCLOUD_TESTS=OFF
    -DBUILD_PLUGIN_PGPOINTCLOUD=OFF
    -DBUILD_PLUGIN_CPD=OFF
    -DBUILD_PLUGIN_GREYHOUND=OFF
    -DBUILD_PLUGIN_HEXBIN=ON
    -DBUILD_PLUGIN_ICEBRIDGE=OFF
    -DBUILD_PLUGIN_MRSID=OFF
    -DBUILD_PLUGIN_NITF=OFF
    -DBUILD_PLUGIN_OCI=OFF
    -DBUILD_PLUGIN_P2G=OFF
    -DBUILD_PLUGIN_SQLITE=OFF
    -DBUILD_PLUGIN_RIVLIB=OFF
    -DBUILD_PLUGIN_PYTHON=OFF
    -DWITH_ZSTD=ON
    -DENABLE_CTEST=OFF
    -DWITH_APPS=ON
    -DWITH_LAZPERF=OFF
    -DWITH_GEOTIFF=ON
    -DWITH_LASZIP=ON
    -DLASZIP_FOUND=TRUE
    -DLASZIP_LIBRARIES=/usr/local/lib/liblaszip.so
    -DLASZIP_VERSION=3.1.1
    -DLASZIP_INCLUDE_DIR=/usr/local/include
    -DLASZIP_LIBRARY=/usr/local/lib/liblaszip.so
    -DWITH_TESTS=OFF
    -DCMAKE_BUILD_TYPE=Release
)

ExternalProject_Add(pcl
    URL               https://github.com/OpenDroneMap/pcl/archive/master.zip
    UPDATE_COMMAND    ""
    CMAKE_ARGS
    -DBUILD_features=OFF
    -DBUILD_filters=OFF
    -DBUILD_geometry=OFF
    -DBUILD_keypoints=OFF
    -DBUILD_outofcore=OFF
    -DBUILD_people=OFF
    -DBUILD_recognition=OFF
    -DBUILD_registration=OFF
    -DBUILD_sample_consensus=OFF
    -DBUILD_segmentation=OFF
    -DBUILD_features=OFF
    -DBUILD_surface_on_nurbs=OFF
    -DBUILD_tools=OFF
    -DBUILD_tracking=OFF
    -DBUILD_visualization=OFF
    -DWITH_QT=OFF
    -DBUILD_OPENNI=OFF
    -DBUILD_OPENNI2=OFF
    -DWITH_OPENNI=OFF
    -DWITH_OPENNI2=OFF
    -DWITH_FZAPI=OFF
    -DWITH_LIBUSB=OFF
    -DWITH_PCAP=OFF
    -DWITH_PXCAPI=OFF
    -DCMAKE_BUILD_TYPE=Release
    -DPCL_VERBOSITY_LEVEL=Error
)

ExternalProject_Add(opencv
  URL               https://github.com/opencv/opencv/archive/3.4.6.zip
  UPDATE_COMMAND    ""
  CMAKE_ARGS
    -DBUILD_opencv_core=ON
    -DBUILD_opencv_imgproc=ON
    -DBUILD_opencv_highgui=ON
    -DBUILD_opencv_video=ON
    -DBUILD_opencv_ml=ON
    -DBUILD_opencv_features2d=ON
    -DBUILD_opencv_calib3d=ON
    -DBUILD_opencv_contrib=OFF
    -DBUILD_opencv_flann=ON
    -DBUILD_opencv_objdetect=ON
    -DBUILD_opencv_photo=ON
    -DBUILD_opencv_legacy=ON
    -DBUILD_opencv_python=ON
    -DWITH_FFMPEG=OFF
    -DWITH_CUDA=OFF
    -DWITH_GTK=OFF
    -DWITH_VTK=OFF
    -DWITH_EIGEN=OFF
    -DWITH_OPENNI=OFF
    -DBUILD_EXAMPLES=OFF
    -DBUILD_TESTS=OFF
    -DBUILD_PERF_TESTS=OFF
    -DBUILD_DOCS=OFF
    -DBUILD_opencv_apps=OFF
    -DBUILD_opencv_gpu=OFF
    -DBUILD_opencv_videostab=OFF
    -DBUILD_opencv_nonfree=OFF
    -DBUILD_opencv_stitching=OFF
    -DBUILD_opencv_world=OFF
    -DBUILD_opencv_superres=OFF
    -DBUILD_opencv_java=OFF
    -DBUILD_opencv_ocl=OFF
    -DBUILD_opencv_ts=OFF
    -DBUILD_opencv_xfeatures2d=OFF
    -DCMAKE_BUILD_TYPE:STRING=Release
)


