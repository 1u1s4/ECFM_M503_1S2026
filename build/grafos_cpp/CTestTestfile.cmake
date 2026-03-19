# CMake generated Testfile for 
# Source directory: /Users/luisalvarado/Documents/GitHub/ECFM_M503_1S2026/grafos_cpp
# Build directory: /Users/luisalvarado/Documents/GitHub/ECFM_M503_1S2026/build/grafos_cpp
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test([=[graph_core_tests]=] "/Users/luisalvarado/Documents/GitHub/ECFM_M503_1S2026/build/grafos_cpp/graph_core_tests")
set_tests_properties([=[graph_core_tests]=] PROPERTIES  _BACKTRACE_TRIPLES "/Users/luisalvarado/Documents/GitHub/ECFM_M503_1S2026/grafos_cpp/CMakeLists.txt;64;add_test;/Users/luisalvarado/Documents/GitHub/ECFM_M503_1S2026/grafos_cpp/CMakeLists.txt;0;")
add_test([=[ui_smoke_tests]=] "/Users/luisalvarado/Documents/GitHub/ECFM_M503_1S2026/build/grafos_cpp/ui_smoke_tests")
set_tests_properties([=[ui_smoke_tests]=] PROPERTIES  ENVIRONMENT "QT_QPA_PLATFORM=offscreen" _BACKTRACE_TRIPLES "/Users/luisalvarado/Documents/GitHub/ECFM_M503_1S2026/grafos_cpp/CMakeLists.txt;72;add_test;/Users/luisalvarado/Documents/GitHub/ECFM_M503_1S2026/grafos_cpp/CMakeLists.txt;0;")
