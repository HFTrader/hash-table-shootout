#include "PerfGroup.h"
#include <perfmon/pfmlib_perf_event.h>
#include <iostream>
#include <cstring>
#include <algorithm>

// https://sources.debian.org/src/libpfm4/4.11.1+git32-gd0b85fb-1/perf_examples/self_count.c/
// https://stackoverflow.com/questions/42088515/perf-event-open-how-to-monitoring-multiple-events
// https://github.com/wcohen/libpfm4/blob/6864dad7cf85fac9fff04bd814026e2fbc160175/perf_examples/self.c

PerfGroup::PerfGroup()
{
}

PerfGroup::~PerfGroup()
{
    close();
}

void PerfGroup::close()
{
    for (Descriptor &d : _ids)
    {
        ::close(d.fd);
    }
    _ids.clear();
}

static bool translate(const char *events[], perf_event_attr_t *evds, size_t size)
{
    // std::cerr << "Translate: " << size << " items" << std::endl;
    for (size_t j = 0; j < size; ++j)
    {
        perf_event_attr_t &attr(evds[j]);
        memset(&attr, 0, sizeof(attr));
        char *fstr = nullptr;
        pfm_perf_encode_arg_t arg;
        memset(&arg, 0, sizeof(arg));
        arg.attr = &attr;
        arg.fstr = &fstr;
        int ret = pfm_get_os_event_encoding(events[j], PFM_PLM0 | PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &arg);
        if (ret != PFM_SUCCESS)
        {
            std::cerr << "PerfGroup: could not translate event [" << events[j] << "] " << pfm_strerror(ret) << std::endl;
            return false;
        }
        // std::cerr << "Event:" << events[j] << " name: [" << fstr << "] type:" << attr.type << " size:" << attr.size << " config:" << attr.config << std::endl;
        ::free(fstr);
    }
    return true;
}

static bool init(std::vector<perf_event_attr_t> &evds, std::vector<PerfGroup::Descriptor> &ids, std::vector<int> &leaders)
{
    pid_t pid = getpid();
    int cpu = -1;
    int leader = -1;
    int flags = 0;
    int counter = 0;
    leaders.clear();
    for (size_t j = 0; j < evds.size(); ++j)
    {
        perf_event_attr_t &pea(evds[j]);
        unsigned type = pea.type;
        long long config = pea.config;
        memset(&pea, 0, sizeof(pea));
        pea.type = type;
        pea.config = config;
        pea.size = sizeof(perf_event_attr_t);
        pea.disabled = 1;
        pea.exclude_kernel = 1;
        pea.exclude_hv = 1;
        pea.read_format = PERF_FORMAT_GROUP | PERF_FORMAT_ID;

        int fd = perf_event_open(&pea, pid, cpu, leader, flags);
        if (fd < 0)
        {
            int err = errno;
            std::cerr << "PerfGroup::init  Index:" << j << " errno:" << err << " " << strerror(err) << std::endl;
            return false;
        }
        if (leader < 0)
        {
            leader = fd;
            leaders.push_back(fd);
        }
        uint64_t id = 0;
        int result = ioctl(fd, PERF_EVENT_IOC_ID, &id);
        if (result < 0)
        {
            int err = errno;
            std::cerr << "PerfGroup::init ioctl(PERF_EVENT_IOC_ID) Index:" << j << " errno:" << err << " " << strerror(err) << std::endl;
            return false;
        }
        if ((pea.type == PERF_TYPE_HARDWARE) || (pea.type == PERF_TYPE_HW_CACHE))
        {
            if (++counter >= 3)
            {
                counter = 0;
                leader = -1;
            }
        }

        ids[j].fd = fd;
        ids[j].id = id;
        ids[j].order = j;
    }
    return true;
}

