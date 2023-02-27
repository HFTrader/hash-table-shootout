#include <inttypes.h>
#include <string>
#include <tsl/hopscotch_map.h>

typedef tsl::hopscotch_map<int64_t, int64_t, std::hash<int64_t>,
                           std::equal_to<int64_t>, std::allocator<std::pair<int64_t, int64_t>>,
                           30, true>
    hash_t;
typedef tsl::hopscotch_map<std::string, int64_t, std::hash<std::string>,
                           std::equal_to<std::string>, std::allocator<std::pair<std::string, int64_t>>,
                           30, true>
    str_hash_t;

#include "hash_map_int_base.h"
#include "hash_map_str_base.h"

#include "template.cc"
