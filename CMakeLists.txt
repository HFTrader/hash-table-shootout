cmake_minimum_required( VERSION 3.12 )

set( CMAKE_CXX_FLAGS_RELEASE_INIT "-O3 -march=native -DNDEBUG" CACHE STRING "" )
project( hash-map-shootout )

set( CMAKE_CXX_STANDARD 17 )

#############################################################################
# System installed sources
#############################################################################
find_library( LIBTCMALLOC NAMES tcmalloc_minimal libtcmalloc_minimal.so.4 )
if ( LIBTCMALLOC-NOTFOUND ) 
message( FATAL_ERROR "libtcmalloc not found ")
else()
link_libraries( ${LIBTCMALLOC} )
endif()
find_package(Python3 REQUIRED COMPONENTS Development )
find_package(Boost COMPONENTS container filesystem )
find_package(Qt5 REQUIRED COMPONENTS Core)
find_package(PkgConfig REQUIRED)
pkg_check_modules(glib REQUIRED IMPORTED_TARGET glib-2.0)
pkg_check_modules(kyotocabinet REQUIRED IMPORTED_TARGET kyotocabinet)
find_library ( LIBPFM_LIBRARY_FILE NAMES libpfm.a libpfm.so )
find_file( LIBPFM_INCLUDE_FILE NAMES perfmon/pfmlib.h )
if ( LIBPFM_LIBRARY_FILE-NOTFOUND OR LIBPFM_INCLUDE_FILE-NOTFOUND )
    set( LIBPFM-NOTFOUND ON )
else()
    cmake_path( GET LIBPFM_INCLUDE_FILE PARENT_PATH LIBPFM_INCLUDE_FILE )
    cmake_path( GET LIBPFM_INCLUDE_FILE PARENT_PATH LIBPFM_INCLUDE_DIR )
    add_library( libpfm INTERFACE IMPORTED GLOBAL )
    target_include_directories( libpfm INTERFACE ${LIBPFM_INCLUDE_DIR} )
    target_link_libraries( libpfm INTERFACE ${LIBPFM_LIBRARY_FILE} )
endif()

