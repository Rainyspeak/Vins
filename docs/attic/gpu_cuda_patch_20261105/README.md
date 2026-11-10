# GPU(CUDA 光流)补丁归档,2026-11-05

用户确认不需要 GPU 版本后,从工作区移除的 CUDA 光流补丁快照。
三个文件是移除前的工作区状态(GPU 补丁 + 当日 CPU 前端改动),从未进过 git。
若哪天要在带 CUDA OpenCV 的机器上恢复,把三个文件拷回对应路径即可:
- CMakeLists.txt                    -> src/VINS-Fusion/vins_estimator/
- feature_tracker.cpp / .h          -> src/VINS-Fusion/vins_estimator/src/featureTracker/
注意:恢复后 config 的 use_gpu/use_gpu_acc_flow 开关与 parameters 里被一并移除的
USE_GPU/USE_GPU_ACC_FLOW 读取也要一并恢复(见归档文件内代码)。
