from pymediainfo import MediaInfo

filename = '/Volumes/ROZO-DELIVERIES/01_WIP/02_PICTURE/LES_INTRANQUILLES/02_TV_GRADE/01_FTR_SHRT_SERIE/LesIntranquilles_177_3840x2160_24_PRORES444_SEQ_210730.mov'

media_info = MediaInfo.parse(filename)

# Utile :
print(media_info.video_tracks[0].to_data()['sampled_width'] + 'x' + media_info.video_tracks[0].to_data()['sampled_height'])
print(type(media_info.general_tracks[0].to_data()['frame_rate']))
print(str(int(float(media_info.general_tracks[0].to_data()['frame_rate']))))

# extension = media_info.general_tracks[0].to_data()['file_extension']

# Check master image et rustine : Pro Res 422 HQ ou Pro Res 444, HD ou UHD
codec = 'PR444'
resolution = 'HD'
dynamique = 'SDR'  # Ou 'HDR 10' = 'HDR DV'
framerate = '25'
bite_rate_mode = 'CBR'
scan = 'P'

# Valeurs attendues :
file_extension = 'mov'

if codec == 'PR444':
    codecs_video = 'ProRes'

print(media_info.to_data())

print(media_info.general_tracks[0].to_data()['codecs_video']) #
print(media_info.general_tracks[0].to_data()['file_extension'])
print(media_info.general_tracks[0].to_data()['frame_rate'])
#print(media_info.general_tracks[0].to_data()['overall_bit_rate_mode'])
print(media_info.video_tracks[0].to_data()['format_profile'])
print(media_info.video_tracks[0].to_data()['codec_id'])
print(media_info.video_tracks[0].to_data()['sampled_height'])
print(media_info.video_tracks[0].to_data()['sampled_width'])



print(media_info.video_tracks[0].to_data()['pixel_aspect_ratio'])
print(media_info.video_tracks[0].to_data()['chroma_subsampling'])
print(media_info.video_tracks[0].to_data()['color_space'])
print(media_info.video_tracks[0].to_data()['scan_type'])
# Si analyse la durée :
#print(media_info.general_tracks[0].to_data()['duration'])
print(media_info.general_tracks[0].to_data()['other_duration'][4])
#print(media_info.other_tracks[0].to_data()['duration'])
print(media_info.video_tracks[0].to_data()['color_primaries'])
print(media_info.video_tracks[0].to_data()['matrix_coefficients'])

