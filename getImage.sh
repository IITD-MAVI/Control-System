gst-launch v4l2src device=/dev/video2 num-buffers=1 ! jpegenc ! filesink location=image.jpg
