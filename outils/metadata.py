from pymediainfo import MediaInfo


# Permet de récupérer des informations sur un fichier vidéo.
class MetaData:
    # Nom du fichier qu'on analyse.
    filename = None

    # Métadonnées récupérées du fichier.
    media_info = None

    def __init__(self, filename):
        self.filename = filename
        self.media_info = MediaInfo.parse(self.filename)

    # Indique le timecode de début du fichier.
    def start(self) -> str:
        extension = self.media_info.general_tracks[0].to_data()['file_extension']

        # Timecode en cas de MP4 :
        if extension == 'mp4':
            try:
                return self.media_info.tracks[0].to_data()['tim']
            # Le tim n'existe pas, donc pas de TC disponible.
            except KeyError:
                return '00:00:00:00'

        # Timecode en cas de WAV :
        if extension == 'wav':
            return self.media_info.tracks[1].to_data()['other_delay'][3]

        # Timecode en cas de MOV :
        if extension == 'mov':
            return self.media_info.other_tracks[0].time_code_of_first_frame

    # Retourne le framerate du fichier vidéo.
    def framerate(self) -> int:
        return int(float(self.media_info.general_tracks[0].to_data()['frame_rate']))

    # Retourne la résolution du fichier vidéo au format 'hauteurxlargeur'.
    def resolution(self) -> str:
        return self.media_info.video_tracks[0].to_data()['sampled_width'] + 'x' + self.media_info.video_tracks[0].to_data()['sampled_height']

    # Durée du fichier en timecode SMTP.
    def duree_to_tc(self) -> str:
        return self.media_info.general_tracks[0].to_data()['other_duration'][4]

    # Durée du fichier en nombre d'image.
    def duree_to_image(self) -> int:
        return int(self.media_info.general_tracks[0].to_data()['duration'])
