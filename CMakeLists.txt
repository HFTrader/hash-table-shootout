cmake_minimum_required( VERSION 3.12 )
project( hash-map-shootout )

set( CMAKE_CXX_STANDARD 17 )

include( FetchContent )
FetchContent_Declare( array-hash GIT_REPOSITORY https://github.com/Tessil/array-hash.git )
FetchContent_Declare( emilib     GIT_REPOSITORY https://github.com/emilk/emilib.git )
FetchContent_Declare( flat_hash_map GIT_REPOSITORY https://github.com/skarupke/flat_hash_map.git )
FetchContent_Declare( hopscotch-map GIT_REPOSITORY https://github.com/Tessil/hopscotch-map.git )
FetchContent_Declare( ordered-map GIT_REPOSITORY https://github.com/Tessil/ordered-map.git )
FetchContent_Declare( robin-map GIT_REPOSITORY https://github.com/Tessil/robin-map.git )
FetchContent_Declare( sparse-map GIT_REPOSITORY https://github.com/Tessil/sparse-map.git )
FetchContent_Declare( sparsepp GIT_REPOSITORY https://github.com/greg7mdp/sparsepp.git )
FetchContent_Declare( ordered-patch-map GIT_REPOSITORY https://github.com/1ykos/ordered_patch_map )
FetchContent_Declare( libcuckoo GIT_REPOSITORY https://github.com/efficient/libcuckoo.git )
FetchContent_Declare( bplus-tree GIT_REPOSITORY https://github.com/berenm/bplus-tree.git GIT_TAG version/2.0.0 )
FetchContent_Declare( klibs GIT_REPOSITORY https://github.com/attractivechaos/klib.git )
FetchContent_Declare( abseil-cpp GIT_REPOSITORY  https://github.com/abseil/abseil-cpp.git )
FetchContent_Declare( folly GIT_REPOSITORY https://github.com/facebook/folly.git GIT_TAG main )

FetchContent_MakeAvailable(abseil-cpp folly )



# $(BUILD_DIR)/% : src/%.cc ${OBJS_${notdir $@}} src/template.cc src/PerfCounter.cpp abseil.done
# 	$(CXX) $(CXXFLAGS) ${CXXFLAGS_${notdir $@}} -o $@ $< src/PerfCounter.cpp ${OBJS_${notdir $@}} ${LDFLAGS} ${LDFLAGS_${notdir $@}}
add_library( perfcounter STATIC src/PerfCounter.cpp )

add_executable( exec_absl_btree_map src/absl_btree_map.cc )
target_link_libraries( exec_absl_btree_map absl::btree perfcounter )
set_target_properties( exec_absl_btree_map PROPERTIES OUTPUT_NAME absl_btree_map )

add_executable( exec_absl_node_hash_map src/absl_node_hash_map.cc )
target_link_libraries( exec_absl_node_hash_map absl::node_hash_map perfcounter )
set_target_properties( exec_absl_node_hash_map PROPERTIES OUTPUT_NAME absl_node_hash_map )

add_executable( exec_absl_flat_hash_map src/absl_node_hash_map.cc )
target_link_libraries( exec_absl_flat_hash_map absl::node_hash_map perfcounter )
set_target_properties( exec_absl_flat_hash_map PROPERTIES OUTPUT_NAME absl_flat_hash_map )

add_executable( folly_f14_fast_map src/folly_f14_fast_map.cc )
target_link_libraries( folly_f14_fast_map )

# folly_f14_fast_map
# folly_f14_node_map
# folly_f14_value_map
# folly_f14_vector_map
# python3_dict
# std_unordered_map
# std_map
# boost_flat_map
# boost_unordered_map
# google_sparse_hash_map
# google_dense_hash_map
# google_dense_hash_map_mlf_0_9
# qt_qhash
# spp_sparse_hash_map
# emilib_hash_map
# ska_flat_hash_map
# ska_flat_hash_map_power_of_two
# ska_bytell_hash_map
# tsl_sparse_map
# tsl_hopscotch_map
# tsl_hopscotch_map_mlf_0_5
# tsl_hopscotch_map_store_hash
# tsl_robin_map
# tsl_robin_map_mlf_0_9
# tsl_robin_map_store_hash
# tsl_robin_pg_map
# #tsl_ordered_map
# tsl_array_map
# tsl_array_map_mlf_1_0
# judyL
# judyHS
# #bplus_tree
# cuckoohash_map
# glib_tree
# glib_hash_table
# kyotocabinet_stash
# kyotocabinet_hash
# leveldb
# rocksdb
# khash
# # nata88
# # nataF8
