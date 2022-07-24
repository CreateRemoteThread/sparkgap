set strategy="lowpass"
set lowpass=(6000000,125000000,1)
run
set strategy="sad"
set corr_cutoff=0.8
set sad_cutoff=100
set window_offset=25327
set window_length=334
set window_slide=100
set clkadjust=0
set clkadjust_max=0
set ref=0
run

