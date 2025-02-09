#include <inttypes.h>
#include <string>
#include <memory>
#include "absl/container/btree_map.h"

typedef absl::btree_map<INT_KEY_TYPE, INT_VALUE_TYPE> hash_t;
typedef absl::btree_map<std::string, INT_VALUE_TYPE> str_hash_t;

#include "hash_map_int_base.h"
#include "hash_map_str_base.h"

#undef RESERVE_INT
#define RESERVE_INT(size)

#undef RESERVE_STR
#define RESERVE_STR(size)

#undef LOAD_FACTOR_INT_HASH
#define LOAD_FACTOR_INT_HASH(hash) 0.0f

#undef LOAD_FACTOR_STR_HASH
#define LOAD_FACTOR_STR_HASH(hash) 0.0f

#include "template.cc"
