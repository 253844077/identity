class Config:
    is_gpu=False
    rec_model_dir = "./inference/ch_ppocr_server_v2.0_rec_infer"
    det_mode_dir = "./inference/ch_ppocr_server_v2.0_det_infer"
    secret = None
    port = 8800