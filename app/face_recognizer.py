from insightface.app import FaceAnalysis

# CUDAExecutionProvider = GPU
# CPUExecutionProvider = CPU

face_app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider'])  # or CUDA
face_app.prepare(ctx_id=0, det_size=(320, 320))