#############################################################################
# Locally installed sources
#############################################################################
include( FetchContent )
include( ExternalProject )
FetchContent_Declare( abseil-cpp         GIT_REPOSITORY https://github.com/abseil/abseil-cpp.git )
FetchContent_Declare( emilib             GIT_REPOSITORY https://github.com/emilk/emilib.git )
FetchContent_Declare( skarupke           GIT_REPOSITORY https://github.com/skarupke/flat_hash_map.git )
FetchContent_Declare( hopscotch-map      GIT_REPOSITORY https://github.com/Tessil/hopscotch-map.git )
FetchContent_Declare( ordered-map        GIT_REPOSITORY https://github.com/Tessil/ordered-map.git )
FetchContent_Declare( robin-map          GIT_REPOSITORY https://github.com/Tessil/robin-map.git )
FetchContent_Declare( sparse-map         GIT_REPOSITORY https://github.com/Tessil/sparse-map.git )
FetchContent_Declare( array-hash         GIT_REPOSITORY https://github.com/Tessil/array-hash.git )
FetchContent_Declare( sparsepp           GIT_REPOSITORY https://github.com/greg7mdp/sparsepp.git )
FetchContent_Declare( ordered-patch-map  GIT_REPOSITORY https://github.com/1ykos/ordered_patch_map )
FetchContent_Declare( libcuckoo          GIT_REPOSITORY https://github.com/efficient/libcuckoo.git )
FetchContent_Declare( bplus-tree         GIT_REPOSITORY https://github.com/berenm/bplus-tree.git GIT_TAG version/2.0.0 )
FetchContent_Declare( klibs              GIT_REPOSITORY https://github.com/attractivechaos/klib.git )
FetchContent_Declare( folly              GIT_REPOSITORY https://github.com/facebook/folly.git GIT_TAG main )
FetchContent_Declare( ankerl             GIT_REPOSITORY https://github.com/martinus/unordered_dense.git GIT_TAG main )
FetchContent_Declare( emhash             GIT_REPOSITORY https://github.com/ktprime/emhash.git )

FetchContent_MakeAvailable( 
    abseil-cpp array-hash hopscotch-map ordered-map 
    robin-map sparse-map ordered-patch-map libcuckoo ankerl )

# Just compile a few files from Folly (HACK)

###############################
# Header-only packages
###############################

FetchContent_Populate( emhash )
add_library( emhash INTERFACE IMPORTED GLOBAL)
target_include_directories( emhash INTERFACE ${emhash_SOURCE_DIR} )

FetchContent_Populate( sparsepp )
add_library( spp_sparsemap INTERFACE IMPORTED GLOBAL)
target_include_directories( spp_sparsemap INTERFACE ${sparsepp_SOURCE_DIR} )

FetchContent_Populate( emilib )
add_library( emilib INTERFACE IMPORTED GLOBAL )
target_include_directories( emilib INTERFACE ${emilib_SOURCE_DIR} )

FetchContent_Populate( skarupke )
add_library( skarupke INTERFACE IMPORTED GLOBAL )
target_include_directories( skarupke INTERFACE ${skarupke_SOURCE_DIR} )

FetchContent_Populate( klibs )
add_library( klibs INTERFACE IMPORTED GLOBAL )
target_include_directories( klibs INTERFACE ${klibs_SOURCE_DIR} )

###############################
# Manually compiled packages
###############################

FetchContent_Populate( folly )
if ( NOT EXISTS ${folly_SOURCE_DIR}/folly/folly-config.h ) 
    file( WRITE ${folly_SOURCE_DIR}/folly/folly-config.h "" )
endif()
add_library( folly STATIC
    ${folly_SOURCE_DIR}/folly/container/detail/F14Table.cpp 
    ${folly_SOURCE_DIR}/folly/lang/SafeAssert.cpp 
    ${folly_SOURCE_DIR}/folly/lang/ToAscii.cpp )
target_include_directories( folly PUBLIC ${folly_SOURCE_DIR})

FetchContent_Populate( bplus-tree )
file( GLOB BPLUS_SOURCES ${bplus-tree_SOURCE_DIR}/src/*.c )
add_library( libbplus_tree_objects STATIC ${BPLUS_SOURCES} )
target_include_directories( libbplus_tree_objects PUBLIC ${bplus-tree_SOURCE_DIR}/include )
target_link_libraries( libbplus_tree_objects PUBLIC PkgConfig::glib )
target_compile_options( libbplus_tree_objects PUBLIC 
    -DBPLUS_TREE_ORDER=32 -DBNPPP_MEMORY_USE_GLIB 
	-DG_DISABLE_CHECKS -DG_DISABLE_ASSERT -D_NDEBUG )

add_library( libbplus_tree INTERFACE IMPORTED GLOBAL )
target_include_directories( libbplus_tree INTERFACE ${bplus-tree_SOURCE_DIR}/include )
target_link_libraries( libbplus_tree INTERFACE libbplus_tree_objects )

ExternalProject_Add( google-sparsehash
    GIT_REPOSITORY https://github.com/sparsehash/sparsehash.git
    PREFIX _deps
    UPDATE_COMMAND ""
    CONFIGURE_COMMAND <SOURCE_DIR>/configure --prefix <SOURCE_DIR>/install
    #BUILD_COMMAND "make -j"
    #INSTALL_COMMAND "make install"
    BUILD_IN_SOURCE 1
)
ExternalProject_Get_Property( google-sparsehash source_dir)
add_library( google_sparsehash INTERFACE IMPORTED GLOBAL )
add_dependencies( google_sparsehash google-sparsehash )
file( MAKE_DIRECTORY ${source_dir}/install/include ) # HACK
target_include_directories( google_sparsehash INTERFACE ${source_dir}/install/include )

#############################################################################
# Our binaries
#############################################################################

add_library( perfcounter STATIC src/PerfGroup.cpp )
target_link_libraries( perfcounter PRIVATE libpfm )
target_compile_definitions( perfcounter PUBLIC INT_KEY_TYPE=int64_t INT_VALUE_TYPE=int64_t )

add_executable( testPerfGroup src/testPerfGroup.cpp )
target_link_libraries( testPerfGroup perfcounter )

add_executable( std_map src/std_map )
target_link_libraries( std_map perfcounter )

add_executable( std_unordered_map src/std_unordered_map )
target_link_libraries( std_unordered_map perfcounter )

add_executable( folly_f14_fast_map src/folly_f14_fast_map.cc )
target_link_libraries( folly_f14_fast_map perfcounter folly )

add_executable( folly_f14_node_map src/folly_f14_node_map.cc )
target_link_libraries( folly_f14_node_map perfcounter folly )

add_executable( folly_f14_value_map src/folly_f14_value_map.cc )
target_link_libraries( folly_f14_value_map perfcounter folly )

add_executable( folly_f14_vector_map src/folly_f14_vector_map.cc )
target_link_libraries( folly_f14_vector_map perfcounter folly )

# abseil has a target with the same name so we added the exec_ prefix
add_executable( exec_absl_btree_map src/absl_btree_map.cc )
target_link_libraries( exec_absl_btree_map absl::btree perfcounter )
set_target_properties( exec_absl_btree_map PROPERTIES OUTPUT_NAME absl_btree_map )

add_executable( exec_absl_node_hash_map src/absl_node_hash_map.cc )
target_link_libraries( exec_absl_node_hash_map absl::node_hash_map perfcounter )
set_target_properties( exec_absl_node_hash_map PROPERTIES OUTPUT_NAME absl_node_hash_map )

add_executable( exec_absl_flat_hash_map src/absl_node_hash_map.cc )
target_link_libraries( exec_absl_flat_hash_map absl::node_hash_map perfcounter )
set_target_properties( exec_absl_flat_hash_map PROPERTIES OUTPUT_NAME absl_flat_hash_map )

add_executable( boost_flat_map src/boost_flat_map.cc )
target_link_libraries( boost_flat_map perfcounter Boost::container )

add_executable( boost_unordered_map src/boost_unordered_map.cc )
target_link_libraries( boost_unordered_map perfcounter Boost::container )

add_executable( google_sparse_hash_map src/google_sparse_hash_map.cc )
target_link_libraries( google_sparse_hash_map perfcounter google_sparsehash )

add_executable( google_dense_hash_map src/google_dense_hash_map.cc )
target_link_libraries( google_dense_hash_map perfcounter google_sparsehash )
target_compile_definitions( google_dense_hash_map PRIVATE INT_HASH_TYPE=std::hash<int64_t> STR_HASH_TYPE=std::hash<std::string> )

add_executable( google_dense_hash_map_mlf_0_9 src/google_dense_hash_map_mlf_0_9.cc )
target_link_libraries( google_dense_hash_map_mlf_0_9 perfcounter google_sparsehash )

add_executable( spp_sparse_hash_map src/spp_sparse_hash_map.cc )
target_link_libraries( spp_sparse_hash_map perfcounter spp_sparsemap )

add_executable( emilib_hash_map src/emilib_hash_map.cc )
target_link_libraries( emilib_hash_map perfcounter emilib )

add_executable( ska_flat_hash_map src/ska_flat_hash_map.cc )
target_link_libraries( ska_flat_hash_map perfcounter skarupke )

add_executable( ska_flat_hash_map_power_of_two src/ska_flat_hash_map_power_of_two.cc )
target_link_libraries( ska_flat_hash_map_power_of_two perfcounter skarupke )

add_executable( ska_bytell_hash_map src/ska_bytell_hash_map.cc )
target_link_libraries( ska_bytell_hash_map perfcounter skarupke )

add_executable( tsl_sparse_map src/tsl_sparse_map.cc )
target_link_libraries( tsl_sparse_map perfcounter tsl::sparse_map )

add_executable( tsl_hopscotch_map src/tsl_hopscotch_map.cc )
target_link_libraries( tsl_hopscotch_map perfcounter tsl::hopscotch_map )

add_executable( tsl_hopscotch_map_mlf_0_5 src/tsl_hopscotch_map_mlf_0_5.cc )
target_link_libraries( tsl_hopscotch_map_mlf_0_5 perfcounter tsl::hopscotch_map )

add_executable( tsl_hopscotch_map_store_hash src/tsl_hopscotch_map_store_hash.cc )
target_link_libraries( tsl_hopscotch_map_store_hash perfcounter tsl::hopscotch_map )

add_executable( tsl_robin_map src/tsl_robin_map.cc )
target_link_libraries( tsl_robin_map perfcounter tsl::robin_map )

add_executable( tsl_robin_map_mlf_0_9 src/tsl_robin_map_mlf_0_9.cc )
target_link_libraries( tsl_robin_map_mlf_0_9 perfcounter tsl::robin_map )

add_executable( tsl_robin_map_store_hash src/tsl_robin_map_store_hash.cc )
target_link_libraries( tsl_robin_map_store_hash perfcounter tsl::robin_map )

add_executable( tsl_robin_pg_map src/tsl_robin_pg_map.cc )
target_link_libraries( tsl_robin_pg_map perfcounter tsl::robin_map )

add_executable( tsl_ordered_map src/tsl_ordered_map.cc )
target_link_libraries( tsl_ordered_map perfcounter tsl::ordered_map )

add_executable( tsl_array_map src/tsl_array_map.cc )
target_link_libraries( tsl_array_map perfcounter tsl::array_hash )

add_executable( tsl_array_map_mlf_1_0 src/tsl_array_map_mlf_1_0.cc )
target_link_libraries( tsl_array_map_mlf_1_0 perfcounter tsl::array_hash )

add_executable( judyL src/judyL.cc )
target_link_libraries( judyL perfcounter Judy )

add_executable( judyHS src/judyHS.cc )
target_link_libraries( judyHS perfcounter Judy )

add_executable( exec_leveldb src/leveldb.cc )
target_link_libraries( exec_leveldb perfcounter leveldb  Boost::filesystem)
set_target_properties( exec_leveldb PROPERTIES OUTPUT_NAME leveldb )

add_executable( exec_rocksdb src/rocksdb.cc )
target_link_libraries( exec_rocksdb perfcounter rocksdb Boost::filesystem)
set_target_properties( exec_rocksdb PROPERTIES OUTPUT_NAME rocksdb )

add_executable( khash src/khash.cc )
target_link_libraries( khash perfcounter klibs )

add_executable( qt_qhash src/qt_qhash.cc )
target_link_libraries( qt_qhash perfcounter Qt5::Core )

add_executable( glib_tree src/glib_tree.cc )
target_link_libraries( glib_tree perfcounter PkgConfig::glib )
target_compile_options( glib_tree PRIVATE -DG_DISABLE_CHECKS -DG_DISABLE_ASSERT )

add_executable( glib_hash_table src/glib_hash_table.cc )
target_link_libraries( glib_hash_table perfcounter PkgConfig::glib )
target_compile_options( glib_hash_table PRIVATE -DG_DISABLE_CHECKS -DG_DISABLE_ASSERT )

add_executable( kyotocabinet_stash src/kyotocabinet_stash.cc )
target_link_libraries( kyotocabinet_stash perfcounter PkgConfig::kyotocabinet )

add_executable( kyotocabinet_hash src/kyotocabinet_hash.cc )
target_link_libraries( kyotocabinet_hash perfcounter PkgConfig::kyotocabinet )

add_executable( cuckoohash_map src/cuckoohash_map.cc )
target_link_libraries( cuckoohash_map perfcounter libcuckoo )

add_executable( python3_dict src/python3_dict.cc )
target_link_libraries( python3_dict perfcounter Python3::Python )

add_executable( bplus_tree src/bplus_tree.cc )
target_link_libraries( bplus_tree perfcounter libbplus_tree PkgConfig::glib )

add_executable( ankerl_unordered_dense_map src/ankerl_unordered_dense_map.cc )
target_link_libraries( ankerl_unordered_dense_map perfcounter unordered_dense::unordered_dense)

add_executable( emhash7 src/emhash7.cc )
target_link_libraries( emhash7 perfcounter emhash )

add_executable( emhash8 src/emhash8.cc )
target_link_libraries( emhash8 perfcounter emhash )

# # nata88
# # nataF8