bool PerfGroup::init(const std::vector<std::string> &events)
{
    std::vector<perf_event_attr_t> evds(events.size());
    memset(&evds[0], 0, sizeof(perf_event_attr_t) * evds.size());
    std::vector<const char *> names(events.size());
    for (size_t j = 0; j < events.size(); ++j)
    {
        names[j] = events[j].c_str();
    }
    if (!translate(names.data(), evds.data(), events.size()))
        return false;
    _ids.resize(events.size());
    if (!::init(evds, _ids, _leaders))
        return false;
    std::sort(_ids.begin(), _ids.end(), [](const Descriptor &lhs, const Descriptor &rhs)
              { return lhs.id < rhs.id; });
    _order.resize(_ids.size());
    for (size_t j = 0; j < _ids.size(); ++j)
    {
        _order[_ids[j].order] = j;
        _names[_ids[j].name] = j;
    }
    return true;
}

bool PerfGroup::start()
{
    if (_ids.empty())
    {
        std::cerr << "Group is empty!" << std::endl;
        return false;
    }
    for (int lead : _leaders)
    {
        int res = ioctl(lead, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
        if (res < 0)
        {
            int err = errno;
            std::cerr << "PerfGroup::start ioctl(PERF_EVENT_IOC_RESET) errno:" << err << " " << strerror(err) << std::endl;
            return false;
        }
    }
    for (int lead : _leaders)
    {
        int res = ioctl(lead, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
        if (res < 0)
        {
            int err = errno;
            std::cerr << "PerfGroup::init ioctl(PERF_EVENT_IOC_ENABLE) errno:" << err << " " << strerror(err) << std::endl;
            return false;
        }
    }
    return true;
}

bool PerfGroup::stop()
{
    if (_ids.empty())
    {
        std::cerr << "Group is empty!" << std::endl;
        return false;
    }
    for (int lead : _leaders)
    {

        int res = ioctl(lead, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
        if (res < 0)
        {
            int err = errno;
            std::cerr << "PerfGroup::init ioctl(PERF_EVENT_IOC_DISABLE) errno:" << err << " " << strerror(err) << std::endl;
            return false;
        }
    }
    read();
    return true;
}

size_t PerfGroup::size() const
{
    return _ids.size();
}

uint64_t PerfGroup::operator[](size_t index) const { return _ids[index].value; }

uint64_t PerfGroup::operator[](const char *name) const
{
    auto it = _names.find(name);
    if (it == _names.end())
        return std::numeric_limits<uint64_t>::max();
    return _ids[it->second].value;
}

std::string PerfGroup::name(size_t index) const { return _ids[index].name; }

void PerfGroup::read()
{
    size_t n = _ids.size();
    if (n == 0)
        return;
    struct MessageValue
    {
        uint64_t value;
        uint64_t id;
    };
    struct Message
    {
        uint64_t nr;
        MessageValue values[];
    };
    for (Descriptor &d : _ids)
        d.value = std::numeric_limits<uint64_t>::max();
    size_t bufsize = 2 * (sizeof(Message) + n * sizeof(MessageValue));
    std::vector<uint8_t> buf(bufsize);
    for (int lead : _leaders)
    {
        ssize_t nb = ::read(lead, buf.data(), bufsize);
        Message *msg = (Message *)buf.data();
        for (uint64_t i = 0; i < msg->nr; i++)
        {
            uint64_t id = msg->values[i].id;
            uint64_t value = msg->values[i].value;
            // std::cerr << "Read lead:" << lead << " index " << id << "/" << msg->nr << " value " << value << std::endl;
            auto it = std::lower_bound(_ids.begin(), _ids.end(), id, [](const Descriptor &d, size_t id)
                                       { return d.id < id; });
            if (it != _ids.end())
            {
                if (id == it->id)
                {
                    it->value = value;
                }
            }
            else
            {
                std::cerr << "Not found id " << id << std::endl;
            }
        }
    }
}

bool PerfGroup::initialize()
{
    int ret = pfm_initialize();
    if (ret != PFM_SUCCESS)
    {
        fprintf(stderr, "Cannot initialize library: %s", pfm_strerror(ret));
        return false;
    }
    return true;
}