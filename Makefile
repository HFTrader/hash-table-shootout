##################################################
# User-settable variables

CXX      ?= clang++
CXXFLAGS ?= -O3 -march=native -std=c++14 -DNDEBUG

# LDFLAGS_MALLOC ?=
# LDFLAGS_MALLOC ?= -ljemalloc # much better that glibc's malloc on some workloads
LDFLAGS_MALLOC ?= -ltcmalloc_minimal # often even better than jemalloc

BUILD_DIR      ?= ./build
OBJ_DIR        ?= ./obj

PYTHON3_PC     ?= python3-embed # pkg-config ID for python3 development files

ifndef APPS
cmd := grep -v \\\# apps.txt
APPS = ${shell ${cmd}}
endif # APPS

LDFLAGS ?= -lm
LDFLAGS += ${LDFLAGS_MALLOC}

ifeq ($(filter glib_tree,${APPS}), glib_tree)
CXXFLAGS_glib_tree ?= $(shell pkg-config --cflags glib-2.0) \
	-DG_DISABLE_CHECKS -DG_DISABLE_ASSERT
LDFLAGS_glib_tree ?= $(shell pkg-config --libs glib-2.0)
endif
ifeq ($(filter glib_hash_table,${APPS}), glib_hash_table)
CXXFLAGS_glib_hash_table ?= $(shell pkg-config --cflags glib-2.0) \
	-DG_DISABLE_CHECKS -DG_DISABLE_ASSERT
LDFLAGS_glib_hash_table ?= $(shell pkg-config --libs glib-2.0)
endif
ifeq ($(filter qt_qhash,${APPS}), qt_qhash)
CXXFLAGS_qt_qhash ?= $(shell pkg-config --cflags Qt5Core) -fPIC
LDFLAGS_qt_qhash ?= $(shell pkg-config --libs Qt5Core)
endif
CXXFLAGS_spp_sparse_hash_map            ?= -Isparsepp
CXXFLAGS_emilib_hash_map                ?= -Iemilib
CXXFLAGS_ska_flat_hash_map              ?= -Iflat_hash_map
CXXFLAGS_ska_flat_hash_map_power_of_two ?= ${CXXFLAGS_ska_flat_hash_map}
CXXFLAGS_ska_bytell_hash_map            ?= ${CXXFLAGS_ska_flat_hash_map}
CXXFLAGS_tsl_hopscotch_map              ?= -Ihopscotch-map
CXXFLAGS_tsl_hopscotch_map_mlf_0_5      ?= ${CXXFLAGS_tsl_hopscotch_map}
CXXFLAGS_tsl_hopscotch_map_store_hash   ?= ${CXXFLAGS_tsl_hopscotch_map}
CXXFLAGS_tsl_robin_map                  ?= -Irobin-map/include
CXXFLAGS_tsl_robin_map_mlf_0_9          ?= ${CXXFLAGS_tsl_robin_map}
CXXFLAGS_tsl_robin_map_store_hash       ?= ${CXXFLAGS_tsl_robin_map}
CXXFLAGS_tsl_robin_pg_map               ?= ${CXXFLAGS_tsl_robin_map}
CXXFLAGS_tsl_sparse_map                 ?= -Isparse-map/include
CXXFLAGS_tsl_ordered_map                ?= -Iordered-map/include
CXXFLAGS_tsl_array_map                  ?= -Iarray-hash/include -std=c++17
CXXFLAGS_tsl_array_map_mlf_1_0          ?= ${CXXFLAGS_tsl_array_map}
CXXFLAGS_judyL                          ?=
CXXFLAGS_judyHS                         ?=
CXXFLAGS_nata88                         ?=
CXXFLAGS_nataF8                         ?= ${CXXFLAGS_nata88}
CXXFLAGS_cuckoohash_map                 ?= -Ilibcuckoo -pthread
CXXFLAGS_leveldb                        ?=
CXXFLAGS_rocksdb                        ?=
CXXFLAGS_khash                          ?= -Iklibs
ifeq ($(filter bplus_tree,${APPS}), bplus_tree)
CFLAGS_bplus_tree                       ?= \
	-DBPLUS_TREE_ORDER=32 -DBNPPP_MEMORY_USE_GLIB \
	-DG_DISABLE_CHECKS -DG_DISABLE_ASSERT -D_NDEBUG \
	-Ibplus-tree/include $(shell pkg-config --cflags glib-2.0)
CXXFLAGS_bplus_tree                     ?= ${CFLAGS_bplus_tree}
LDFLAGS_bplus_tree                      ?= \
	$(shell pkg-config --libs glib-2.0)
OBJS_bplus_tree = ${OBJ_DIR}/bplus_foreach.o ${OBJ_DIR}/bplus_insert.o \
   ${OBJ_DIR}/bplus_iterator.o ${OBJ_DIR}/bplus_leaf.o ${OBJ_DIR}/bplus_node.o \
   ${OBJ_DIR}/bplus_rebalance.o ${OBJ_DIR}/bplus_remove.o \
   ${OBJ_DIR}/bplus_search.o ${OBJ_DIR}/bplus_tree.o
