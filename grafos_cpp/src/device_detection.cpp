#include "grafos_cpp/device_detection.hpp"

#include <array>
#include <cctype>
#include <cstdio>
#include <memory>
#include <string>

namespace grafos {

namespace {

std::string run_probe(const char* command) {
    std::array<char, 256> buffer{};
#if defined(_WIN32)
    std::unique_ptr<FILE, decltype(&_pclose)> pipe(_popen(command, "r"), _pclose);
#else
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command, "r"), pclose);
#endif
    if (!pipe) {
        return {};
    }

    std::string output;
    while (fgets(buffer.data(), static_cast<int>(buffer.size()), pipe.get()) != nullptr) {
        output += buffer.data();
    }

    while (!output.empty() && (output.back() == '\n' || output.back() == '\r')) {
        output.pop_back();
    }
    return output;
}

}  // namespace

DeviceInfo detect_compute_device() {
#if defined(__APPLE__) && (defined(__aarch64__) || defined(__arm64__))
    return DeviceInfo{
        "Apple Silicon",
        "GPU detectada por plataforma; la simulación actual corre en CPU.",
        true,
    };
#elif defined(__linux__)
    const auto nvidia_name = run_probe("nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null");
    if (!nvidia_name.empty()) {
        const auto first_break = nvidia_name.find('\n');
        return DeviceInfo{
            "NVIDIA",
            (first_break == std::string::npos ? nvidia_name : nvidia_name.substr(0, first_break))
                + " detectada; la simulación actual corre en CPU.",
            true,
        };
    }

    const auto lspci_output = run_probe("lspci 2>/dev/null");
    const auto lowered = [&]() {
        auto copy = lspci_output;
        for (auto& ch : copy) {
            ch = static_cast<char>(std::tolower(static_cast<unsigned char>(ch)));
        }
        return copy;
    }();
    if (lowered.find("amd") != std::string::npos || lowered.find("radeon") != std::string::npos) {
        return DeviceInfo{
            "AMD",
            "GPU AMD detectada; la simulación actual corre en CPU.",
            true,
        };
    }
    if (lowered.find("nvidia") != std::string::npos) {
        return DeviceInfo{
            "NVIDIA",
            "GPU NVIDIA detectada; la simulación actual corre en CPU.",
            true,
        };
    }
#elif defined(_WIN32)
    const auto wmic_output = run_probe("wmic path win32_VideoController get name");
    auto lowered = wmic_output;
    for (auto& ch : lowered) {
        ch = static_cast<char>(std::tolower(static_cast<unsigned char>(ch)));
    }
    if (lowered.find("nvidia") != std::string::npos) {
        return DeviceInfo{
            "NVIDIA",
            "GPU NVIDIA detectada; la simulación actual corre en CPU.",
            true,
        };
    }
    if (lowered.find("amd") != std::string::npos || lowered.find("radeon") != std::string::npos) {
        return DeviceInfo{
            "AMD",
            "GPU AMD detectada; la simulación actual corre en CPU.",
            true,
        };
    }
#endif

    return DeviceInfo{
        "CPU only",
        "No se detectó una GPU compatible o no fue posible sondearla.",
        false,
    };
}

}  // namespace grafos
