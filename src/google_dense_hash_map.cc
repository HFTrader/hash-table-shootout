#include <inttypes.h>
#include <string>
#include <google/dense_hash_map>

typedef google::dense_hash_map<int64_t, int64_t, INT_HASH_TYPE> hash_t;
typedef google::dense_hash_map<std::string, int64_t, STR_HASH_TYPE> str_hash_t;

#include "hash_map_int_base.h"
#include "hash_map_str_base.h"

#undef SETUP_INT
#define SETUP_INT           \
    hash_t hash;            \
    hash.set_empty_key(-1); \
    hash.set_deleted_key(-2);

#undef RESERVE_INT
#define RESERVE_INT(size) hash.resize(size)

#undef SETUP_STR
#define SETUP_STR               \
    str_hash_t str_hash;        \
    str_hash.set_empty_key(""); \
    str_hash.set_deleted_key("d");

#undef RESERVE_STR
#define RESERVE_STR(size) str_hash.resize(size)

#include "template.cc"