${OBJ_DIR}/%.o: bplus-tree/src/%.c
	${CC} -std=c99 ${CFLAGS} ${CFLAGS_bplus_tree} -c -o $@ $<
endif
#ifeq ($(filter absl,${APPS}), absl)
abseil.done:
	mkdir -p build/abseil-cpp && cd build/abseil-cpp && pwd && \
    cmake -DCMAKE_INSTALL_PREFIX=.. -DBUILD_SHARED_LIBS=OFF -DCMAKE_CXX_STANDARD=14 ../../abseil-cpp && \
    cmake --build . --target all && \
    cmake --build . --target install
	touch abseil.done folly/folly/folly-config.h
CXXFLAGS_absl_flat_hash_map ?= -Ibuild/include
LDFLAGS_absl_flat_hash_map  ?= -Lbuild/lib -labsl_flags_reflection -labsl_raw_hash_set -labsl_hash -labsl_city -labsl_low_level_hash
CXXFLAGS_absl_btree_map ?= -Ibuild/include
LDFLAGS_absl_btree_map  ?= -Lbuild/lib -labsl_flags_reflection -labsl_raw_hash_set -labsl_hash  -labsl_city -labsl_low_level_hash
CXXFLAGS_absl_node_hash_map ?= -Ibuild/include
LDFLAGS_absl_node_hash_map  ?= -Lbuild/lib -labsl_flags_reflection -labsl_raw_hash_set -labsl_hash  -labsl_city -labsl_low_level_hash
CXXFLAGS_folly_f14_fast_map ?= -Ifolly
LDFLAGS_folly_f14_fast_map  ?= -Lbuild/lib folly/folly/container/detail/F14Table.cpp folly/folly/lang/SafeAssert.cpp folly/folly/lang/ToAscii.cpp
CXXFLAGS_folly_f14_node_map ?= -Ifolly
LDFLAGS_folly_f14_node_map  ?= -Lbuild/lib folly/folly/container/detail/F14Table.cpp folly/folly/lang/SafeAssert.cpp folly/folly/lang/ToAscii.cpp
CXXFLAGS_folly_f14_value_map ?= -Ifolly
LDFLAGS_folly_f14_value_map  ?= -Lbuild/lib folly/folly/container/detail/F14Table.cpp folly/folly/lang/SafeAssert.cpp folly/folly/lang/ToAscii.cpp
CXXFLAGS_folly_f14_vector_map ?= -Ifolly
LDFLAGS_folly_f14_vector_map  ?= -Lbuild/lib folly/folly/container/detail/F14Table.cpp folly/folly/lang/SafeAssert.cpp folly/folly/lang/ToAscii.cpp
#endif

LDFLAGS_judyL                           ?= -lJudy
LDFLAGS_judyHS                          ?= ${LDFLAGS_judyL}
LDFLAGS_nata88                          ?= -lnata
LDFLAGS_nataF8                          ?= ${LDFLAGS_nata88}
LDFLAGS_cuckoohash_map                  ?= -pthread
ifeq ($(filter kyotocabinet_stash,${APPS}), kyotocabinet_stash)
CXXFLAGS_kyotocabinet_stash ?= $(shell pkg-config --cflags kyotocabinet)
LDFLAGS_kyotocabinet_stash  ?= $(shell pkg-config --libs kyotocabinet)
endif
ifeq ($(filter kyotocabinet_hash,${APPS}), kyotocabinet_hash)
CXXFLAGS_kyotocabinet_hash ?= $(shell pkg-config --cflags kyotocabinet)
LDFLAGS_kyotocabinet_hash  ?= $(shell pkg-config --libs kyotocabinet)
endif
ifeq ($(filter python3_dict,${APPS}), python3_dict)
CXXFLAGS_python3_dict ?= $(shell pkg-config --cflags ${PYTHON3_PC})
LDFLAGS_python3_dict  ?= $(shell pkg-config --libs ${PYTHON3_PC})
endif
LDFLAGS_leveldb                         ?= -lleveldb -lboost_filesystem
LDFLAGS_rocksdb                         ?= -lrocksdb -lboost_filesystem
LDFLAGS_khash                           ?=

##################################################

.DEFAULT_GOAL := all

EXECUTABLES = $(APPS:%=$(BUILD_DIR)/%)

all: $(BUILD_DIR) $(OBJ_DIR) $(EXECUTABLES) abseil.done

$(OBJ_DIR) $(BUILD_DIR): abseil.done
	mkdir -p $@

clean:
	rm -rf $(BUILD_DIR) $(OBJ_DIR) abseil.done

$(BUILD_DIR)/% : src/%.cc ${OBJS_${notdir $@}} src/template.cc src/PerfCounter.cpp abseil.done
	$(CXX) $(CXXFLAGS) ${CXXFLAGS_${notdir $@}} -o $@ $< src/PerfCounter.cpp ${OBJS_${notdir $@}} ${LDFLAGS} ${LDFLAGS_${notdir $@}}
