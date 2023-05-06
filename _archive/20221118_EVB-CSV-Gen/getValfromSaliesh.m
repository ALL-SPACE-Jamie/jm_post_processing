% Spit out G vs phase

S12_re=4.0
S12_im=1.2
mag = 20*log10((S12_re^2+S12_im^2)^(0.5))

test_data = (results.testData)
measured_data = test_data.measured_data

phase_bits = [measured_data.fe_phase_code]
atten_bits = [measured_data.fe_atten_code]

vna_data = [measured_data.vna_data]

S12_re_log = []
S12_im_log = []

for a = 1:1:length(vna_data)
    S12_re_array = [vna_data(a).CH1_S12_2_real]  
    S12_re = S12_re_array(41)*1.0
    S12_re_log(1,a) = S12_re

    S12_im_array = [vna_data(a).CH1_S12_2_imag]  
    S12_im = S12_im_array(41)*1.0
    S12_im_log(1,a) = S12_im
end

mag_log = 20*log10((S12_re_log.*S12_re_log+S12_im_log.*S12_im_log).^(0.5))
phase_log = atan(S12_im_log./S12_re_log)

x = phase_bits
y = atten_bits
z = mag_log
z2 = phase_log
scatter3(x,y,z)

arrayOut = transpose(cat(1,x,y,z,z2))

csvwrite('myFile.csv',arrayOut)
